from tornado import gen
import tormysql


pool = tormysql.ConnectionPool(
    autocommit=True,
    max_connections=20,
    idle_seconds=7200,
    host='',
    user='',
    passwd='',
    db='',
    port=3306
)


@gen.coroutine
def fetch(sql, args=None):
    with (yield pool.Connection()) as conn:
        with conn.cursor() as cursor:
            if args:
                yield cursor.execute(sql, args)
            else:
                yield cursor.execute(sql)
            data = cursor.fetchall()
    raise gen.Return(data)
