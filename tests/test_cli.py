# coding: utf-8
import json

from click.testing import CliRunner

from critics.commands import cli


def test_args(tmpdir):
    model = tmpdir.join("reviews.json")
    runner = CliRunner()
    result = runner.invoke(cli, ['--ios', '343200656',
                                 '--android', 'com.rovio.angrybirds',
                                 '--language', 'en', '--language', 'ru',
                                 '--model', model.strpath,
                                 '--run-once'],
                           env={'CRITICS_SLACK_WEBHOOK': 'http://httpbin.org/post',
                                'CRITICS_IOS_CHANNEL': 'ios',
                                'CRITICS_ANDROID_CHANNEL': 'android'},
                           auto_envvar_prefix='CRITICS')
    assert result.exit_code == 0

    # iOS rss feed returns either 10 or 0 reviews - probably a bug on Apple side,
    # sometimes the feed is just empty.
    num_reviews_ios = len(json.loads(model.read())['ios']['value'])
    num_reviews_android = len(json.loads(model.read())['android']['value'])

    assert num_reviews_ios in [0, 20]
    assert num_reviews_android == 20
    assert result.output == ('Languages: English, Russian\n'
                             'Tracking IOS apps: 343200656\n'
                             'Tracking Android apps: com.rovio.angrybirds\n'
                             'Transport: slack channels: IOS -> ios   Android -> android\n'
                             'ios: 343200656: en: Fetched %s reviews, %s new\n' % (num_reviews_ios, num_reviews_ios) +
                             'ios: 343200656: ru: Fetched %s reviews, %s new\n' % (num_reviews_ios, num_reviews_ios) +
                             'android: com.rovio.angrybirds: en: Fetched 10 reviews, 10 new\n'
                             'android: com.rovio.angrybirds: ru: Fetched 10 reviews, 10 new\n')
