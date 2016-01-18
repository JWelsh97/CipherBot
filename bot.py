from irc import IRC
import ssl


class Bot(IRC):
    def __init__(self, host: str, port: int, nicks: list, pwd: str,
                 use_ssl: bool=False, ssl_options: ssl.SSLContext=None,
                 encoding: str='utf-8'):
        super().__init__(host, port, nicks, pwd, use_ssl, ssl_options, encoding)