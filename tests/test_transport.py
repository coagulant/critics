# coding: utf-8
import json
import datetime

from critics.i18n import get_language, get_locale
from critics.parsers import Review
from critics.transport import post2slack


try:
    from urllib.parse import parse_qs
except ImportError:
    from urlparse import parse_qs

import responses


def patch_locale(monkeypatch, lang):
    monkeypatch.setenv('LANGUAGE', lang)
    monkeypatch.setattr('critics.transport.language', get_language())
    monkeypatch.setattr('critics.transport._', get_language().ugettext)
    monkeypatch.setattr('critics.transport.locale', get_locale())


@responses.activate
def test_slack(monkeypatch):
    patch_locale(monkeypatch, 'en')
    responses.add(responses.POST, 'http://slack.hook/')

    post2slack([Review(
        id=u'gp:AOqpTOGVTpUWQyZJhCbF6dpGfgWnmaj992am2upoCj8Iur1YoNKubAlN_W_BzRYHGh7pdxAe-HDIdOUEvaRfpw',
        platform='android',
        title=u'',
        rating=1,
        summary=u'dffdf\nfgf4tt',
        url=u'http://www',
        author=u'Someauthor',
        date=datetime.datetime(2015, 1, 1, 6),
        language='ru',
        version=None
    )], 'http://slack.hook/', channel=None)

    assert json.loads(parse_qs(responses.calls[0].request.body)['payload'][0]) == {
        u'username': u'Critic',
        u'text': u'There is 1 new review in Google Play',
        u'attachments': [{
            u'color': u'#CC2525',
            u'text': u'★☆☆☆☆\ndffdf\nfgf4tt\n\n_Someauthor_, 1 January 2015 06:00 ',
            u'title_link': u'http://www',
            u'mrkdwn_in': [u'text'],
            u'title': u'-'}
        ],
        u'icon_emoji': u':feelsgood:'}


@responses.activate
def test_slack_locale(monkeypatch):
    patch_locale(monkeypatch, 'ru')
    responses.add(responses.POST, 'http://slack.hook/')

    post2slack([Review(
        id=u'34e56344☃',
        platform='ios',
        title=u'Great app! ♡',
        rating=5,
        summary=u'NOO̼O​O NΘ stop the an​*̶͑̾̾​̅ͫ͏̙̤g͇̫͛͆̾ͫ̑͆l͖͉̗̩̳̟̍ͫͥͨ',
        url=u'http://www',
        author=u'Here comes more BS',
        date=datetime.datetime(2015, 1, 1, 6),
        language=None,
        version='2.1.3'
    )], 'http://slack.hook/', channel=None)

    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == 'http://slack.hook/'
    assert json.loads(parse_qs(request.body)['payload'][0]) == {
        u'username': u'Критик',
        u'text': u'В AppStore 1 новый отзыв',
        u'attachments': [{
            u'color': u'#30E80C',
            u'text': u'★★★★★\nNOO̼O​O NΘ stop the an​*̶͑̾̾​̅ͫ͏̙̤g͇̫͛͆̾ͫ̑͆l͖͉̗̩̳̟̍ͫͥͨ\n\n_Here comes more BS_, 1 января 2015 06:00 [2.1.3]',  # noqa
            u'title_link': u'http://www',
            u'mrkdwn_in': [u'text'],
            u'title': u'Great app! \u2661'}
        ],
        u'icon_emoji': u':godmode:'}
