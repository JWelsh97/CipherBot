from tornado.ioloop import IOLoop
from tornado import gen
import yaml
import tormysql


class Database(object):
    def __init__(self):
        with open('config.yaml', 'r') as f:
            conf = yaml.load(f)['db']
            conf['passwd'] = conf.pop('password')
        self.pool = tormysql.ConnectionPool(
            max_connections=20,
            idle_seconds=7200,
            host='127.0.0.1',
            user='gazelle_bot',
            passwd='@cYw%Rln%%NnT1jwU^',
            db='gazelle',
            port=3396
        )
        self.pool.connect()

    @gen.coroutine
    def execute(self, sql):
        print('Executing')
        with (yield self.pool.Connection()) as conn:
            print('Connection Pool')
            with conn.cursor() as cursor:
                print('Getting cursor')
                yield cursor.execute(sql)
                data = cursor.fetchall()
        print(type(data))
        print(data.result())


def t():
    test = Database()
    test.execute('SELECT Username FROM gazelle.users_main')


ioloop = IOLoop.instance()
ioloop.run_sync(t)
# ioloop.run_sync(Database.execute)

