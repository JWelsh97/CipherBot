class Plugin(object):
    def __init__(self, irc):
        self.irc = irc

    def on_join(self, user, channel):
        pass

    def on_part(self, user, channel, message):
        pass

    def privmsg(self, source: str, target: str, message: str):
        pass

    def send_msg(self, target, message):
        self.irc.send('PRIVMSG %s %s' % (target, message))

    def user_mode(self, user, channel):
        try:
            mode = self.irc.users[channel][user]
        except KeyError:
            mode = ''

        if 'q' in mode:
            return '~'
        elif 'a' in mode:
            return '&'
        elif 'o' in mode:
            return '@'
        elif 'h' in mode:
            return '%'
        elif 'v' in mode:
            return '+'
        else:
            return ''
