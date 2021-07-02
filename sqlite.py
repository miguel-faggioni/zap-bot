#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

DB_FILE = 'aux/videos.db'
TABLE = 'videos'
TABLE_CREATION_SQL = '''
CREATE TABLE IF NOT EXISTS {}
    (
        link              TEXT,
        title             TEXT,
        width             INTEGER,
        height            INTEGER,
        original_width    INTEGER,
        original_height   INTEGER,
        duration          REAL,
        filepath          TEXT,
        compilation       TEXT
    )
'''.format(TABLE)


class Sqlite:
    def __init__(self):
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.row_factory = dict_factory
        self.cur = self.conn.cursor()
        self.cur.execute(TABLE_CREATION_SQL)
        self.conn.commit()

    def cleanUp(self):
        self.conn.close()

    def run(self,query):
        result = self.cur.execute(query)
        self.conn.commit()
        return result

