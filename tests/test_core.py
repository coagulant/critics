# coding: utf-8
import json
from mock import Mock
from critics.core import CriticApp
from critics.parsers import Review


def test_poll_store(tmpdir):
    fakemodel = tmpdir.join("fakemodel.json")
    app = CriticApp(ios=['app1', 'app2'], language=['ru'], persist=True, slack_webhook='http://www')
    app.model_file = fakemodel.strpath
    fake_fetcher = Mock(return_value=[Review(
        id=u'xfkew4ytwqqddid:2e22wdad',
        platform='ios',
        title=u'Great app! ♡',
        rating=2,
        summary=u'Here be\nDragons!',
        url=u'http://www',
        author=u'Here comes more BS',
        date='bull',
        language='en',
        version=None
    )])
    app.fetchers['ios'] = fake_fetcher
    fake_notifier = Mock()
    app.notifiers['slack'] = fake_notifier
    app.poll_store(platform='ios')

    assert fake_fetcher.call_count == 2
    assert fake_notifier.call_count == 1
    assert len(app.reviews['ios']) == 1

    fake_fetcher.reset_mock()
    fake_notifier.reset_mock()
    app.poll_store(platform='ios')
    assert fake_fetcher.call_count == 2
    assert fake_notifier.call_count == 0
    assert len(app.reviews['ios']) == 1


def test_load_model():
    app = CriticApp(persist=False)
    assert not app.load_model()
    assert app.reviews['ios'] == set()
    assert app.reviews['android'] == set()

    app = CriticApp(persist=True, model='tests/fixtures/model.json')
    assert app.load_model()
    assert app.reviews['ios'] == {'123'}
    assert app.reviews['android'] == {'xxx', 'yyyy'}


def test_save_model(tmpdir):
    fakemodel = tmpdir.join("fakemodel.json")
    app = CriticApp(persist=False)

    assert not app.save_model()
    assert not fakemodel.check()

    app = CriticApp(persist=True, model=fakemodel.strpath)

    assert app.save_model()
    assert fakemodel.check()
    assert json.load(fakemodel) == {'android': {'python_object': 'set', 'value': []},
                                    'ios': {'python_object': 'set', 'value': []}}

    app.reviews['ios'].add('678')
    app.reviews['android'].add('qqq')
    assert app.save_model()
    assert fakemodel.check()
    assert json.load(fakemodel) == {'android': {'python_object': 'set', 'value': ['qqq']},
                                    'ios': {'python_object': 'set', 'value': ['678']}}
