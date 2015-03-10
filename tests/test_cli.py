# coding: utf-8
import json

from click.testing import CliRunner

from critics.commands import cli


def test_args(tmpdir):
    model = tmpdir.join("reviews.json")
    runner = CliRunner()
    result = runner.invoke(cli, ['--ios', '343200656',
                                 '--android', 'com.rovio.angrybirds',
                                 '--model', model.strpath,
                                 '--run-once'],
                           env={'CRITICS_SLACK_WEBHOOK': 'http://httpbin.org/post',
                                'CRITICS_IOS_CHANNEL': 'ios',
                                'CRITICS_ANDROID_CHANNEL': 'android'},
                           auto_envvar_prefix='CRITICS')
    print(result.exception)
    assert result.exit_code == 0

    # iOS rss feed returns either 10 or 0 reviews - probably a bug on Apple side,
    # sometimes the feed is just empty.
    num_reviews = len(json.loads(model.read())['ios']['value'])

    assert num_reviews in [0, 10]
    assert result.output == ('Tracking IOS apps: 343200656\n'
                             'Tracking Android apps: com.rovio.angrybirds\n'
                             'Transport: slack channels: IOS -> ios   Android -> android\n'
                             'ios: Fetched %s reviews, %s new\n' % (num_reviews, num_reviews) +
                             'android: Fetched 10 reviews, 10 new\n')
