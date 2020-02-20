from threading import Thread
from _collections import defaultdict

from utils.download import download
from utils import get_logger
from scraper import scraper
import time

from urllib.parse import urlparse
import operator
from nltk.corpus import stopwords

# Functions below will be functions used for final report
# ------------------------------------------------------------------------#


"""" 1. How many unique pages did you find? Uniqueness is established by the URL, but discarding the fragment part. 
 So, for example, http://www.ics.uci.edu#aaa and http://www.ics.uci.edu#bbb are the same URL."""


def unique_pages(url_list):
    # # url_list is a list of the urls we have crawled
    # unique_netlocs = set()
    # for link in url_list:
    #     # adds the unique domains into unique_netlocs
    #     unique_netlocs.add(urlparse(link)[1])
    # # returns the len() of the set which is the amount of unique pages present
    return len(url_list)


""" 2. What is the longest page in terms of number of words? (HTML markup doesn’t count as words)"""


def longest_page(d):
    # dict will be a dictionary that has the url as the key and it's value will be the len() of the extract text function
    return max(d.keys(), key=(lambda key: len(d[key])))


""" 3. What are the 50 most common words in the entire set of pages? (Ignore English stop words, which can be found, 
for example, here (Links to an external site.)) Submit the list of common words ordered by frequency."""


def fifty_most_common_words(d):
    stop_words = set(stopwords.words('english'))
    return [word[0] for word in sorted(d.items(), key=operator.itemgetter(1), reverse=True) if not word in stop_words][:50]


""" 4. How many subdomains did you find in the ics.uci.edu domain? Submit the list of subdomains ordered alphabetically 
and the number of unique pages detected in each subdomain. The content of this list should be lines containing URL, 
number, for example: http://vision.ics.uci.edu, 10 (not the actual number here)"""


def ics_subdomain_frequencies(url_list):
    netloc = "ics.uci.edu"
    lst = defaultdict(int)
    for link in url_list:
        if netloc in urlparse(link)[1]:
            lst[urlparse(link)[1]] += 1
    return [(sub, freq) for sub, freq in sorted(lst.items(), key=lambda x: x[0])]


#---------------------------------------------------------------------------------------------


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        super().__init__(daemon=True)

    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            # if there is a url to download on the frontier
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            # put the response = download into a try except, in case there is a timeout
            # and resp doesn't equal anything
            resp = download(tbd_url, self.config, self.logger)

            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")

            # after getting the response from the webpage, the function will
            # store the information in the self.frontier
            self.frontier.store_page_text_content(resp, tbd_url)

            scraped_urls = scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)

        self.frontier.close_files()

        print("number of unique pages is:", unique_pages(self.frontier.discovered_urls))
        print("longest page is:", longest_page(self.frontier.site_content))
        print("fifty most common words are here:",fifty_most_common_words(self.frontier.word_frequencies))
        print(ics_subdomain_frequencies(self.frontier.discovered_urls))
        #
        # print("just in case here are all the urls that were discovered", self.frontier.discovered_urls, "\n")
        # print("and here are all the words and their frequencies", self.frontier.word_frequencies)




