# -*- coding: utf-8 -*-
import redis
import os
import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')


class RedisConnect():

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


class VideoFileCheck():

    def __init__(self, file_dir):
        self.file_dir = file_dir

    def get_file_size(self, file_name, is_convert=True):
        file_byte = os.path.getsize(os.path.join(self.file_dir, file_name))
        if is_convert:
            return self.size_convert(file_byte)
        else:
            return file_byte

    def size_convert(self, size):  # 单位换算
        K, M, G = 1024, 1024 ** 2, 1024 ** 3
        if size >= G:
            return str(size / G) + 'G '
        elif size >= M:
            return str(size / M) + 'M '
        elif size >= K:
            return str(size / K) + 'K '
        else:
            return str(size) + 'Bytes'


