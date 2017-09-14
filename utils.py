import signal
import requests
from urllib import request

import os, sys
from PIL import Image

user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/55.0.2883.87 Safari/537.36'}


class DownloadException(Exception):
    pass


class TimeoutException(Exception):
    pass


def _timeout(signum, frame):
    raise TimeoutException()


def merge_spaces(s):
    if s is None:
        return ''
    if len(s) == 0:
        return ''
    s = s.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ').replace('\n\xa0', ' ')
    s_new = ''
    for i in range(0, len(s) - 1):
        if not (s[i] == ' ' and s[i + 1] == ' '):
            s_new += s[i]
    return (s_new + s[-1]).strip()


def get_soup(url):
    from bs4 import BeautifulSoup

    _, html = get_html(url)
    return BeautifulSoup(html, 'lxml')


# Retrieve the html and the url after redirection of a given url
# There are a lot of exceptions to handle there..
def get_html(url, timeout_seconds=20):
    signal.signal(signal.SIGALRM, _timeout)
    signal.alarm(timeout_seconds)

    verbose = False

    try:  # sometimes the async SIGALRM signal is called outside of the inner try/except
        try:  # force timeout of the request
            resp = requests.get(url, allow_redirects=True, headers=user_agent)
        except TimeoutException:
            if verbose: print('Request timed out:', url)
            raise DownloadException('timeout')
        except Exception as e:  # an exception from requests lib
            if verbose: print('\'{}\' exception retrieving URL \'{}\': {}'.format(type(e), url, e))
            raise DownloadException('unknown exception', {'exception': e})
        else:
            if not resp.ok:  # content fetched without any exception but error code
                if verbose: print('Bad status code for URL \'{}\': {}'.format(url, resp.status_code))
                raise DownloadException('bad status code', {'status_code': resp.status_code})
            elif not resp.headers.get('content-type', '').startswith('text/html'):  # content is not html
                if verbose: print('Not a html url:', url)
                raise DownloadException('bad content type', {'content_type': resp.headers.get('content-type', None)})
            else:  # valid response, & html file
                if 'dnserrorassist' in resp.text:  # AT&T display custom page when the url doesn't exist
                    if verbose: print('Got ATT DNS... Probably invalid URL:', url)
                    raise DownloadException('att dns error')
                else:
                    if verbose: print('Successfully fetched:', url)
                    try:
                        return resp.url, resp.content.decode('utf-8')
                    except UnicodeDecodeError:
                        # sometimes decoding with utf-8 does not work, use requests built-in instead
                        if verbose: print('Error (ignored) converting to unicode:', url)
                        return resp.url, resp.text
    except TimeoutException:
        if verbose: print('Timeout after request ended: ignore it:', url)
    finally:
        signal.alarm(0)


def download_and_save_image(url, save_path):
    try:
        request.urlretrieve(url, save_path)
    except Exception as e:
        print('could not load : ' + url)
        print(e)


def resize_picture(path, height, width):

    size = height, width

    try:
        im = Image.open(path)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(path, "JPEG")
    except IOError:
        print("cannot create thumbnail for '%s'" % path)
        os.remove(path)
