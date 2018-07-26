# coding=utf-8
import sys

if sys.version_info > (3, 0):
    from html2jirawiki.html2jirawiki import html_to_jira_wiki, ATX, ATX_CLOSED
else:
    from html2jirawiki import html_to_jira_wiki, ATX, ATX_CLOSED
