import pytest
import redis
import unittest.mock as mock
from io import BytesIO as IO

import scripts.db_client as db_client
import scripts.server as server


class TestServerSuitePositive:
    '''
    Позитивные тесты
    '''

    @classmethod
    def setup_class(cls):
        redis.StrictRedis = mock.Mock()
        cls.db = db_client.DBClient()
        cls.db._r.get.return_value = b"https://habr.com/ru/all/"

    def test_do_post(self):
        '''
        В данном тесте проверяется стандартная работа функции do_POST. Имитируем POST запрос и проверяем наличие ответа
        с кодом 200 и содержанием короткой ссылки. Так же проверяем что метод set, отвевающий за запись в базу данных,
        был вызван 1 раз с параметром в виде ссылки(которую требовалось сократить и которая была передана в имитируемом
        POST запросе).
        '''
        server.MyHandler.send_error = mock.Mock()
        server.MyHandler.send_response = mock.Mock()
        server.MyHandler.wfile = mock.Mock()
        server.MyHandler.gen_url = mock.Mock()
        server.MyHandler.gen_url.return_value = "abcdefg"
        req = mock.Mock()
        req.makefile.return_value = IO(b"POST / HTTP/1.1\n"
                                       b"Content-Type: application/x-www-form-urlencoded\n"
                                       b"Content-Length: 24\n"
                                       b"\n"
                                       b"https://habr.com/ru/all/")
        handler = server.MyHandler(self.db, "127.0.0.1", 6379, 1000, request=req,
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
        server.MyHandler.send_error = mock.Mock()
        server.MyHandler.send_response = mock.Mock()
        server.MyHandler.wfile = mock.Mock()
        req = mock.Mock()
        req.makefile.return_value = IO(b"GET /http://127.0.0.1:6379/abcdefg HTTP/1.1\n")
        handler = server.MyHandler(self.db, "127.0.0.1", 6379, 1000, request=req,
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
        cls.db = db_client.DBClient()
        cls.db._r.get.return_value = None

    def test_do_post(self):
        '''
        В данном тесте проверяем работу метода do_POST с некорректными входными данными. Первый генерируемый запрос
        содержит некорректный Content-Type. Проверяем что в ответ отправлено сообщение "INCORRECT_REQUEST".
        Второй запрос не содержит URL ссылки. Проверяем что в ответ отправлено сообщение "URL 123 is not correct".
        '''
        server.MyHandler.send_error = mock.Mock()
        server.MyHandler.send_response = mock.Mock()
        server.MyHandler.wfile = mock.Mock()
        req = mock.Mock()
        req.makefile.return_value = IO(b"POST / HTTP/1.1\n"
                                       b"Content-Type: text/html\n"
                                       b"Content-Length: 3\n"
                                       b"\n"
                                       b"123")
        handler = server.MyHandler(self.db, "127.0.0.1", 6379, 1000, request=req,
                                   client_address='0.0.0.0', server=("127.0.0.1", 8080))
        handler.send_response.assert_called_with(200)
        handler.wfile._sock.sendall.assert_called_with(server.INCORRECT_REQUEST.encode())
        req.makefile.return_value = IO(b"POST / HTTP/1.1\n"
                                       b"Content-Type: application/x-www-form-urlencoded\n"
                                       b"Content-Length: 3\n"
                                       b"\n"
                                       b"123")
        handler = server.MyHandler(self.db, "127.0.0.1", 6379, 1000, request=req,
                                   client_address='0.0.0.0', server=("127.0.0.1", 8080))
        handler.send_response.assert_called_with(200)
        handler.wfile._sock.sendall.assert_called_with(b'URL 123 is not correct.')

    def test_do_get(self):
        '''
        В данном тесте проверяем работу метода do_GET с некорректными параметрами. При обработке GET запроса в качестве
        результата чтения из базы данных функцией get получаем None, что приводит к ошибке 404.
        '''
        server.MyHandler.send_error = mock.Mock()
        server.MyHandler.send_response = mock.Mock()
        req = mock.Mock()
        req.makefile.return_value = IO(b"GET /https://habr.com/ru/all/ HTTP/1.1\n")
        handler = server.MyHandler(self.db, "127.0.0.1", 6379, 1000, request=req,
                                   client_address='0.0.0.0', server=("127.0.0.1", 8080))
        handler.send_error.assert_called_with(404)
        assert handler._bd._r.get.call_count == 1


if __name__ == '__main__':
    pytest.main()
