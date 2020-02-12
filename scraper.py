import re
from urllib.parse import urlparse
import urllib.robotparser as RFP
from bs4 import BeautifulSoup

viable_links = ["ics.uci.edu", "cs.uci.edu",
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
    if not robot_allow(url): return []
    asdf = input()
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def tokenize_html(html_content: str) -> list:
    res = []

    soup = BeautifulSoup(html_content, features='html.parser')
    links = soup.findAll('a')

    for link in links:
        href_attr = link.get('href')
        if is_valid(href_attr):
            for i in viable_links:
                if i in href_attr:
                    res.append(href_attr)
                    break
    return res


def extract_next_links(url: str, resp):
    if type(resp) is None:
        return []
    if resp.status not in range(100, 300):
        return []
    # print(resp.raw_response.text)
    return tokenize_html(resp.raw_response.text)


def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print("TypeError for ", parsed)
        raise

# res = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', html_content)

# regex = "\.(css|js|bmp|gif|jpe?g|ico|png|tiff?|mid|mp2|mp3|mp4|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf|ps|eps|tex
# |ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|shal|thmx|mso|arff
# |rtf|jar|csv|rm|smil|wmv|swf|wma|zip|rar|gz)$"

# print("\n\n")
