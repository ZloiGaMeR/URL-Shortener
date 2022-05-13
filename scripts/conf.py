import json
import logging

logger = logging.getLogger('url_shortener.config')
_default_config = {'db': {'ip': '192.168.2.100',
                          'port': 6379,
                          'index': 0,
                          'charset': 'utf-8',
                          'decode_responses': 'True',
                          'url_ttl': 100},
                   'server_http': {'ip': '127.0.0.1',
                                   'port': 8080}}


class Dict(dict):
    """
        dot.notation access to dictionary attributes
        Данный класс реализует возможность получения содержимого словаря через "."
        Для этого переопределяем магический метод __getattr__, заменяя его стандартным методом get класса dict.
        В результате чего при написании через "." происходит вызов метода get. Ключом в данном случае является
        написанный через "." атрибут.
        Так же переопределяем методы на присвоение значение атрибуту и удаление, заменяя их на аналогичные методы класса
        dict.
    """
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Configuration(object):

    @staticmethod
    def __load__(data):
        if type(data) is dict:
            return Configuration.load_dict(data)
        else:
            return data

    @staticmethod
    def load_dict(data: dict):
        result = Dict()
        for key, value in data.items():
            result[key] = Configuration.__load__(value)
        return result

    @staticmethod
    def load_json(path: str):
        try:
            with open(path, "r") as f:
                logger.debug(f"Read configuration from file {path}")
                result = Configuration.__load__(json.loads(f.read()))
        except FileExistsError:
            logger.warning(f"Failed to read configuration from file {path}. "
                           f"Server will be started with default parameters ")
            result = _default_config
        return result
