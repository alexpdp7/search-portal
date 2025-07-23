import urllib.parse

import bs4
import httpx


def find_search_on_url(url):
    """
    >>> find_search_on_url("https://eu.wikipedia.org")
    'https://eu.wikipedia.org/w/rest.php/v1/search'
    """
    html = httpx.get(url, follow_redirects=True)
    return find_search_on_html(html, url)


def find_search_on_html(s: str, base_url):
    link = bs4.BeautifulSoup(s, features="lxml").find("link", attrs={"rel": "search"})
    href = link.attrs["href"]
    href = urllib.parse.urlparse(href)
    base_url = urllib.parse.urlparse(base_url)

    return urllib.parse.urlunparse(
        href._replace(
            scheme=href.scheme or base_url.scheme, netloc=href.netloc or base_url.netloc
        )
    )
