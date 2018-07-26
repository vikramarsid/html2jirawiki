# coding=utf-8
import logging
import re
import unittest

from html2jirawiki import html_to_jira_wiki, ATX, ATX_CLOSED

logging.basicConfig(format="* %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

nested_uls = re.sub('\s+', '', """
    <ul>
        <li>1
            <ul>
                <li>a
                    <ul>
                        <li>I</li>
                        <li>II</li>
                        <li>III</li>
                    </ul>
                </li>
                <li>b</li>
                <li>c</li>
            </ul>
        </li>
        <li>2</li>
        <li>3</li>
    </ul>""")


class CommandTest(unittest.TestCase):

    def test_nested(self):
        text = html_to_jira_wiki('<p>This is an <a href="http://example.com/">example link</a>.</p>')
        self.assertTrue(text == 'This is an [example link](http://example.com/).\n\n')

    def test_strip(self):
        text = html_to_jira_wiki('<a href="https://github.com/matthewwithanm">Some Text</a>', strip=['a'])
        self.assertTrue(text == 'Some Text')

    def test_do_not_strip(self):
        text = html_to_jira_wiki('<a href="https://github.com/matthewwithanm">Some Text</a>', strip=[])
        self.assertTrue(text == '[Some Text](https://github.com/matthewwithanm)')

    def test_convert(self):
        text = html_to_jira_wiki('<a href="https://github.com/matthewwithanm">Some Text</a>', convert=['a'])
        self.assertTrue(text == '[Some Text](https://github.com/matthewwithanm)')

    def test_do_not_convert(self):
        text = html_to_jira_wiki('<a href="https://github.com/matthewwithanm">Some Text</a>', convert=[])

        self.assertTrue(text == 'Some Text')

    def test_single_tag(self):
        self.assertTrue(html_to_jira_wiki('<span>Hello</span>') == 'Hello')

    def test_soup(self):
        self.assertTrue(html_to_jira_wiki('<div><span>Hello</div></span>') == 'Hello')

    def test_whitespace(self):
        self.assertTrue(html_to_jira_wiki(' a  b \n\n c ') == ' a b c ')

    def test_a(self):
        self.assertTrue(html_to_jira_wiki('<a href="http://google.com">Google</a>') == '[Google](http://google.com)')

    def test_a_with_title(self):
        text = html_to_jira_wiki('<a href="http://google.com" title="The &quot;Goog&quot;">Google</a>')
        self.assertTrue(text == r'[Google](http://google.com "The \"Goog\"")')

    def test_a_shortcut(self):
        text = html_to_jira_wiki('<a href="http://google.com">http://google.com</a>')
        self.assertTrue(text == '<http://google.com>')

    def test_a_no_autolinks(self):
        text = html_to_jira_wiki('<a href="http://google.com">http://google.com</a>', autolinks=False)
        self.assertTrue(text == '[http://google.com](http://google.com)')

    def test_b(self):
        self.assertTrue(html_to_jira_wiki('<b>Hello</b>') == '*Hello*')

    def test_blockquote(self):
        self.assertTrue(html_to_jira_wiki('<blockquote>Hello</blockquote>').strip() == '> Hello')

    def test_nested_blockquote(self):
        text = html_to_jira_wiki('<blockquote>And she was like <blockquote>Hello</blockquote></blockquote>').strip()
        self.assertTrue(text == '> And she was like \n> > Hello')

    def test_br(self):
        self.assertTrue(html_to_jira_wiki('a<br />b<br />c') == 'a  \nb  \nc')

    def test_em(self):
        self.assertTrue(html_to_jira_wiki('<em>Hello</em>') == '_Hello_')

    def test_h1(self):
        self.assertTrue(html_to_jira_wiki('<h1>Hello</h1>') == 'h1. Hello\n')

    def test_h2(self):
        self.assertTrue(html_to_jira_wiki('<h2>Hello</h2>') == 'h2. Hello\n')

    def test_hn(self):
        self.assertTrue(html_to_jira_wiki('<h3>Hello</h3>') == 'h3. Hello\n')
        self.assertTrue(html_to_jira_wiki('<h6>Hello</h6>') == 'h6. Hello\n')

    def test_atx_headings(self):
        self.assertTrue(html_to_jira_wiki('<h1>Hello</h1>', heading_style=ATX) == 'h6. Hello\n')
        self.assertTrue(html_to_jira_wiki('<h2>Hello</h2>', heading_style=ATX) == 'h6. Hello\n')

    def test_atx_closed_headings(self):
        self.assertTrue(html_to_jira_wiki('<h1>Hello</h1>', heading_style=ATX_CLOSED) == 'h6. Hello\n')
        self.assertTrue(html_to_jira_wiki('<h2>Hello</h2>', heading_style=ATX_CLOSED) == 'h6. Hello\n')

    def test_i(self):
        self.assertTrue(html_to_jira_wiki('<i>Hello</i>') == '_Hello_')

    def test_ol(self):
        self.assertTrue(html_to_jira_wiki('<ol><li>a</li><li>b</li></ol>') == '1. a\n2. b\n')

    def test_p(self):
        self.assertTrue(html_to_jira_wiki('<p>hello</p>') == 'hello\n\n')

    def test_strong(self):
        self.assertTrue(html_to_jira_wiki('<strong>Hello</strong>') == '*Hello*')

    def test_ul(self):
        self.assertTrue(html_to_jira_wiki('<ul><li>a</li><li>b</li></ul>') == '* a\n* b\n')

    def test_nested_uls(self):
        """
        Nested ULs should alternate bullet characters.

        """
        self.assertTrue(
            html_to_jira_wiki(nested_uls)
            ==
            '* 1\n\t+ a\n\t\t- I\n\t\t- II\n\t\t- III\n\t\t\n\t+ b\n\t+ c\n\t\n* 2\n* 3\n'
        )

    def test_bullets(self):
        self.assertTrue(
            html_to_jira_wiki(nested_uls, bullets='-')
            ==
            '- 1\n\t- a\n\t\t- I\n\t\t- II\n\t\t- III\n\t\t\n\t- b\n\t- c\n\t\n- 2\n- 3\n'
        )

    def test_img(self):
        self.assertTrue(html_to_jira_wiki(
            '<img src="/path/to/img.jpg" alt="Alt text" title="Optional title" />') == '![Alt text](/path/to/img.jpg '
                                                                                       '"Optional title")')
        self.assertTrue(html_to_jira_wiki('<img src="/path/to/img.jpg" alt="Alt text" />') == '![Alt text]('
                                                                                              '/path/to/img.jpg)')

    def test_underscore(self):
        self.assertTrue(html_to_jira_wiki('_hey_dude_') == '\_hey\_dude\_')

    def test_xml_entities(self):
        self.assertTrue(html_to_jira_wiki('&amp;') == '&')

    def test_named_entities(self):
        self.assertTrue(html_to_jira_wiki('&raquo;') == u'\xbb')

    def test_hexadecimal_entities(self):
        # This looks to be a bug in BeautifulSoup (fixed in bs4) that we have to work around.
        self.assertTrue(html_to_jira_wiki('&#x27;') == '\x27')

    def test_single_escaping_entities(self):
        self.assertTrue(html_to_jira_wiki('&amp;amp;') == '&amp;')


def suite():
    """ Generate the Test Suite which sets up all the Unit Test Cases in the proper order."""
    suite_list = [unittest.TestLoader().loadTestsFromTestCase(CommandTest)]
    fullSuite = unittest.TestSuite(suite_list)
    return fullSuite


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
