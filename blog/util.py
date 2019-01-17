# -*- coding: utf-8 -*-
import redis


class redisConnect():
    def __init__(self, host='localhost', port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db

    def __enter__(self):
        pool = redis.ConnectionPool(host=self.host, port=self.port, db=self.db)
        self.r = redis.Redis(connection_pool=pool)
        return self.r

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            print '连接成功'
        else:
            print('Type: ', exc_type)
            print('Value:', exc_val)
            print('TreacBack:', exc_tb)

# with redisConnect() as r:
#     r.set('blog_visit', 0)
#     # r.incr('blog_visit')
#     print r.get('blog_visit')

# r = redis.Redis(host='localhost', port=6379, db=0)
# r.set('blog_visit', 0)
# print r.get()