class Plugin(object):
    def __init__(self, irc):
        self.irc = irc

    def on_join(self, user, channel):
        pass

    def on_part(self, user, channel, message):
        pass

    def privmsg(self, user: str, target: str, message: str):
        pass
