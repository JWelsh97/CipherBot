from cipher.irc import Plugin, Events


class ListPlugins(Plugin):
    def __init__(self, irc):
        super().__init__(irc)
        Events.privmsg += self.privmsg

    def privmsg(self, source: str, target: str, message: str):
        if not target.startswith('#'):
            target = source

        if message == '!plugins':
            plugins = []
            for plugin in self.irc.plugins:
                plugins.append(type(plugin).__name__)

            self.send_msg(target, 'Loaded Plugins: %s' % ', '.join(plugins))
