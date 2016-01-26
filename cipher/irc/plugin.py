class Plugin(object):
    def __init__(self, irc):
        self.irc = irc

    def on_join(self, user, channel):
        pass

    def on_part(self, user, channel, message):
        pass

    def privmsg(self, source: str, target: str, message: str):
        pass

    def send_msg(self, target, message):
        self.irc.send('PRIVMSG %s %s' % (target, message))
