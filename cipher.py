import tornado.ioloop
from cipher.irc import Bot
from cipher.config import read_config


if __name__ == '__main__':
    config = read_config()
    cli = Bot(db_config=config['db'], **config['bot'])
    tornado.ioloop.IOLoop.instance().start()
