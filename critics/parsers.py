# coding: utf-8
from collections import namedtuple
import json
import datetime
import logging
import re
from time import mktime

import feedparser
import requests
from lxml import html

from .compat import python_2_unicode_compatible


logger = logging.getLogger('critics')


@python_2_unicode_compatible
class Review(namedtuple('Review',
                        ['id', 'platform', 'title', 'rating', 'summary', 'url', 'author', 'date', 'version'])):
    __slots__ = ()

    def __str__(self):
        return (u'Review (%s):\ntitle=%s\nrating=%s\nsummary=%s\nurl=%s\nauthor=%s\ndate=%s\nversion=%s' % (
            self.id,
            self.title,
            self.rating,
            self.summary,
            self.url,
            self.author,
            self.date,
            self.version
        ))


def get_ios_reviews(app_id, limit=100):
    url = 'https://itunes.apple.com/ru/rss/customerreviews/id=%s/sortBy=mostRecent/xml' % app_id
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'},
                            timeout=1)
    feed = feedparser.parse(response.text)
    reviews = [Review(
        id=entry.id,
        platform='ios',
        title=entry.title,
        rating=int(entry.im_rating),
        summary=entry.summary,
        url=entry.links[0].href,
        author=entry.author,  # author url: entry.href
        date=datetime.datetime.fromtimestamp(mktime(entry.updated_parsed)),
        version=entry.im_version
    ) for entry in feed['entries'][1:1 + limit]]
    return reviews


def get_android_reviews(app_id, limit=100):
    url = 'https://play.google.com/store/getreviews'
    response = requests.post(url, data={'xhr': 1, 'id': app_id, 'reviewSortOrder': 0, 'pageNum': 0, 'reviewType': 0},
                             timeout=1)
    json_source = response.text[response.text.find('['):]
    response_as_json = json.loads(json_source)
    try:
        response_as_html = response_as_json[0][2]
    except IndexError:
        logger.error('Unexpected json for app_id=%s', app_id)
        return []
    doc = html.fromstring(response_as_html)
    reviews_html = doc.cssselect('.single-review')

    def get_rating_from_html(review_html):
        string = review_html.cssselect('.star-rating-non-editable-container')[0].get('aria-label')
        return int(re.search('(\d).+(\d)', string).group(1))

    reviews = [Review(
        id=review_html.cssselect('.review-header')[0].get('data-reviewid'),
        platform='android',
        title=review_html.cssselect('.review-body .review-title')[0].text_content().strip(),
        rating=get_rating_from_html(review_html),
        summary=review_html.cssselect('.review-body .review-title')[0].tail.strip(),
        url='https://play.google.com' + review_html.cssselect('.reviews-permalink')[0].get('href'),
        author=review_html.cssselect('.review-header .author-name')[0].text_content().strip(),
        date=review_html.cssselect('.review-header .review-date')[0].text_content().strip(),
        version=None
    ) for review_html in reviews_html[:limit]]
    return reviews
