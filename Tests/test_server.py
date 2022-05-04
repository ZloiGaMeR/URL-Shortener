import pytest
import redis
import unittest.mock as mock
from io import BytesIO as IO

import scripts.server
from scripts.server import MyHandler
from scripts.bd_client import DBClient


class TestServerSuitePositive:
    '''
    Позитивные тесты
    '''
    @classmethod
    def setup_class(cls):
        redis.StrictRedis = mock.Mock()
        cls.db = DBClient()
        cls.db._r.get.return_value = b"https://habr.com/ru/all/"

    def test_do_post(self):
        '''
        В данном тесте проверяется стандартная работа функции do_POST. Имитируем POST запрос и проверяем наличие ответа
        с кодом 200 и содержанием короткой ссылки. Так же проверяем что метод set, отвевающий за запись в базу данных,
        был вызван 1 раз с параметром в виде ссылки(которую требовалось сократить и которая была передана в имитируемом
        POST запросе).
        '''
        MyHandler.send_error = mock.Mock()
        MyHandler.send_response = mock.Mock()
        MyHandler.wfile = mock.Mock()
        MyHandler.gen_url = mock.Mock()
        MyHandler.gen_url.return_value = "abcdefg"
        req = mock.Mock()
        req.makefile.return_value = IO(b"POST / HTTP/1.1\n"
                                       b"Content-Type: application/x-www-form-urlencoded\n"
                                       b"Content-Length: 24\n"
                                       b"\n"
                                       b"https://habr.com/ru/all/")
        handler = MyHandler(self.db, "127.0.0.1", 6379, 1000, request=req,
                            client_address='0.0.0.0', server=("127.0.0.1", 8080))
        handler.send_response.assert_called_with(200)
        handler.wfile._sock.sendall.assert_called_with(b'Your short URL: http://127.0.0.1:6379/abcdefg')
        assert handler._bd._r.set.call_count == 1
        assert handler._bd._r.set.call_args.args[1] == "https://habr.com/ru/all/"

    def test_do_get(self):
        '''
        В данном тесте проверяем стандартную работу функции do_GET. Имитируем GET запрос содержащий короткую ссылку.
        Проверяем наличие ответа с кодом 301 и длинной ссылкой. Так же проверяем то что метод get был вызван 1 раз
        и в качестве параметра передавалась короткая ссылка из GET запроса.
        '''
        MyHandler.send_error = mock.Mock()
        MyHandler.send_response = mock.Mock()
        MyHandler.wfile = mock.Mock()
        req = mock.Mock()
        req.makefile.return_value = IO(b"GET /http://127.0.0.1:6379/abcdefg HTTP/1.1\n")
        handler = MyHandler(self.db, "127.0.0.1", 6379, 1000, request=req,
                            client_address='0.0.0.0', server=("127.0.0.1", 8080))
        handler.send_response.assert_called_with(301)
        handler.wfile._sock.sendall.assert_called_with(b"Location: b'https://habr.com/ru/all/'\r\n\r\n")
        assert handler._bd._r.get.call_count == 1
        assert handler._bd._r.get.call_args.args[0] == b"/http://127.0.0.1:6379/abcdefg"


class TestServerSuiteNegative:
    '''
    Негативные тесты
    '''
    @classmethod
    def setup_class(cls):
        redis.StrictRedis = mock.Mock()
        cls.db = DBClient()
        cls.db._r.get.return_value = None

    def test_do_post(self):
        '''
        В данном тесте проверяем работу метода do_POST с некорректными входными данными. Первый генерируемый запрос
        содержит некорректный Content-Type. Проверяем что в ответ отправлено сообщение "INCORRECT_REQUEST".
        Второй запрос не содержит URL ссылки. Проверяем что в ответ отправлено сообщение "URL 123 is not correct".
        '''
        MyHandler.send_error = mock.Mock()
        MyHandler.send_response = mock.Mock()
        MyHandler.wfile = mock.Mock()
        req = mock.Mock()
        req.makefile.return_value = IO(b"POST / HTTP/1.1\n"
                                       b"Content-Type: text/html\n"
                                       b"Content-Length: 3\n"
                                       b"\n"
                                       b"123")
        handler = MyHandler(self.db, "127.0.0.1", 6379, 1000, request=req,
                            client_address='0.0.0.0', server=("127.0.0.1", 8080))
        handler.send_response.assert_called_with(200)
        handler.wfile._sock.sendall.assert_called_with(scripts.server.INCORRECT_REQUEST.encode())
        req.makefile.return_value = IO(b"POST / HTTP/1.1\n"
                                       b"Content-Type: application/x-www-form-urlencoded\n"
                                       b"Content-Length: 3\n"
                                       b"\n"
                                       b"123")
        handler = MyHandler(self.db, "127.0.0.1", 6379, 1000, request=req,
                            client_address='0.0.0.0', server=("127.0.0.1", 8080))
        handler.send_response.assert_called_with(200)
        handler.wfile._sock.sendall.assert_called_with(b'URL 123 is not correct.')

    def test_do_get(self):
        '''
        В данном тесте проверяем работу метода do_GET с некорректными параметрами. При обработке GET запроса в качестве
        результата чтения из базы данных функцией get получаем None, что приводит к ошибке 404.
        '''
        MyHandler.send_error = mock.Mock()
        MyHandler.send_response = mock.Mock()
        req = mock.Mock()
        req.makefile.return_value = IO(b"GET /https://habr.com/ru/all/ HTTP/1.1\n")
        handler = MyHandler(self.db, "127.0.0.1", 6379, 1000, request=req,
                            client_address='0.0.0.0', server=("127.0.0.1", 8080))
        handler.send_error.assert_called_with(404)
        assert handler._bd._r.get.call_count == 1


if __name__ == '__main__':
    pytest.main()
