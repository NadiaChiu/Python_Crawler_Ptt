import os
import sqlite3

# 發文表
TABLE_POST_COL = ['id', 'board', 'code', 'author', 'title', 'dt', 'content']
CREATE_TABLE_POST = 'CREATE TABLE IF NOT EXISTS pttpost(' \
                    'id INTEGER UNIQUE, ' \
                    'board TEXT,' \
                    'code TEXT UNIQUE,' \
                    'author TEXT,' \
                    'title TEXT,' \
                    'dt TEXT,' \
                    'content TEXT, PRIMARY KEY (id))'
DATA_INSERT_POST = 'INSERT INTO pttpost ({collist}) VALUES({values})'.format(
    collist=','.join(TABLE_POST_COL), values=','.join(['?'] * len(TABLE_POST_COL)))

# 推文表
TABLE_PUSH_COL = ['pttpost_id', 'user', 'ipdt', 'tag', 'content']
CREATE_TABLE_PUSH = 'CREATE TABLE IF NOT EXISTS pttpush(' \
                    'pttpost_id INTEGER,' \
                    'user TEXT,' \
                    'ipdt TEXT,' \
                    'tag TEXT,' \
                    'content TEXT)'
DATA_INSERT_PUSH = 'INSERT INTO pttpush ({collist}) VALUES({values})'.format(
    collist=','.join(TABLE_PUSH_COL), values=','.join(['?'] * len(TABLE_PUSH_COL)))


class Write2Sqlite:
    def __init__(self):
        self._path = os.path.join(os.getcwd(), 'db', 'mydb.db')
        if os.path.exists(self._path):
            os.remove(self._path)
        else:
            os.makedirs(os.path.join(os.getcwd(), 'db'))
        self._conn = sqlite3.connect(self._path)
        self._cursor = self._conn.cursor()
        self._check_table()

    def _check_table(self):
        self._cursor.execute(CREATE_TABLE_POST)
        self._cursor.execute(CREATE_TABLE_PUSH)
        self._commit()

    def _commit(self):
        self._conn.commit()

    def _rollback(self):
        self._conn.rollback()

    @staticmethod
    def _check_data(dict_data, data_type):
        if data_type == 'POST':
            return tuple([dict_data[i] for i in TABLE_POST_COL])
        elif data_type == 'PUSH':
            return [tuple([data[item] for item in TABLE_PUSH_COL]) for data in dict_data]
        else:
            return None

    def execute_data(self, dict_post, l_dict_push):
        try:
            # get post id
            post_id = self._cursor.execute('SELECT MAX(id) FROM pttpost').fetchall()
            post_id = post_id[0][0] + 1 if len(post_id) == 1 and post_id[0][0] is not None else 1

            # insert id info
            dict_post['id'] = post_id
            for item in l_dict_push:
                item['pttpost_id'] = post_id

            # insert data : post
            ins = self._check_data(dict_post, 'POST')
            self._cursor.execute(DATA_INSERT_POST, ins)

            # insert data : push
            ins = self._check_data(l_dict_push, 'PUSH')
            self._cursor.executemany(DATA_INSERT_PUSH, ins)

            self._commit()
        except Exception as e:
            print(e)
            self._rollback()

    def close(self):
        self._cursor.close()
        self._conn.close()
