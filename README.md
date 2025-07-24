# search-portal

I have stopped using Google for Internet search and started using a paid search engine.

I was used to using Google to search for everything, now I want to be more conscious and use more specific search engines when possible.
(For example, I would often use Google to find Wikipedia articles.
Searching directly on Wikipedia should be faster and cheaper.)

However, setting up extra search engines in Firefox is a pain, because [Firefox Sync does not sync search engines](https://bugzilla.mozilla.org/show_bug.cgi?id=444284).
So to add a search engine, I have to add the search engine to all my devices.

This project uses [OpenSearch](OpenSearch (specification)) to scrape the search engines you use and generate a search portal.

The following command generates the HTML for a portal defined by the search engines in the `example.toml` file in this repository:

```console
$ pipx run --spec git+https://github.com/alexpdp7/search-portal search-portal <(curl https://raw.githubusercontent.com/alexpdp7/search-portal/refs/heads/main/example.toml)
```

## TODO

* Sites without OpenSearch, like:
  * https://dle.rae.es
