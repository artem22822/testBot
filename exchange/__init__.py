import requests


class AbstractExchange(object):
    """ test """

    def __init__(self, title, url):
        self.title = title
        self.url = url

    def call_api(self):
        rec = requests.get(url=self.url)
        print(rec.json())
