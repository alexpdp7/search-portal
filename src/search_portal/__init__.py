import urllib.parse
from xml.etree import ElementTree

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
    link = bs4.BeautifulSoup(s, features="html.parser").find(
        "link", attrs={"rel": "search"}
    )
    href = link.attrs["href"]
    href = urllib.parse.urlparse(href)
    base_url = urllib.parse.urlparse(base_url)

    return urllib.parse.urlunparse(
        href._replace(
            scheme=href.scheme or base_url.scheme, netloc=href.netloc or base_url.netloc
        )
    )


class OpenSearch:
    """
    >>> s = OpenSearch(b'<?xml version="1.0"?><OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/" xmlns:moz="http://www.mozilla.org/2006/browser/search/"><ShortName>Wikipedia (eu)</ShortName><Description>Wikipedia (eu)</Description><Image height="16" width="16" type="image/x-icon">https://eu.wikipedia.org/static/favicon/wikipedia.ico</Image><Url type="text/html" method="get" template="https://eu.wikipedia.org/w/index.php?title=Berezi:Bilatu&amp;search={searchTerms}" /><Url type="application/x-suggestions+json" method="get" template="https://eu.wikipedia.org/w/api.php?action=opensearch&amp;search={searchTerms}&amp;namespace=0" /><Url type="application/x-suggestions+xml" method="get" template="https://eu.wikipedia.org/w/api.php?action=opensearch&amp;format=xml&amp;search={searchTerms}&amp;namespace=0" /><moz:SearchForm>https://eu.wikipedia.org/wiki/Berezi:Bilatu</moz:SearchForm></OpenSearchDescription>')
    >>> s.short_name
    'Wikipedia (eu)'
    >>> s.urls
    {'text/html': {'type_': 'text/html', 'method': 'get', 'template': 'https://eu.wikipedia.org/w/index.php?title=Berezi:Bilatu&search={searchTerms}'}, 'application/x-suggestions+json': {'type_': 'application/x-suggestions+json', 'method': 'get', 'template': 'https://eu.wikipedia.org/w/api.php?action=opensearch&search={searchTerms}&namespace=0'}, 'application/x-suggestions+xml': {'type_': 'application/x-suggestions+xml', 'method': 'get', 'template': 'https://eu.wikipedia.org/w/api.php?action=opensearch&format=xml&search={searchTerms}&namespace=0'}}
    """

    def __init__(self, s):
        tree = ElementTree.fromstring(s)
        self.short_name = tree.find(
            "{http://a9.com/-/spec/opensearch/1.1/}ShortName"
        ).text
        self.urls = {
            u.type_: u
            for u in map(
                OpenSearchUrl, tree.findall("{http://a9.com/-/spec/opensearch/1.1/}Url")
            )
        }


class OpenSearchUrl:
    def __init__(self, element):
        self.type_ = element.attrib["type"]
        self.method = element.attrib["method"]
        self.template = element.attrib["template"]

    def __repr__(self):
        return repr(self.__dict__)
