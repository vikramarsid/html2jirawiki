# coding=utf-8
"""
**Module**: html2jirawiki
       :platform: Linux
       :synopsis: Python module to convert HTML to JIRA wiki format
"""
import re

import six
from bs4 import BeautifulSoup
from bs4.element import NavigableString

# regexes
CONVERT_HEADING_RE = re.compile(r'convert_h(\d+)')
LINE_BEGINNING_RE = re.compile(r'^', re.MULTILINE)
WHITESPACE_RE = re.compile(r'[\r\n\s\t ]+')
FRAGMENT_ID = '__MARKDOWNIFY_WRAPPER__'
WRAPPED_DIV = '<div id="%s">%%s</div>' % FRAGMENT_ID

# Heading styles
ATX = 'atx'
ATX_CLOSED = 'atx_closed'
UNDERLINED = 'underlined'
SETEXT = UNDERLINED


def escape(text):
    if not text:
        return ''
    return text.replace('_', r'\_')


def _to_dict(obj):
    return dict((k, getattr(obj, k)) for k in dir(obj) if not k.startswith('_'))


class MarkdownConverter(object):
    class DefaultOptions(object):
        strip = None
        convert = None
        autolinks = True
        heading_style = UNDERLINED
        bullets = '*+-'  # An iterable of bullet types.

    class Options(DefaultOptions):
        pass

    def __init__(self, **options):
        # Create an options dictionary. Use DefaultOptions as a base so that
        # it doesn't have to be extended.
        self.options = _to_dict(self.DefaultOptions)
        self.options.update(_to_dict(self.Options))
        self.options.update(options)
        if self.options['strip'] is not None and self.options['convert'] is not None:
            raise ValueError('You may specify either tags to strip or tags to'
                             ' convert, but not both.')

    def convert(self, html):
        # We want to take advantage of the html5 parsing, but we don't actually
        # want a full document. Therefore, we'll mark our fragment with an id,
        # create the document, and extract the element with the id.
        html = WRAPPED_DIV % html
        soup = BeautifulSoup(html, 'html.parser')
        return self.process_tag(soup.find(id=FRAGMENT_ID), children_only=True)

    def process_tag(self, node, children_only=False):
        text = ''

        # Convert the children first
        for el in node.children:
            if isinstance(el, NavigableString):
                text += self.process_text(six.text_type(el))
            else:
                text += self.process_tag(el)

        if not children_only:
            convert_fn = getattr(self, 'convert_%s' % node.name, None)
            if convert_fn and self.should_convert_tag(node.name):
                text = convert_fn(node, text)

        return text

    @staticmethod
    def process_text(text):
        return escape(WHITESPACE_RE.sub(' ', text or ''))

    def __getattr__(self, attr):
        # Handle headings
        m = CONVERT_HEADING_RE.match(attr)
        if m:
            n = int(m.group(1))

            def convert_tag(el, text):
                return self.convert_hn(n, el, text)

            convert_tag.__name__ = 'convert_h%s' % n
            setattr(self, convert_tag.__name__, convert_tag)
            return convert_tag

        raise AttributeError(attr)

    def should_convert_tag(self, tag):
        tag = tag.lower()
        strip = self.options['strip']
        convert = self.options['convert']
        if strip is not None:
            return tag not in strip
        elif convert is not None:
            return tag in convert
        else:
            return True

    @staticmethod
    def indent(text, level):
        return LINE_BEGINNING_RE.sub('\t' * level, text) if text else ''

    # Updated to return <h> tags with proper formatting; removed extra /n from return
    @staticmethod
    def underline(text, pad_char):
        text = (text or '').rstrip()
        return '%s%s\n' % (pad_char, text) if text else ''

    def convert_a(self, el, text):
        href = el.get('href')
        title = el.get('title')
        if self.options['autolinks'] and text == href and not title:
            # Shortcut syntax
            return '<%s>' % href
        title_part = ' "%s"' % title.replace('"', r'\"') if title else ''
        return '[%s](%s%s)' % (text or '', href, title_part) if href else text or ''

    # Command updated to handle h1-h6 returning updated markdown format instead of pound sign
    def convert_hn(self, n, el, text):
        style = self.options['heading_style']
        text = text.rstrip()
        if style == UNDERLINED and n <= 6:
            line = 'h{}. '.format(n)
            return self.underline(text, line)
        else:
            line = 'h6. '
            return self.underline(text, line)

    # Updated to handle <i></i> to **%s**
    @staticmethod
    def convert_strong(el, text):
        return '*%s*' % text if text else ''

    @staticmethod
    def convert_b(el, text):
        return '*%s*' % text if text else ''

    @staticmethod
    def convert_em(el, text):
        return '_%s_' % text if text else ''

    # Updated to handle <i></i> to _%s_
    @staticmethod
    def convert_i(el, text):
        return '_%s_' % text if text else ''

    # Updated to handle <u></u> to +%s+
    @staticmethod
    def convert_u(el, text):
        return '+%s+' % text if text else ''

    # Updated to handle <del></del> to -%s-
    @staticmethod
    def convert_del(el, text):
        return '-%s-' % text if text else ''

    # Added to handle <sup></sup> to ^%s^
    @staticmethod
    def convert_sup(el, text):
        return '^%s^' % text if text else ''

    # Updated to handle <sub></sub> to ~%s~
    @staticmethod
    def convert_sub(el, text):
        return '~%s~' % text if text else ''

    # Added to handle <sub></sub> to ??%s??
    @staticmethod
    def convert_cite(el, text):
        return '??%s??' % text if text else ''

    @staticmethod
    def convert_blockquote(el, text):
        return '\n' + LINE_BEGINNING_RE.sub('> ', text) if text else ''

    @staticmethod
    def convert_br(el, text):
        return '  \n'

    @staticmethod
    def convert_p(el, text):
        return '%s\n\n' % text if text else ''

    def convert_list(self, el, text):
        nested = False
        while el:
            if el.name == 'li':
                nested = True
                break
            el = el.parent
        if nested:
            text = '\n' + self.indent(text, 1)
        return text

    convert_ul = convert_list
    convert_ol = convert_list

    def convert_li(self, el, text):
        parent = el.parent
        if parent is not None and parent.name == 'ol':
            bullet = '%s.' % (parent.index(el) + 1)
        else:
            depth = -1
            while el:
                if el.name == 'ul':
                    depth += 1
                el = el.parent
            bullets = self.options['bullets']
            bullet = bullets[depth % len(bullets)]
        return '%s %s\n' % (bullet, text or '')

    @staticmethod
    def convert_img(el, text):
        alt = el.attrs.get('alt', None) or ''
        src = el.attrs.get('src', None) or ''
        title = el.attrs.get('title', None) or ''
        title_part = ' "%s"' % title.replace('"', r'\"') if title else ''
        return '![%s](%s%s)' % (alt, src, title_part)


def html_to_jira_wiki(html_string, **options):
    return MarkdownConverter(**options).convert(html_string)
