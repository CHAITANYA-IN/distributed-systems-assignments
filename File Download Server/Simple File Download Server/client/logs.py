from datetime import datetime


class Record(object):
    # f'{fileStatusCodes[code]}@{str(datetime.now())}#{fileName}|{path}\n')
    def __init__(self, record):
        self.string = record
        self.status, leftOver = record.split('@', 1)
        self.status = int(self.status)
        self.time, leftOver = leftOver.split('#', 1)
        self.fileName, self.filePath = leftOver.split('|', 1)
        self.fixDataTypesAndErrors()

    def fixDataTypesAndErrors(self):
        self.filePath = self.filePath[:-1]
        self.time = datetime.fromisoformat(self.time)

    def compare(self, path, status):
        if (self.status == status and self.filePath == path):
            return self.time
        return False


def checkPreviousAccess(LOGS, path, status):
    try:
        logs = open(LOGS, 'r')
    except:
        return False
    accesses = []
    while(True):
        record = logs.readline()
        if(record == ''):
            break
        r = Record(record)
        if (r.status == status):
            time = r.compare(path, status)
            if(time):
                accesses = [time]
    logs.close()
    return False if (len(accesses) == 0) else accesses[-1]


def timeAgo(d: datetime):
    delta = (datetime.now() - d)
    days = delta.days
    deltaTime = str(delta).split(', ', 1)[1] if delta.days else str(delta)
    hours, minutes, secMicrosec = deltaTime.split(':')
    seconds, microSeconds = secMicrosec.split('.')
    agoString = ""
    if(days > 0):
        agoString += f'{days} days, '
    if(int(hours) > 0):
        agoString += f'{hours} hours, '
    if(int(minutes) > 0):
        agoString += f'{minutes} minutes, '
    agoString += f'{seconds} seconds ago'
    return agoString, d.isoformat()
