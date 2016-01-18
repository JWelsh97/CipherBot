from bot import Bot
import tornado.ioloop
import config

config = config.read_config()
if __name__ == '__main__':
    cli = Bot(config['irc_host'],
              config['port'],
              [config['nickname'], '%s_' % config['nickname'], '%s__' % config['nickname']],
              config['password'],
              config['ssl'])
    tornado.ioloop.IOLoop.instance().start()

