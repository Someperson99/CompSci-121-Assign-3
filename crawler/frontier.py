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
import re


class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = list()

        # store all the urls that have been downloaded already so
        # that the same url isn't downloaded twice
        self.discovered_urls = defaultdict(int)
        # dictionary that would contain a key value pair of the checksum value
        # and url

        # Dictionary of word as key and it's frequency as value
        self.word_frequencies = defaultdict(int)

        self.site_checksum = {}

        # key value pairs of urls and the text contained in them
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
            if self.discovered_urls[url] == 1:
                self.to_be_downloaded.append(url)

    def mark_url_complete(self, url):
        urlhash = get_urlhash(url)
        if urlhash not in self.save:
            # This should not happen.
            self.logger.error(
                f"Completed url {url}, but have not seen it before.")
        self.save[urlhash] = (url, True)
        self.save.sync()

    def store_page_text_content(self, resp, url):
        # is a method to insert the url and associate it with the value which would
        # be all of the text content in the page by calling self.get_url_text_content
        # will be stored in self.site_content
        self.site_content[url] = self.get_url_text_content(resp)

    def tokenize(self, text):
        token_lst = []
        for line in text:
            alpha_lst = re.split(r'[^a-zA-Z0-9]+', line)
            for i in list(filter(lambda w: re.match(r'[a-zA-Z0-9]+', w), alpha_lst)):
                token_lst.append(i.lower())
                self.word_frequencies[i.lower()] += 1
        return token_lst

    def get_url_text_content(self, resp):
        # given a raw response the function will use BeautifulSoup to
        # take out all of the relevant text, will the concatenate all
        # of the text and then return it. To filter what is valuable
        # text and what is not is handled by self.filter_text
        soup = BeautifulSoup(resp.raw_response.text, features="html.parser")
        text_content = soup.findAll(text=True)
        relevant_text = filter(self.filter_text, text_content)
        return self.tokenize(text_content)

    def filter_text(self, unfiltered_text):
        # found the tags that don't hold valuable text from
        # https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
        # as well as
        # https://matix.io/extract-text-from-webpage-using-beautifulsoup-and-python/
        if unfiltered_text.parent.name in ['style', 'script', 'noscript', 'header',
                                            'head', 'title', 'meta', '[document]', 'html',
                                           'input']:
            return False
        if isinstance(unfiltered_text, Comment):
            return False
        return True

    # def check_sum_value(url) -> int:
    #     response = urllib.request.urlopen(url).read().decode("utf-8")
    #     soup = BeautifulSoup(response, features='html_parser')
    #     text = soup.get_text().decode('utf-8')
    #     text = str.encode(text)
    #
    #     response.close()
