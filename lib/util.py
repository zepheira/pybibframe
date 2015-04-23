import time

class LoggedList(list):
    '''
    Used to capture the order in which subfields are added to the Versa input model
    '''
    def __init__(self, *args, **kwargs):
        super(LoggedList, self).__init__(*args, **kwargs)
        self.log = []
        if len(args) > 0:
            self.log.append((args[0][0], time.time())) # capture initialization value and time

    def append(self, item):
        super(LoggedList, self).append(item)
        self.log.append((item, time.time()))
