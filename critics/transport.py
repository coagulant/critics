# coding: utf-8
import json
import datetime
import math

from babel.dates import format_datetime
import requests

from .i18n import get_language, get_locale


locale = get_locale()
language = get_language()
_ = language.ugettext


def post2slack(reviews, slack_url, channel):
    emoji = {
        1: ':feelsgood:',
        2: ':finnadie:',
        3: ':hurtrealbad:',
        4: ':suspect:',
        5: ':godmode:',
    }
    colors = {
        1: '#CC2525',
        2: '#CC2525',
        3: '#E8AD0C',
        4: '#30E80C',
        5: '#30E80C',
    }
    stars = {
        1: u'★☆☆☆☆',
        2: u'★★☆☆☆',
        3: u'★★★☆☆',
        4: u'★★★★☆',
        5: u'★★★★★'
    }

    if not reviews:
        return

    def get_date_string(date):
        if isinstance(date, datetime.datetime):
            return format_datetime(date, 'd MMMM yyyy hh:mm', locale=get_locale())
        else:
            return date

    average_rating = int(math.floor(sum(review.rating for review in reviews) / float(len(reviews))))
    platform = reviews[0].platform

    store = _('AppStore') if platform == 'ios' else _('Google Play')
    template = language.ungettext('There is %(num)d new review in %(store)s',
                                  'There are %(num)d new reviews in %(store)s', len(reviews))
    text = template % {'num': len(reviews), 'store': store}

    payload = {
        'attachments': [{
            'color': colors[review.rating],
            'title': review.title or u'-',
            'title_link': review.url,
            'text': u'{stars}\n{summary}\n\n_{author}_, {date} {version}'.format(
                stars=stars[review.rating],
                summary=review.summary,
                author=review.author,
                date=get_date_string(review.date),
                version=u'[%s]' % review.version if review.version else ''
            ),
            "mrkdwn_in": ["text"],
        } for review in reviews],
        'text': text,
        'username': _('Critic'),
        "icon_emoji": emoji[average_rating],
    }
    if channel:
        payload['channel'] = channel

    requests.post(slack_url, data={'payload': json.dumps(payload)})
