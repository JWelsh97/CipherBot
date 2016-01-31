class Event(object):
    def __init__(self):
        self.__handlers = []

    def __iadd__(self, other):
        if isinstance(other, list):
            self.__handlers += other
        else:
            self.__handlers.append(other)
        return self

    def append(self, other):
        self.__handlers.append(other)

    def notify(self, *args):
        for handler in self.__handlers:
            if args:
                handler(*args)
            else:
                handler()


class Events:
    join = Event()
    part = Event()
    privmsg = Event()
    quit = Event()
    mode_change = Event()
