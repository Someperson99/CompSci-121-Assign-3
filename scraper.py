import re
from urllib.parse import urlparse, urldefrag
import urllib.robotparser as RFP
from bs4 import BeautifulSoup

useragent = "IR W20 80993556 63354188"

today_uci_pattern = r"http[s]?:\/\/today\.uci\.edu\/department\/information_computer_sciences"


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
    if not robot_allow(url): return []
    links = extract_next_links(resp)
    return [link for link in links if is_valid(link)]


def is_subdomain(url):
        site_match = r"((www|[a-z]+)\.(cs\.uci\.edu|ics\.uci\.edu|stat\.uci\.edu|informatics\.uci\.edu))"
        new_url = url.netloc

        matching = re.match(site_match, new_url)

        if matching:
            return True
        return False

def tokenize_html(html_content: str) -> list:
    '''given a raw_response that is decoded (string) that represents
    html the tokenizer finds all of the links that are in the html string
    and then puts them all into res, removes the fragment of the links'''
    res = []
    soup = BeautifulSoup(html_content, features='html.parser')
    links = soup.findAll('a')

    for link in links:
        href_attr = urldefrag(link.get('href')).url
        if is_valid(href_attr):
            if re.search(today_uci_pattern, href_attr):
                res.append(str(href_attr))
            else:
                x = urlparse(href_attr)
                if is_subdomain(x):
                    res.append(str(href_attr))
    return res


def extract_next_links(resp):
    if not resp.raw_response:
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

        if not query_match and path_match:
            return False

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

        return True


    except TypeError:
        print("TypeError for ", parsed)
        raise