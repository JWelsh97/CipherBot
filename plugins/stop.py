from cipher.irc import Plugin, Events


class Stop(Plugin):
    def __init__(self, irc):
        super().__init__(irc)
        Events.privmsg += self.privmsg

    def privmsg(self, source: str, target: str, message: str):
        if not target.startswith('#'):
            target = source

        if message == '!stop' and self.user_mode(source, target) in ['~', '&']:
            self.irc.send('QUIT :Bye')
            self.irc.stream.close()
