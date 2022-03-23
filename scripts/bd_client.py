import redis
import logging


logger = logging.getLogger('run.db_client')
# Создаем подключение


class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True):
        try:
            logger.info(f"Connecting to database {host}:{port}")
            logger.debug(f"Connection parameters: {host=}, {port=}, {db=}, {charset=}, {decode_responses=}")
            self._r = redis.StrictRedis(host=host, port=port, db=db, charset=charset, decode_responses=decode_responses)
            if self._r.ping():
                logger.info("Connection to database completed")
        except redis.exceptions.TimeoutError:
            logger.critical("Failed to connect to database. Check your connection settings: "
                            f"{host=}, {port=}, {db=}, {charset=}, {decode_responses=} ")
            logger.critical("Exit application")
            raise SystemExit

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.info("Disconnecting from the database")
        self._r.close()

    def set(self, key, value, ttl=-1):
        try:
            self._r.set(key, value, ttl)
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
