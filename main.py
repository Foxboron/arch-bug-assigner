#! /usr/bin/env python3

import os
import re
import time

import requests
from bs4 import BeautifulSoup

import bugs


USER = os.getenv("BUGTRACKER_USER", "")
PASSWORD = os.getenv("BUGTRACKER_PASS", "")

TARGET_PAGE = "https://bugs.archlinux.org/index.php?events%5B%5D=1&event_number=600&project=5&do=reports"

SOUP_PARSE = 'lxml'


class Session(object):

    def __init__(self):
        self.user = USER
        self.password = PASSWORD
        self.login_page = 'https://bugs.archlinux.org/index.php?do=authenticate'
        self.target_page = TARGET_PAGE

        self.opener = requests.Session()
        self.opener.headers.update({'User-agent': 'Mozilla/5.0'})

        # need this twice - once to set cookies, once to log in...
        self.login()
        self.login()

    def get_soup(self, url):
        while True:
            try:
                response = self.opener.get(url)
                break
            except Exception:
                print('Failed request')
                time.sleep(10)
        return BeautifulSoup(response.text, features=SOUP_PARSE)

    def login(self):
        "handle login, populate the cookie jar"
        login_data = {'user_name': self.user,
                      'password': self.password,
                      'remember_login': 'on'}
        response = self.opener.get(self.login_page, params=login_data, allow_redirects=False)
        return response.text


SESSION = Session()


def extract(soupy):
    if isinstance(soupy, str):
        return str(soupy)
    return str(soupy.extract())


class Bugtracker(object):

    def get_bugreport(self, url):
        soup = SESSION.get_soup(url)
        body = soup.html.body
        mains = []
        for main in body.find(headers='assignedto').findAll('a'):
            mains.append(main['href'].split("/")[-1])
        ret = {
                'title': soup.html.title.text, 
                'maintainers': mains,
                'category': body.find(headers='category').text.split()[-1].replace('\\t',''),
            }
        ret["package"] = re.findall(r'\[(.+?)\]', ret["title"])
        soup.decompose()
        return ret

    def get_recent(self):
        soup = SESSION.get_soup(self.target_page)
        body = soup.html.body
        tasks = body.find(**{'id': 'tasklist_table'}).findAll('tr')[1:]
        results = []
        for t in tasks:
            t = t.findAll('td')
            status = extract(t[3].a['title'])
            if status.endswith(' | 100%'):
                continue
            results.append({'event':   extract(t[0].contents[0]),
                            'date':    extract(t[2].contents[0]),
                            'url':     extract(t[3].a['href'].partition('?')[0]),
                            'status':  status,
                            'summary': extract(t[3].a.contents[0]),
                           })
        soup.decompose()
        return results

    def clean_misc(self, event):
        "remove waste of ascii"
        for k, v in event.items():
            event[k] = str(v)
        if event['status'].endswith(' | 100%'):
            event['status'] = event['status'][:-7]
        if event['status'].endswith(' | 0%'):
            event['status'] = event['status'][:-5]
        return event


def main():
    bt = Bugtracker()
    bug = bugs.Bug(SESSION, "")
    # res = bt.get_recent()
    # for n in res:
    #     print(n)
    #     break
    print(bt.get_bugreport("https://bugs.archlinux.org/task/69474"))
    bug.assign_bug()

if __name__ == "__main__":
    main()
