# coding: utf-8
from collections import namedtuple
import json
import datetime
import logging
import os
import re
from time import mktime

import feedparser
import requests
from lxml import html

from .compat import python_2_unicode_compatible


logger = logging.getLogger('critics')
timeout = os.environ.get('CRITICS_TIMEOUT', 5)


@python_2_unicode_compatible
class Review(namedtuple('Review',
                        ['id', 'platform', 'title', 'rating', 'summary', 'url',
                         'author', 'date', 'language', 'version'])):
    __slots__ = ()

    def __str__(self):
        return (u'Review (%s):\ntitle=%s\nrating=%s\nsummary=%s\nurl=%s\n'
                u'author=%s\ndate=%s\nlanguage=%s\nversion=%s' % (
                    self.id,
                    self.title,
                    self.rating,
                    self.summary,
                    self.url,
                    self.author,
                    self.date,
                    self.language,
                    self.version
                ))


def get_ios_reviews(app_id, language, limit=100):
    url = 'https://itunes.apple.com/%(language)srss/customerreviews/id=%(app_id)s/sortBy=mostRecent/xml' % {
        'language': '%s/' % language if language else '', 'app_id': app_id}
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'},
                            timeout=timeout)
    response.encoding = 'utf-8'  # avoid chardet not guessing correctly
    feed = feedparser.parse(response.text)
    reviews = [Review(
        id=entry.id,
        platform='ios',
        title=entry.title,
        rating=int(entry.im_rating),
        summary=entry.summary,
        url=entry.href,
        author=entry.author,  # author url: entry.href
        date=datetime.datetime.fromtimestamp(mktime(entry.updated_parsed)),
        language=language,
        version=entry.im_version
    ) for entry in feed['entries'][1:1 + limit]]
    return reviews


def get_android_reviews(app_id, language, limit=100):
    url = 'https://play.google.com/store/getreviews'
    payload = {'xhr': 1, 'id': app_id, 'reviewSortOrder': 0, 'pageNum': 0, 'reviewType': 0}
    if language:
        payload['hl'] = language
    response = requests.post(url, data=payload, timeout=timeout)
    json_source = response.text[response.text.find('['):]
    response_as_json = json.loads(json_source)
    try:
        response_as_html = response_as_json[0][2]
    except IndexError:
        logger.error('Unexpected json for app_id=%s', app_id)
        return []

    utf8_parser = html.HTMLParser(encoding='utf-8')
    doc = html.fromstring(response_as_html.encode('utf-8'), parser=utf8_parser)
    reviews_html = doc.cssselect('.single-review')

    def get_rating_from_html(review_html):
        star_style = review_html.cssselect('.current-rating')[0].get('style')  # e.g. 'width: 20%'
        return int(re.search('(\d+)%', star_style).group(1)) / 20

    reviews = [Review(
        id=review_html.cssselect('.review-header')[0].get('data-reviewid'),
        platform='android',
        title=review_html.cssselect('.review-body .review-title')[0].text_content().strip(),
        rating=get_rating_from_html(review_html),
        summary=review_html.cssselect('.review-body .review-title')[0].tail.strip(),
        url='https://play.google.com' + review_html.cssselect('.reviews-permalink')[0].get('href'),
        author=review_html.cssselect('.review-header .author-name')[0].text_content().strip(),
        date=review_html.cssselect('.review-header .review-date')[0].text_content().strip(),
        language=language,
        version=None
    ) for review_html in reviews_html[:limit]]
    return reviews
