from cipher.irc import Plugin, Events


class MyPlugin(Plugin):
    def __init__(self, irc):
        super().__init__(irc)
        Events.privmsg += self.privmsg

    def privmsg(self, source: str, target: str, message: str):
        if not target.startswith('#'):
            target = source

        if message == '!test':
            self.send_msg(target, 'Success!')
