import logging

import redis

logger = logging.getLogger('url_shortener.db_client')


class TimeoutException(Exception):
    pass


class DBClient:
    def __init__(self, host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True):
        self.open_connect(host, port, db, charset, decode_responses)

    def __enter__(self, host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True):
        if self._r is None:
            self.open_connect(host, port, db, charset, decode_responses)
        return self

    def __del__(self):
        self.close_connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connect()

    @classmethod
    def open_connect(cls, host, port, db, charset, decode_responses):
        try:
            logger.info(f"Connecting to database {host}:{port}")
            logger.debug(f"Connection parameters: {host=}, {port=}, {db=}, {charset=}, {decode_responses=}")
            cls._r = redis.StrictRedis(host=host, port=port, db=db, charset=charset, decode_responses=decode_responses)
            if cls._r.ping():
                logger.info("Connection to database completed")
        except redis.exceptions.TimeoutError:
            logger.critical("Failed to connect to database. Check your connection settings: "
                            f"{host=}, {port=}, {db=}, {charset=}, {decode_responses=} ")
            raise TimeoutException

    @classmethod
    def close_connect(cls):
        logger.info("Disconnecting from the database")
        if cls._r is not None:
            cls._r.close()
            cls._r = None

    def set(self, key, value, ttl=None):
        try:
            self._r.set(key, value, ex=ttl)
            logger.debug(f"Database entry: {key=}, {value=}, {ttl=}")
        except redis.exceptions.TimeoutError:
            logger.warning(f"Unable to write value to database. Cause: {redis.exceptions.__unicode__(self)}")

    def get(self, key):
        try:
            res = self._r.get(key)
            logger.debug(f"Reading from database: {key=}")
        except redis.exceptions.TimeoutError:
            logger.warning(f"Unable to read value from database. Cause: {redis.exceptions.__unicode__(self)}")
            res = None
        return res
