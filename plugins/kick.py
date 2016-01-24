from cipher.plugin import Plugin
from cipher.event import Events


class Kick(Plugin):
    def __init__(self, irc):
        super().__init__(irc)

        # Set plugin name
        self.name = 'kick'

        # Subscribe to events
        Events.privmsg.append(self.msg)

    def msg(self, user, target, message):
        if not target.startswith('#'):
            return

        if message == '!kick':
            data = ('KICK %s %s Success!' % (target, user)).encode('utf-8')
            self.irc.send(data)
