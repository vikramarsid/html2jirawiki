

[![Build Status](https://travis-ci.org/vikramarsid/html2jirawiki.svg?branch=master)](https://travis-ci.org/vikramarsid/html2jirawiki)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/2755acb84ec94bc1a992987e06a1c019)](https://www.codacy.com/app/vikram-arsid/html2jirawiki?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=vikramarsid/html2jirawiki&amp;utm_campaign=Badge_Grade)

Installation
============

``pip install html2jirawiki``


Usage
=====

Convert some HTML to Markdown:
```
    from html2jirawiki import html_to_jira_wiki
    html_to_jira_wiki('<b>Yay</b> <a href="http://github.com">GitHub</a>')  # > '**Yay** [GitHub](http://github.com)'
```
Specify tags to exclude (blacklist):

```

    from html2jirawiki import html_to_jira_wiki
    html_to_jira_wiki('<b>Yay</b> <a href="http://github.com">GitHub</a>', strip=['a'])  # > '*Yay* GitHub'

```

or specify the tags you want to include (whitelist):

```

    from html2jirawiki import html_to_jira_wiki
    html_to_jira_wiki('<b>Yay</b> <a href="http://github.com">GitHub</a>', convert=['b'])  # > '*Yay* GitHub'
```

Options
=======

html2jirawiki supports the following options:

strip
  A list of tags to strip (blacklist). This option can't be used with the
  ``convert`` option.

convert
  A list of tags to convert (whitelist). This option can't be used with the
  ``strip`` option.

autolinks
  A boolean indicating whether the "automatic link" style should be used when
  a ``a`` tag's contents match its href. Defaults to ``True``

heading_style
  Defines how headings should be converted. Accepted values are ``ATX``,
  ``ATX_CLOSED``, ``SETEXT``, and ``UNDERLINED`` (which is an alias for
  ``SETEXT``). Defaults to ``UNDERLINED``.

bullets
  An iterable (string, list, or tuple) of bullet styles to be used. If the
  iterable only contains one item, it will be used regardless of how deeply
  lists are nested. Otherwise, the bullet will alternate based on nesting
  level. Defaults to ``'*+-'``.

Options may be specified as kwargs to the ``html2jirawiki`` function, or as a
nested ``Options`` class in ``MarkdownConverter`` subclasses.