from cipher.plugin import Plugin
from cipher.event import Events


class ListPlugins(Plugin):
    def __init__(self, irc):
        super().__init__(irc)
        Events.privmsg += self.msg

    def msg(self, user, target, message):
        if not target.startswith('#'):
            target = user

        if message == '!plugins':
            for plugin in self.irc.plugins:
                data = ('PRIVMSG %s Loaded Plugin: %s' % (target, type(plugin).__name__)).encode('utf-8')
                self.irc.send(data)
