from cipher.irc import Plugin, Events


class Kick(Plugin):
    def __init__(self, irc):
        super().__init__(irc)
        Events.privmsg += self.privmsg

    def privmsg(self, source: str, target: str, message: str):
        if not target.startswith('#'):
            return

        if message == '!kick':
            data = ('KICK %s %s Success!' % (target, source)).encode('utf-8')
            self.irc.send(data)
