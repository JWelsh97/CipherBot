from cipher.irc import Plugin, Events


class Kick(Plugin):
    def __init__(self, irc):
        super().__init__(irc)
        Events.privmsg += self.privmsg

    def privmsg(self, source: str, target: str, message: str):
        if not target.startswith('#'):
            return

        if message.startswith('!kick'):
            if self.user_mode(source, target) in ['~', '&', '@']:
                message = message.split(' ')
                kick_user = message[1]
                if len(message) >= 3:
                    kick_reason = ' '.join(message[2:])
                else:
                    kick_reason = ''
                data = 'KICK %s %s %s' % (target, kick_user, kick_reason)
                self.irc.send(data)
            else:
                self.send_msg(target, 'You are not allowed to use that command.')
