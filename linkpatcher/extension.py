# coding:utf-8
from __future__ import unicode_literals

import re

import markdown
from markdown.inlinepatterns import Pattern
from markdown.treeprocessors import Treeprocessor
from markdown.util import etree
from mkdocs.relative_path_ext import path_to_url

import linkpatcher.plugin as plugin
from linkpatcher.plugin import TABLE

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote


class LinkPatcherTreeProcessor(Treeprocessor):
    db_value_map, db_keys_re = None, None

    class IndexedNewElem:
        def __init__(self, index, element):
            self.index, self.element = index, element

    def make_anchor(self, text):
        el = etree.Element('a')
        el.text = text
        el.set('class', "linkpatcher_link")
        el.set('href',
               path_to_url(self.db_value_map[text],
                           plugin.linkpatcher_plugin_globals.nav, True))
        return el

    def newelem_from_text(self, text):
        def __generate_elem(elements, match_iter, last_match_endpoint=0):
            match = next(match_iter, None)
            if not match:
                return text[last_match_endpoint:], elements
            start, end = match.span()
            match_word = text[start:end]
            new_element = self.make_anchor(match_word)
            new_element.tail, elements = __generate_elem(
                elements, match_iter, end)
            elements.insert(0, new_element)
            return text[last_match_endpoint:start], elements

        if not text:
            return text, []
        match_iter = self.db_keys_re.finditer(text)
        if not match_iter:
            return text, []
        return __generate_elem([], match_iter)

    def insert_patchedlink(self, element):
        additional_siblings = []
        for i, child in enumerate(element):
            if child.tag == 'p':
                child.text, children = self.newelem_from_text(child.text)
                for new_child in reversed(children):
                    child.insert(0, new_child)
            if child.tail:
                child.tail, siblings = self.newelem_from_text(child.tail)
                additional_siblings.extend(
                    [self.IndexedNewElem(i, sibling) for sibling in siblings])
            self.insert_patchedlink(child)
        for sibling in reversed(additional_siblings):
            element.insert(sibling.index + 1, sibling.element)

    def run(self, element):
        all_values = TABLE.all()
        if not all_values:
            return
        self.db_value_map = {link['text']: link['link'] for link in all_values}
        self.db_keys_re = re.compile(
            r'((?<=^)|(?<=\W))(%s)((?=$)|(?= )|(?=\W))' % '|'.join(
                [re.escape(k) for k in self.db_value_map.keys()]),
            re.MULTILINE)
        self.insert_patchedlink(element)


class LinkPathcerInlineProcessor(Pattern):
    pattern = r'(::+) +(.*)'

    def handleMatch(self, m):
        lines = m.group(3).splitlines()
        header_size = len(m.group(2))
        main_text, rest = lines[0], lines[1:]
        aliases = [alias.strip() for alias in re.split(r',? +', main_text)]

        el = etree.Element('h%s' % header_size)
        el.tail = '\n' + '\n'.join(rest)
        el.text = aliases[0]
        if el.text.startswith('!'):
            el.text = re.sub(r'^!', '', el.text)
            del aliases[0]
        el_id = 'linkpatcher_%s' % quote(el.text.encode('utf-8'))
        el.set('id', el_id)
        el.set('class', 'linkpatcher')

        links = [{
            'text':
            alias,
            'link':
            plugin.linkpatcher_plugin_globals.page.abs_url + '#' + el_id
        } for alias in aliases]
        TABLE.insert_multiple(links)
        return el


class LinkPatcherExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.treeprocessors.insert(-1, 'linkpatcher_treeprocessor',
                                 LinkPatcherTreeProcessor(md))
        md.inlinePatterns['linkpatcher'] = LinkPathcerInlineProcessor(
            LinkPathcerInlineProcessor.pattern)


def makeExtension(configs={}):
    return LinkPatcherExtension(configs=configs)
