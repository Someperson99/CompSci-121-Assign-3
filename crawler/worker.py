from threading import Thread

from utils.download import download
from utils import get_logger
from scraper import scraper
import time


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
            self.frontier.store_page_text_content(resp.raw_response, tbd_url)

            scraped_urls = scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)