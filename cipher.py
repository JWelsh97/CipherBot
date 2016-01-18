from bot import Bot
import tornado.ioloop

if __name__ == '__main__':
    cli = Bot('affinity.pw', 6697, ['Cipher', 'Cipher_', 'Cipher__'], '', True)
    tornado.ioloop.IOLoop.instance().start()
