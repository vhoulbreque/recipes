
# a custom generic exception raised if any errors appears during download
class DownloadException(Exception): pass


class TimeoutException(Exception):
    pass

def _timeout(signum, frame):
    raise TimeoutException()
