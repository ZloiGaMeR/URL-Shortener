import redis


# Создаем подключение
class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True):
        try:
            self._r = redis.StrictRedis(host=host, port=port, db=db, charset=charset, decode_responses=decode_responses)
            if self._r.ping():
                print("Соединение с базой данных установлено")
        except redis.exceptions.TimeoutError:
            print("Не удалось установить соединение с базой данных")
            raise SystemExit

    def __enter__(self):
        return self._r

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._r.close()

    def set(self, key, value, ttl=-1):
        try:
            print("redis_set")
            self._r.set(key, value, ttl)
            print("after set")
        except redis.exceptions.TimeoutError:
            print(f"Не удалось записать значение в БД. Причина: {redis.exceptions.__unicode__(self)}")

    def get(self, key):
        return self._r.get(key)
