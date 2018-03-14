from __future__ import unicode_literals

import codecs
import json
import shutil
from tempfile import NamedTemporaryFile

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from six import PY2
from tinydb import TinyDB

DB_TABLENAME = 'links'
DB_FILE = NamedTemporaryFile(delete=False)
TABLE = TinyDB(DB_FILE.name, ensure_ascii=PY2).table(DB_TABLENAME)
linkpatcher_plugin_globals = None


class LinkPatcherGlobals:
    def __init__(self, page=None, site_navigation=None):
        self.page = page
        self.nav = site_navigation


class LinkPatcherPlugin(BasePlugin):
    TABLE.purge()
    config_scheme = (
        ('delete_dbfile', config_options.Type(bool, default=True)),
        ('dbfile_path',
         config_options.Type(type("string"), default="linkpatcher_db.json")),
    )

    def on_config(self, config):
        config['markdown_extensions'].append(
            'linkpatcher.extension:LinkPatcherExtension')
        return config

    def on_page_markdown(self, _, page, config, site_navigation):
        global linkpatcher_plugin_globals
        linkpatcher_plugin_globals = LinkPatcherGlobals(page, site_navigation)

    def on_post_build(self, config):
        plugin_config = config['plugins']['linkpatcher-plugin'].config
        if not plugin_config.get('delete_dbfile'):
            dbpath = plugin_config.get('dbfile_path')
            if not PY2:
                shutil.copy(DB_FILE.name, dbpath)
            else:
                encoded = json.loads(
                    DB_FILE.read(), object_hook=self.unicodize)
                json.dump(
                    encoded,
                    codecs.open(dbpath, 'w', 'utf-8'),
                    ensure_ascii=False)

    def unicodize(self, data):
        if isinstance(data, dict):
            return dict(
                map(self.ascii_encode_dict, pair) for pair in data.items())
        return unicode(data)
