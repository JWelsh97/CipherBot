from tornado import gen
import tormysql


pool = None


def connect(config):
    global pool
    pool = tormysql.ConnectionPool(**config)


def disconnect():
    pool.close()


@property
def connected():
    return pool.closed()


@gen.coroutine
def execute(sql, args=None):
    with (yield pool.Connection()) as conn:
        with conn.cursor() as cursor:
            if args:
                yield cursor.execute(sql, args)
            else:
                yield cursor.execute(sql)
            data = cursor.fetchall()
    raise gen.Return(data)
