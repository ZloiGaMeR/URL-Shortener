import argparse


def load_version():
    with open("./etc/version.cfg", "r") as f:
        return f.read()


def create_parse_args():
    parser = argparse.ArgumentParser(
        prog='URL Shortener',
        description='''Простая программа по сокращению длинных URL ссылок''',
        epilog='''(c) Март 2021. Автор программы, как всегда,
    не несет никакой ответственности ни за что =)''',
        add_help=False
    )
    parent_group = parser.add_argument_group(title='Параметры')
    parent_group.add_argument('--help', '-h', action='help', help='Справка')
    parent_group.add_argument('--version',
                              action='version',
                              help='Вывести номер версии',
                              version=f'%(prog)s {load_version()}')
    parent_group.add_argument('--configuration', '-c',
                              type=argparse.FileType(mode='r'),
                              default='./etc/config.json',
                              help='Путь к файлу конфигурации сервера',
                              metavar='ПУТЬ')
    subparser = parser.add_subparsers(dest='command',
                                      title='Возможные команды',
                                      description='Команды, которые должны быть в качестве параметра %(prog)s')
    logging_on_parser = subparser.add_parser('Logging',
                                             add_help=False,
                                             help='Запуск сервера с поддержкой логов',
                                             description='Запуск сервера с поддержкой логов.'
                                                         'В этом режиме запись логов осуществляется в '
                                                         'указанный лог файл,'
                                                         'с указанным уровнем логирования')
    loging_on_group = logging_on_parser.add_argument_group(title='Параметры')
    loging_on_group.add_argument('-path', '-p', default=None,
                                 help='Путь до файла логов',
                                 metavar="ПУТЬ")
    loging_on_group.add_argument('--level', '-l',
                                 choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'],
                                 default='DEBUG',
                                 help='Уровень ведения журнала',
                                 metavar="Уровень"
                                 )
    loging_on_group.add_argument('--help', '-h', action='help', help='Справка')
    return parser
