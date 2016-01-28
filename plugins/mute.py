from cipher.irc import Plugin, Events


class Mute(Plugin):
    def __init__(self, irc):
        super().__init__(irc)
        Events.privmsg += self.privmsg

    def privmsg(self, source: str, target: str, message: str):
        if not target.startswith('#'):
            return

        if message.startswith('!mute'):
            if self.user_mode(source, target) in ['~', '&', '@']:
                message = message.split(' ')
                mute_user = message[1]
                data = 'MODE %s +b m:%s!*@*' % (target, mute_user)
                self.irc.send(data)
            else:
                self.send_msg(target, 'You are not allowed to use that command.')

        elif message.startswith('!unmute'):
            if self.user_mode(source, target) in ['~', '&', '@']:
                message = message.split(' ')
                mute_user = message[1]
                data = 'MODE %s -b m:%s!*@*' % (target, mute_user)
                self.irc.send(data)
            else:
                self.send_msg(target, 'You are not allowed to use that command.')
