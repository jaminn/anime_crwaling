import html
import re

import execjs
import requests
import time
from get_anigod_list import get_anigod_list
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor


class Timer:
    def __enter__(self):
        print("START")
        self.start = time.time()
        return self

    def __exit__(self, *args):
        print("END")
        self.end = time.time()
        self.time = self.end - self.start
        print("걸린시간:")
        print(self.time)


def retryer(max_retries=20, timeout=2000):
    def wraps(func):
        request_exceptions = (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
            IndexError
        )

        def inner(*args, **kwargs):
            for i in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                except request_exceptions:
                    print("retry")
                    time.sleep(timeout)
                    continue
                else:
                    return result
            else:
                raise ConnectionError

        return inner

    return wraps


@retryer()
def get_html(*args, **kwargs):
    return str(requests.get(*args, **kwargs).text)


@retryer()
def get_real_video(my_url):
    out = get_html(my_url, allow_redirects=False)
    out = html.unescape(out)
    result = re.findall(r'<a href="([\s\S]*?)">', out)[0]
    return result


@retryer()
def anigod2text(str_url):
    headers = {'referer': 'http://t.umblr.com/'}
    string = get_html(str_url, headers=headers)
    return str(string)


@retryer()
def anigod2name_url_sumnail(str_url):
    pattern = "<h1>.*?<a.*?>([\s\S]*?)<\/a>.*?<\/h1>"
    pattern2 = '<img class="cover-profile" src="([\s\S]*?)"\/>'
    pattern3 = r"var videoID =[\s\S]*?'([\s\S]*?)'"
    my_ani = anigod2text(str_url)
    name = re.findall(pattern, my_ani)[0]
    sumnail = re.findall(pattern2, my_ani)[0]
    videoID = re.findall(pattern3, my_ani)[0]
    # string = quote(videoID, safe='~()*!.\'')
    string = execjs.eval("encodeURIComponent('" + videoID + "')")
    past_url = "https://anigod.com/video?id=" + (string)
    url = get_real_video(past_url)
    return {"name": html.unescape(name), "sumnail": sumnail, "url": url}


def main_url2ani_list(main_url):
    aniSubUrl = get_anigod_list(main_url)
    with ThreadPoolExecutor(max_workers=20) as executor:
        result = executor.map(lambda url: anigod2name_url_sumnail(url), aniSubUrl)
    aniList = list(result)
    return aniList


def main_url2ani_info(main_url):
    patt = r'<h1><a href=".*?">(.*?)<\/a><\/h1>'
    patt2 = r'<img class="cover-profile" src="([\s\S]*?)"\/>'
    text = get_html(main_url)
    name = re.findall(patt, text)[0]
    sumnail = re.findall(patt2, text)[0]
    return {"name": name, "sumnail": sumnail}


def get_ani_data(main_url):
    info = main_url2ani_info(main_url)
    list = main_url2ani_list(main_url)
    result = {"info": info, "list": list}
    return result


def db_connect():
    client = MongoClient("localhost", 27017)
    db = client.ani_db
    return db


if __name__ == "__main__":
    main_url = "https://anigod.com/animation/%EB%82%98%EB%A3%A8%ED%86%A0-17"
    db = db_connect()
    result = get_ani_data(main_url)
    db.anime.delete_many({})
    db.anime.insert(result)

    for ani in db.anime.find():
        print(ani['info']['name'])
