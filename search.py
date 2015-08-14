""" Copyright 2015 Noel Niles <noelniles@gmail.com>

    This file is part of Pybrarian.

    Pybrarian is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Pybrarian.  If not, see <http://www.gnu.org/licenses/>.
"""
import time
import requests
from urllib import parse
from bs4 import BeautifulSoup


class SearchResult():
    def __init__(self):
        self.name = None  # The title of the link
        self.link = None  # The external link
        self.google_link = None  # The google link
        self.description = None  # The description of the link
        self.page = None  # Results page this one was on
        self.index = None  # What index on this page it was on
    
    def __repr__(self):
        name = '\n\nname: {}'.format(self.name)
        link = 'link: {}'.format(self.link)
        glink = 'Google Link: {}'.format(self.google_link)
        return '\n'.join([name, link, glink])


def measure_time(fn):
    def decorator(*args, **kwargs):
        start = time.time()
        result = fn(*args, **kwargs)
        elapsed = time.time() - start
        print('{0} took {1} seconds.'.format(fn.__name__, elapsed))
        return result
    return decorator

def trim_query(query):
    return (query.strip()
        .replace(':', '%3A')
        .replace('+', '%2B')
        .replace('&', '%26')
        .replace(' ', '+')
        )

def google_search_url(query, page=0, per_page=10):
    srch_url = 'https://www.google.com/search?hl=en&q=%s&start=%i&num=%i'
    q = trim_query(query)
    return  srch_url % (q, page * per_page, per_page)

def google_html(url):
    try:
        headers = { 
            'user-agent':'Mozilla/5.001 (windows; U; NT4.0; en-US; rv:1.0) '
            +'Gecko/25250101'
                }
        html = requests.get(url, headers=headers) 
        return html.text
    except:
        print('Error accessing: ', url)
        return None

def get_name(li):
    a = li.find('a')
    return a.text.strip()

def get_link(li):
    a = li.find("a")
    link = a["href"]
    if link.startswith("/url?") or link.startswith("/search?"):
        return link.replace('/url?q=', '')
    else:
        return None

def google_link(li):
    a = li.find("a")
    link = a["href"]
    if link.startswith("/url?") or link.startswith("/search?"):
        return parse.urljoin("http://www.google.com", link)
    else:
        return None

def search(query, pages=1):
    search_results = []
    for i in range(pages):
        url = google_search_url(query)
        html = google_html(url)
        j = 0
        if html:
            soup = BeautifulSoup(html, "html.parser")
            lis = soup.findAll("li", attrs={"class": "g"})
            for li in lis:
                res = SearchResult()
                res.page = i
                res.index = j
                res.name = get_name(li)
                res.link = get_link(li)
                res.google_link = google_link(li)
                search_results.append(res)
                j += 1
    return search_results

@measure_time
def test_measure_time():
    for i in range(10):
        time.sleep(.1)

def test_link_alive(url):
    resp = requests.head(url)
    status = resp.status_code
    if status != 200:
        print('ERROR BAD LINK STATUS: ', status)
        return False
    return True

def test_trim_query():
    q = ' :+ & '
    correct = '%3A%2B+%26'
    test = trim_query(q)
    print('test trim_query: ', test)
    assert test == correct

def test_search():
    q = 'dogs'
    res = search(q)
    for i in res:
        print('link: ', res)

def test_google_search_url():
    q = 'linux'
    search_url = google_search_url('q')
    assert test_link_alive(search_url) == True


if __name__ == '__main__':
    test_measure_time()
    test_trim_query()
    test_google_search_url()
    test_search()


