import tornado.ioloop
from cipher.irc import Bot
from cipher.config import read_config


if __name__ == '__main__':
    config = read_config()
    cli = Bot(config['host'],
              config['port'],
              config['nickname'],
              config['password'],
              config['ssl'])
    tornado.ioloop.IOLoop.instance().start()
