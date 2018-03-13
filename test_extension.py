# coding: utf-8
from __future__ import unicode_literals

import re
import unittest
from os import remove

import markdown
from markdown.util import etree
from mkdocs import config, nav

import linkpatcher.plugin as plugin
from linkpatcher.extension import (LinkPatcherTreeProcessor,
                                   LinkPathcerInlineProcessor)

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote


class LinkPatcherExtensionTestBase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.tree_processor = LinkPatcherTreeProcessor()
        self.conf = config.Config(schema=config.DEFAULT_SCHEMA)
        self.conf.load_dict({
            "pages": [{
                'Home': 'index.md'
            }, {
                'testpage': 'nest/nest.md'
            }]
        })
        self.site_navigation = nav.SiteNavigation(self.conf)
        self.site_navigation.file_context.set_current_path('nest/nest.md')


class TestMakeAnchor(LinkPatcherExtensionTestBase):
    def setUp(self):
        super(TestMakeAnchor, self).setUp()
        self.tree_processor.db_value_map = {
            "text1": "/test1.html",
            "text2": "/test2.html",
            "text3": "/test3.html"
        }
        self.tree_processor.db_keys_re = re.compile("|".join(
            self.tree_processor.db_value_map.keys()))

    def dotest(self, current_url, link_to, text):
        self.site_navigation.url_context.set_current_url(current_url)
        self.tree_processor = LinkPatcherTreeProcessor()
        self.tree_processor.db_value_map = {}
        self.tree_processor.db_value_map[text] = link_to
        plugin.linkpatcher_plugin_globals = plugin.LinkPatcherGlobals(
            page={}, site_navigation=self.site_navigation)
        return self.tree_processor.make_anchor(text)

    def test_make_anchor(self):
        test_patterns = [{
            "expectation":
            """<a class="linkpatcher_link" href="../../index.html#linkpatcher_test">test</a>""",
            "params": {
                "current_url": "/nest/nest/index.html",
                "link_to": '/index.html#linkpatcher_test',
                "text": "test"
            }
        }, {
            "expectation":
            """<a class="linkpatcher_link" href="./index.html#linkpatcher_test">あいうえお</a>""",
            "params": {
                "current_url": "/index.html",
                "link_to": '/index.html#linkpatcher_test',
                "text": "あいうえお"
            }
        }]
        for pattern in test_patterns:
            test_result = self.dotest(**pattern["params"])
            try:
                self.assertEqual(
                    etree.tostring(test_result, encoding='unicode'),
                    pattern['expectation'])
            except LookupError:
                self.assertEqual(
                    etree.tostring(test_result, encoding='utf-8'),
                    pattern['expectation'].encode('utf-8'))


class TestNewElemFromText(LinkPatcherExtensionTestBase):
    def setUp(self):
        super(TestNewElemFromText, self).setUp()
        self.tree_processor.db_value_map = {
            "text1": "/test1.html",
            "text2": "/test2.html",
            "text3": "/test3.html"
        }
        self.tree_processor.db_keys_re = re.compile("|".join(
            self.tree_processor.db_value_map.keys()))

    def dotest(self, text):
        plugin.linkpatcher_plugin_globals = plugin.LinkPatcherGlobals(
            page={}, site_navigation=self.site_navigation)
        return self.tree_processor.newelem_from_text(text)

    def test_newelem_from_text(self):
        text_patterns = [{
            "param": "",
            "expectation": ["", []]
        }, {
            "param": "abcabc  acd",
            "expectation": ["abcabc  acd", []]
        }, {
            "param":
            "abcabc text1 acd text2 text3",
            "expectation": [
                "abcabc ", [
                    """<a class="linkpatcher_link" href="./test1.html">text1</a> acd """,
                    """<a class="linkpatcher_link" href="./test2.html">text2</a> """,
                    """<a class="linkpatcher_link" href="./test3.html">text3</a>"""
                ]
            ]
        }]
        for pattern in text_patterns:
            text, elems = self.dotest(pattern["param"])
            expectation = pattern["expectation"]
            self.assertEqual(text, expectation[0])
            self.assertEqual(
                list(map(lambda e: etree.tostring(e).decode(), elems)),
                expectation[1])


class TestInsertPatchedLink(LinkPatcherExtensionTestBase):
    def setUp(self):
        super(TestInsertPatchedLink, self).setUp()
        self.tree_processor.db_value_map = {
            "text1": "/test1.html",
            "text2": "/test2.html",
            "text3": "/test3.html"
        }
        self.tree_processor.db_keys_re = re.compile("|".join(
            self.tree_processor.db_value_map.keys()))
        self.site_navigation.url_context.set_current_url("/index.html")
        plugin.linkpatcher_plugin_globals = plugin.LinkPatcherGlobals(
            page={}, site_navigation=self.site_navigation)

    def test_insert_patchedlink(self):
        elemstr = """<p id="0">
            <p id="1">
                text1 0123
                text2 4567
                text3 8901
                <a id="2">text2</a>
                text3 9999
            </p>
        text1 abcd
        text2 efgh
        text3 hijk
        </p>"""
        expectation = """<p id="0">
            <p id="1">
                <a class="linkpatcher_link" href="./test1.html">text1</a> 0123
                <a class="linkpatcher_link" href="./test2.html">text2</a> 4567
                <a class="linkpatcher_link" href="./test3.html">text3</a> 8901
                <a id="2">text2</a>
                <a class="linkpatcher_link" href="./test3.html">text3</a> 9999
            </p>
        <a class="linkpatcher_link" href="./test1.html">text1</a> abcd
        <a class="linkpatcher_link" href="./test2.html">text2</a> efgh
        <a class="linkpatcher_link" href="./test3.html">text3</a> hijk
        </p>"""
        elem = etree.fromstring(elemstr)
        self.tree_processor.insert_patchedlink(elem)
        self.assertEqual(etree.tostring(elem).decode(), expectation)


class TestRun(LinkPatcherExtensionTestBase):
    def setUp(self):
        super(TestRun, self).setUp()
        self.site_navigation.url_context.set_current_url("/index.html")
        plugin.linkpatcher_plugin_globals = plugin.LinkPatcherGlobals(
            page={}, site_navigation=self.site_navigation)

        plugin.TABLE.insert_multiple([{
            "text": "text1",
            "link": "/test1.html"
        }, {
            "text": "text2",
            "link": "/test2.html"
        }, {
            "text": "text3",
            "link": "/test3.html"
        }])

    def test_run(self):
        elemstr = """<p>
        <p>text1 text2text2
text2
        text3.</p>
        </p>"""
        expectation = """<p>
        <p><a class="linkpatcher_link" href="./test1.html">text1</a> text2text2
<a class="linkpatcher_link" href="./test2.html">text2</a>
        <a class="linkpatcher_link" href="./test3.html">text3</a>.</p>
        </p>"""
        elem = etree.fromstring(elemstr)
        self.tree_processor.run(elem)
        self.assertEqual(
            etree.tostring(elem, encoding='utf-8').decode(), expectation)

    def tearDown(self):
        remove(plugin.DB_FILE.name)


class LinkPatcherExtensionTest(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['linkpatcher'] = LinkPathcerInlineProcessor(
            LinkPathcerInlineProcessor.pattern)


class TestHandleMatch(LinkPatcherExtensionTestBase):
    def setUp(self):
        super(TestHandleMatch, self).setUp()
        self.inline_processor = LinkPathcerInlineProcessor(
            LinkPathcerInlineProcessor.pattern)
        self.md = markdown.Markdown(extensions=[LinkPatcherExtensionTest()])
        page = nav.Page(
            title='', path='', url_context=nav.URLContext(), config=self.conf)
        plugin.linkpatcher_plugin_globals = plugin.LinkPatcherGlobals(
            page=page, site_navigation=self.site_navigation)

    def test_handleMatch(self):
        test_patterns = [{
            "param": ": あ",
            "expectation": {
                "element": ": あ",
                "db": []
            }
        }, {
            "param": ":: あ",
            "expectation": {
                "element":
                """
<h2 class="linkpatcher" id="linkpatcher_%E3%81%82">あ</h2>
""",
                "db": [{
                    'text': 'あ',
                    'link': '//#linkpatcher_%s' % quote("あ".encode('utf-8'))
                }]
            }
        }, {
            "param": "::: あ",
            "expectation": {
                "element":
                """
<h3 class="linkpatcher" id="linkpatcher_%E3%81%82">あ</h3>
""",
                "db": [{
                    'text': 'あ',
                    'link': '//#linkpatcher_%s' % quote("あ".encode('utf-8'))
                }]
            }
        }, {
            "param": ":::: あ",
            "expectation": {
                "element":
                """
<h4 class="linkpatcher" id="linkpatcher_%E3%81%82">あ</h4>
""",
                "db": [{
                    'text': 'あ',
                    'link': '//#linkpatcher_%s' % quote("あ".encode('utf-8'))
                }]
            }
        }, {
            "param": "::::: あ",
            "expectation": {
                "element":
                """
<h5 class="linkpatcher" id="linkpatcher_%E3%81%82">あ</h5>
""",
                "db": [{
                    'text': 'あ',
                    'link': '//#linkpatcher_%s' % quote("あ".encode('utf-8'))
                }]
            }
        }, {
            "param": ":::::: あ",
            "expectation": {
                "element":
                """
<h6 class="linkpatcher" id="linkpatcher_%E3%81%82">あ</h6>
""",
                "db": [{
                    'text': 'あ',
                    'link': '//#linkpatcher_%s' % quote("あ".encode('utf-8'))
                }]
            }
        }, {
            "param": ":: !あ",
            "expectation": {
                "element":
                """
<h2 class="linkpatcher" id="linkpatcher_%E3%81%82">あ</h2>
""",
                "db": []
            }
        }, {
            "param": ":: あ, い",
            "expectation": {
                "element":
                """
<h2 class="linkpatcher" id="linkpatcher_%E3%81%82">あ</h2>
""",
                "db": [{
                    'text': 'あ',
                    'link': '//#linkpatcher_%s' % quote("あ".encode('utf-8'))
                }, {
                    'text': 'い',
                    'link': '//#linkpatcher_%s' % quote('あ'.encode('utf-8'))
                }]
            },
        }, {
            "param": ":: !あ, い",
            "expectation": {
                "element":
                """
<h2 class="linkpatcher" id="linkpatcher_%E3%81%82">あ</h2>
""",
                "db": [{
                    'text': 'い',
                    'link': '//#linkpatcher_%s' % quote('あ'.encode('utf-8'))
                }]
            },
        }]
        for test_pattern in test_patterns:
            plugin.TABLE.purge()
            result = self.md.convert(test_pattern["param"])
            self.assertEqual(
                result,
                """<p>%s</p>""" % test_pattern["expectation"]['element'])
            self.assertEqual(plugin.TABLE.all(),
                             test_pattern["expectation"]['db'])


if __name__ == '__main__':
    unittest.main()
