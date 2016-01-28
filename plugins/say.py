from cipher.irc import Plugin, Events


class Say(Plugin):
    def __init__(self, irc):
        super().__init__(irc)
        Events.privmsg += self.privmsg

    def privmsg(self, source: str, target: str, message: str):
        if message.startswith('!say'):
            message = message.split(' ')
            if len(message) == 1:
                return

            if message[1].startswith('#'):
                target = message[1]
                message = ' '.join(message[2:])
            elif target.startswith('#'):
                message = ' '.join(message[1:])
            else:
                target = source
                message = ' '.join(message[1:])

            self.send_msg(target, message)
