import os
import shelve

from threading import Thread, RLock
from queue import Queue, Empty

from utils import get_logger, get_urlhash, normalize
from scraper import is_valid

from collections import defaultdict
import urllib.request

from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request


class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = list()
        self.discovered_urls = defaultdict(int)
        self.site_checksum = {}
        self.site_content = {}

        if not os.path.exists(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
        elif os.path.exists(self.config.save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        if restart:
            for url in self.config.seed_urls:
                self.add_url(url)
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    self.add_url(url)

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save)
        tbd_count = 0
        for url, completed in self.save.values():
            if not completed and is_valid(url):
                self.to_be_downloaded.append(url)
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")

    def get_tbd_url(self):
        try:
            return self.to_be_downloaded.pop()
        except IndexError:
            return None

    def add_url(self, url):
        url = normalize(url)
        urlhash = get_urlhash(url)
        if urlhash not in self.save:
            self.save[urlhash] = (url, False)
            self.save.sync()
            self.discovered_urls[url] += 1
            # print(str(self.discovered_urls[url]))
            if self.discovered_urls[url] == 1:
                self.to_be_downloaded.append(url)

                # print("added " + url + " with value: " + str(self.discovered_urls[url]))
            # else:
            #     print("\n\n" + url + "IS A DUPLICATE\n\n")

    def mark_url_complete(self, url):
        urlhash = get_urlhash(url)
        if urlhash not in self.save:
            # This should not happen.
            self.logger.error(
                f"Completed url {url}, but have not seen it before.")
        self.save[urlhash] = (url, True)
        self.save.sync()

    def get_url_text_content(self, url):
        res = ""
        html_content = urllib.request.urlopen(url, timeout=10).read()
        soup = BeautifulSoup(html_content, features="html_parser")
        text_content = soup.findAll(text=True)
        for i in text_content:
            if i.parent.name not in ['stye', 'script', 'head', 'title', 'meta' '[document]'] and\
                not isinstance(i.parent.name, Comment):
                res += i.strip(

        print(res)




    # def check_sum_value(url) -> int:
    #     response = urllib.request.urlopen(url).read().decode("utf-8")
    #     soup = BeautifulSoup(response, features='html_parser')
    #     text = soup.get_text().decode('utf-8')
    #     text = str.encode(text)
    #
    #     response.close()
