import re
from urllib.parse import urlparse

def scraper(url: str, resp) -> list:
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def tokenize_html(html_content: str) -> list:
	valid_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~:/?#[]@!$&'()*+,;="
	res = []

	token = ""
	#token will be a variable where valid characters will be
	#concatenated up until there is an invalid character

	for char in html_content:
		#going through every character preset in the word that is
		#currently being looked at, O(n) time complexity
		if char in valid_characters:
			#if the character that is currently being looked at is
			#an alphanumeric character then execute this if
			token += char
		else:
			if not token == "":
				res.append(token)
				token = ""

	for i in res:
		print(i)	


	return res

def extract_next_links(url: str, resp):
	if type(resp) == None: return []
	return tokenize_html(resp.raw_response.text)


def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
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
        print ("TypeError for ", parsed)
        raise


