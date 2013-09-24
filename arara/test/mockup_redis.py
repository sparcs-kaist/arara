import operator
class PipelineMockup(object):
    def __init__(self, redis):
        self.buffer = []
        self.redis = redis

    def sadd(self, key, value):
        self.redis.sadd(key, value)

    def sismember(self, key, value):
        self.buffer.append(self.redis.sismember(key, value))

    def set(self, key, value):
        self.redis.set(key, value)

    def get(self, key):
        self.buffer.append(self.redis.get(key))

    def execute(self):
        r = self.buffer
        self.buffer = []
        return r

class RedisMockup(object):
    def __init__(self, host, port, db):
        self.data = {}

    def sadd(self, key, val):
        if not key in self.data:
            self.data[key] = set()
        self.data[key].add(val)

    def sismember(self, key, val):
        if not key in self.data:
            return False
        return val in self.data[key]

    def smembers(self, key):
        return list(self.data.get(key, []))

    def srem(self, key, val):
        self.data[key].remove(val)

    def get(self, key):
        return self.data.get(key, None)

    def set(self, key, val):
        self.data[key] = val

    def delete(self, key):
        if key in self.data:
            del self.data[key]

    def pipeline(self):
        return PipelineMockup(self)

    def zadd(self, key, *args, **kwargs):
        if kwargs:
            score_dict = kwargs
        elif args:
            score_dict = dict(zip(args[1::2], args[::2]))
        else:
            score_dict = {}

        for (val, score) in score_dict.iteritems():
            if not key in self.data:
                self.data[key] = {}
            self.data[key][val] = score

    def zrange(self, key, score_from, score_to, withscores, score_cast_func=int, reverse=False):
        if key not in self.data:
            return []

        items = sorted(self.data[key].items(), key=operator.itemgetter(1, 0), reverse=reverse)

        score_to += 1
        if score_to:
            target_items = items[score_from:score_to]
        else:
            target_items = items[score_from:]

        if withscores:
            return target_items
        else:
            return [x for (x, y) in target_items]

    def zrevrange(self, key, score_from, score_to, withscores, score_cast_func=int):
        return self.zrange(key, score_from, score_to, withscores, score_cast_func, reverse=True)

    def zremrangebyrank(self, key, score_from, score_to):
        if key not in self.data:
            return

        items = sorted(self.data[key].items(), key=operator.itemgetter(1, 0))

        score_to += 1
        if score_to:
            removing_items = items[score_from:score_to]
        else:
            removing_items = items[score_from:]

        for (value, score) in removing_items:
            del self.data[key][value]

    def zremrangebyscore(self, key, score_from, score_to):
        if key not in self.data:
            return

        if score_from == "-inf":
            score_from = -99999999999999999999999999999999999999
        else:
            score_from = float(score_from)
            score_to = float(score_to)

        for (value, score) in self.data[key].items():
            if score_from <= score <= score_to:
                del self.data[key][value]

    def expire(self, *args, **kwargs):
        pass  # TODO

    def zscore(self, key, value):
        return self.data.get(key, {}).get(value)

class TestMockupRedis(object):
    def test_set_type(self):
        redis = RedisMockup('127.0.0.1', '1234', 0)
        redis.sadd('myset', 'hello')
        redis.sadd('myset', 'world')
        redis.sadd('myset', 'world')
        assert set(redis.smembers('myset')) == set(('hello', 'world'))

        assert redis.sismember('myset', 'hello') == True
        assert redis.sismember('myset', 'foobar') == False

        redis.srem('myset', 'world')
        assert set(redis.smembers('myset')) == set(('hello', ))

    def test_orderedset_type(self):
        redis = RedisMockup('127.0.0.1', '1234', 1)
        redis.zadd('myzset', 1, 'one')
        redis.zadd('myzset', 1, 'uno')
        redis.zadd('myzset', 2, 'two')
        redis.zadd('myzset', **{'two': 3})
        assert (redis.zrange('myzset', 0, -1, withscores=True) ==
                ["one", 1, "uno", 1, "two", 3])
        assert (redis.zrange('myzset', 0, -2, withscores=True) ==
                ["one", 1, "uno", 1])
        assert (redis.zrange('myzset', 1, -1, withscores=False) ==
                ["uno", "two"])

        redis.zremrangebyrank('myzset', 0, -2)
        assert (redis.zrange('myzset', 0, -1, withscores=True) ==
                ["two", 3])
