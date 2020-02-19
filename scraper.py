import re
from urllib.parse import urlparse, urldefrag
import urllib.robotparser as RFP
from bs4 import BeautifulSoup

viable_domains = ["ics.uci.edu", "cs.uci.edu",
                "informatics.uci.edu", "stat.uci.edu",
                "today.uci.edu/department/information_computer_sciences"]

useragent = "IR W20 80993556 63354188"


def robot_allow(url):
    # parses the current url down to the domain and then adds '/robots.txt' to the
    # end of it so that beautifulsoup can view if the current path that the
    # url is going to is allowed
    url_parsed = urlparse(url)
    robots_url = url_parsed.scheme + "://" + url_parsed.netloc + "/robots.txt"

    x = RFP.RobotFileParser()
    x.set_url(robots_url)
    x.read()
    return x.can_fetch(useragent, url)


def scraper(url: str, resp) -> list:
    if resp.status not in range(100,400): return []
    if not robot_allow(url): return []
    # asdf = input()

    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def is_subdomain(url):
    if url.netloc != "today.uci.edu":
        cs_match = r"([a-z]+\.)*cs\.uci\.edu"
        ics_match = r"([a-z]+\.)*ics\.uci\.edu"
        informatics_match = r"([a-z]+\.)*informatics\.uci\.edu"
        stats_match = r"([a-z]+\.)*stats\.uci\.edu"

        if re.match(cs_match, url) or re.match(ics_match, url) or \
            re.match(informatics_match, url) or re.match(stats_match):
            return True
        return False
    else:
        if "/department/information_computer_sciences" in url.path.lower():
            return True

def tokenize_html(html_content: str) -> list:
    '''given a raw_response that is decoded (string) that represents
    html the tokenizer finds all of the links that are in the html string
    and then puts them all into res, removes the fragment of the links'''
    res = []

    soup = BeautifulSoup(html_content, features='html.parser')

    links = soup.findAll('a')

    for link in links:
        href_attr = link.get('href')
        if is_valid(href_attr):
            href_attr = urldefrag(href_attr)
            x = urlparse(href_attr.url)
            if is_subdomain(x):
                res.append(str(href_attr.url))
    return res


def extract_next_links(url: str, resp):
    if type(resp) is None:
        return []
    if resp.status not in range(100, 400):
        return []
    return tokenize_html(resp.raw_response.text)


def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        if "/pdf/" in url:
            return False
        if parsed.netloc in {"http:", "https:"}:
            return False
        if "replytocom" in parsed.query:
            return False


        path_match = not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|ppsx"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)\/*$", parsed.path.lower())

        query_match = path_match = not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|ppsx"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)\/*$", parsed.query.lower())

        date_match = not re.search(r"(\/[0-9][0-9][0-9][0-9]-[0-9][0-9](-[0-9]*)*\/*)$",
                              parsed.path.lower())

        if date_match is False:
            return date_match

        page_match = not re.search(r"/page/([0-9]+\/*)$", parsed.path)

        if "ical=1" in parsed.query.lower():
            return False

        if "share=" in parsed.query.lower():
            return False

        if page_match is False:
            return page_match


        return query_match and path_match

    except TypeError:
        print("TypeError for ", parsed)
        raise