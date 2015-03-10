# coding: utf-8
import json
try:
    from urllib.parse import parse_qs
except ImportError:
    from urlparse import parse_qs

import responses

from critics.parsers import Review
from critics.transport import post2slack


@responses.activate
def test_slack():
    responses.add(responses.POST, 'http://slack.hook/')

    post2slack([Review(
        id=u'34e56344☃',
        platform='ios',
        title=u'Great app! ♡',
        rating=5,
        summary=u'NOO̼O​O NΘ stop the an​*̶͑̾̾​̅ͫ͏̙̤g͇̫͛͆̾ͫ̑͆l͖͉̗̩̳̟̍ͫͥͨ',
        url=u'http://www',
        author=u'Here comes more BS',
        date='whatever',
        version='2.1.3'
    )], 'http://slack.hook/', channel=None)

    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert request.url == 'http://slack.hook/'
    assert json.loads(parse_qs(request.body)['payload'][0]) == {
        u'username': u'Critic',
        u'text': u'В AppStore 1 новый отзыв',
        u'attachments': [{
            u'color': u'#30E80C',
            u'text': u'★★★★★\nNOO̼O​O NΘ stop the an​*̶͑̾̾​̅ͫ͏̙̤g͇̫͛͆̾ͫ̑͆l͖͉̗̩̳̟̍ͫͥͨ\n\n_Here comes more BS_, whatever [2.1.3]',  # noqa
            u'title_link': u'http://www',
            u'mrkdwn_in': [u'text'],
            u'title': u'Great app! \u2661'}
        ],
        u'icon_emoji': u':godmode:'}
