from cipher.irc import Plugin, Events
from cipher.db import execute
from tornado import gen


class GetUser(Plugin):
    def __init__(self, irc):
        super().__init__(irc)
        Events.privmsg += self.privmsg

    @gen.coroutine
    def privmsg(self, source: str, target: str, message: str):
        if not target.startswith('#'):
            target = source

        if message.startswith('!u'):
            message = message.split(' ')
            if len(message) != 2:
                return

            username = message[1]
            paranoia = yield execute('SELECT Paranoia FROM users_main WHERE Username = %s', username)
            if paranoia:
                paranoia = paranoia[0][0]

            data = yield execute("SELECT Username,Uploaded,Downloaded FROM users_main WHERE Username = %s", username)
            if data:
                username, upload, download = data[0][:3]
                if 'uploaded' not in paranoia:
                    ul, ul_abbr = self.convert_type(upload)
                else:
                    ul = 'PRIVATE'
                    ul_abbr = ''

                if 'downloaded' not in paranoia:
                    dl, dl_abbr = self.convert_type(download)
                else:
                    dl = 'PRIVATE'
                    dl_abbr = ''

                self.send_msg(target, '%s - U: \x0304%s\x0F %s - D: \x0304%s\x0F %s' %
                              (username, ul, ul_abbr, dl, dl_abbr))
            else:
                self.send_msg(target, 'User not found.')

    @staticmethod
    def convert_type(size):
        abbr = 'b'
        if size > 1073741824:
            size /= 1073741824
            abbr = 'GB'
        elif size > 1048576:
            size /= 1048576
            abbr = 'MB'
        elif size >= 1024:
            size /= 1024
            abbr = 'KB'
        return size, abbr
