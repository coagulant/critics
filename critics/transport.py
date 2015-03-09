# coding: utf-8
import json
import datetime
import math
from pytils import numeral
from pytils.dt import ru_strftime
import requests


def post2slack(reviews, slack_url, channel, bot_name=u'Critic'):
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
            return ru_strftime('%d %B %Y %H:%m', review.date)
        else:
            return date

    noun = numeral.choose_plural(len(reviews), (u'новый отзыв', u'новых отзыва', u'новых отзывов'))
    average_rating = int(math.floor(sum(review.rating for review in reviews) / float(len(reviews))))
    platform = reviews[0].platform
    text = u'В {store} {num_reviews} {noun}'.format(
        store=u'AppStore' if platform == 'ios' else 'Google Play',
        num_reviews=len(reviews),
        noun=noun)

    payload = {
        'attachments': [{
            'color': colors[review.rating],
            'title': review.title or '-',
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
        'username': bot_name,
        "icon_emoji": emoji[average_rating],
    }
    if channel:
        payload['channel'] = channel

    # print payload
    requests.post(slack_url, data={'payload': json.dumps(payload)})
