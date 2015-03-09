# coding: utf-8
from click.testing import CliRunner

from critics.commands import cli


def test_args(tmpdir):
    runner = CliRunner()
    result = runner.invoke(cli, ['--ios', '343200656',
                                 '--android', 'com.rovio.angrybirds',
                                 '--model', tmpdir.join("reviews.json").strpath,
                                 '--run-once'],
                           env={'CRITICS_SLACK_WEBHOOK': 'http://httpbin.org/post',
                                'CRITICS_IOS_CHANNEL': 'ios',
                                'CRITICS_ANDROID_CHANNEL': 'android'},
                           auto_envvar_prefix='CRITICS')
    print(result.exception)
    assert result.exit_code == 0
    assert result.output == ('Tracking IOS apps: 343200656\n'
                             'Tracking Android apps: com.rovio.angrybirds\n'
                             'Transport: slack channels: IOS -> ios   Android -> android\n'
                             'ios: Fetched 0 reviews, 0 new\n'
                             'android: Fetched 10 reviews, 10 new\n')
