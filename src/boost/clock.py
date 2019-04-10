from datetime import datetime


class Clock(object):
    @staticmethod
    def now():
        return datetime.now()
