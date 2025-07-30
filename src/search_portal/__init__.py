import argparse
import pathlib
import tomllib
import urllib.parse
from xml.etree import ElementTree

import bs4
import htmlgenerator
import httpx


def opensearch_from_url(url):
    try:
        return OpenSearch(httpx.get(find_search_on_url(url)).read())
    except:
        pass
    try:
        return OpenSearch(httpx.get(url).read())
    except:
        pass
    raise Exception(f"could not find opensearch on {url}")


def find_search_on_url(url):
    """
    >>> find_search_on_url("https://eu.wikipedia.org")
    'https://eu.wikipedia.org/w/rest.php/v1/search'
    """
    html = httpx.get(url, follow_redirects=True)
    return find_search_on_html(html, url)


def find_search_on_html(s: str, base_url):
    html = bs4.BeautifulSoup(s, features="html.parser")
    link = html.find("link", attrs={"rel": "search"})
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

    def html_form(self):
        search = self.urls["text/html"]
        url = search.template
        url = urllib.parse.urlparse(url)
        query = url.query
        query = urllib.parse.parse_qs(query)
        search_term_parameters = [
            parameter
            for parameter, value in query.items()
            if value[0] == "{searchTerms}"
        ]
        assert len(search_term_parameters) == 1, (
            f"parameter with {{searchTerms}} not found in {query}"
        )
        search_term_parameter = search_term_parameters[0]
        other_inputs = [
            htmlgenerator.INPUT(name=parameter, value=value[0], _type="hidden")
            for parameter, value in query.items()
            if parameter != search_term_parameter
        ]
        return htmlgenerator.FORM(
            htmlgenerator.LABEL(
                self.short_name,
                htmlgenerator.INPUT(
                    name=search_term_parameter,
                ),
            ),
            *other_inputs,
            htmlgenerator.INPUT(_type="submit"),
            method=search.method.upper(),
            action=url._replace(query=None).geturl(),
        )


class OpenSearchUrl:
    def __init__(self, element):
        self.type_ = element.attrib["type"]
        self.method = element.attrib.get("method", "GET")
        self.template = element.attrib["template"]

    def __repr__(self):
        return repr(self.__dict__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("toml", type=pathlib.Path)
    args = parser.parse_args()

    toml = tomllib.loads(args.toml.read_text())
    search = toml["search"]
    forms = [opensearch_from_url(s).html_form() for s in search]
    print(
        htmlgenerator.render(
            htmlgenerator.HTML(
                htmlgenerator.HEAD(
                    htmlgenerator.META(name="viewport", content="width=device-width, initial-scale=1.0"),
                    htmlgenerator.STYLE(
                        """
                        body {
                          max-width: 40em;
                          margin-left: auto;
                          margin-right: auto;
                          padding-left: 2em;
                          padding-right: 2em;
                          line-height: 1.6em;
                          font-size: 20px;
                        }
                        label, input {
                          display: block;
                          width: 100%;
                          margin-bottom: 1em;
                        }
                        """
                    )
                ),
                htmlgenerator.BODY(*forms),
            ),
            {},
        )
    )
