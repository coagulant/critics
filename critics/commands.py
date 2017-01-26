#!/usr/bin/env python
# coding: utf-8
from collections import OrderedDict
from functools import partial
import logging
from itertools import chain, repeat

from babel import Locale, UnknownLocaleError
import click
import tornado.web
import tornado.httpserver
import tornado.ioloop
from prometheus_client import start_http_server

from .i18n import get_locale
from .core import CriticApp
import critics


logger = logging.getLogger('critics')


@click.command()
@click.option('--ios', multiple=True, help='ios app id, e.g. 122434343')
@click.option('--ios-channel', multiple=True, help='Slack channel for ios notifications, optional')
@click.option('--android', multiple=True, help='Android app name, e.g. "com.rovio.angrybirds"')
@click.option('--android-channel', multiple=True, help='Slack channel for android notifications, optional')
@click.option('--language', multiple=True, help='ISO 639-1 languages of review [default: system locale]')
@click.option('--slack-webhook', help='Slack webhook absolute URL, required')
@click.option('--parse-max-entries', default=10, help='Number of feed entries to look into [default: 10]')
@click.option('--beat', default=300, help='Number of seconds between polling feed [default: 300]')
@click.option('--verbose/--short', default=False)
@click.option('--notify/--no-notify', default=True)
@click.option('--persist/--no-persist', default=True)
@click.option('--model', type=click.Path(), default='reviews.json')
@click.option('--daemonize/--run-once', default=True)
@click.option('--stats', default=9137, help='Port to serve prometheus stats [default: 9137]')
@click.option('--version', is_flag=True)
def cli(**settings):
    """Notify about new reviews in AppStore and Google Play in slack.

       Launch command using supervisor or using screen/tmux/etc.
       Reviews are fetched for multiple apps and languages in --beat=300 interval.
    """

    setup_logging(settings)
    settings = setup_languages(settings)
    channels = setup_channel_map(settings)
    app = CriticApp(**dict(settings, channels=channels))

    if settings['version']:
        click.echo('Version %s' % critics.__version__)
        return
    if not (settings['ios'] or settings['android']):
        click.echo('Please choose either --ios or --android')
        return

    loop = tornado.ioloop.IOLoop.instance()

    if app.load_model():
        logger.debug('Model loaded OK, not skipping notify on first run')
        notify = True
    else:
        notify = False

    if settings['ios']:
        logger.info('Tracking IOS apps: %s', ', '.join(settings['ios']))
        itunes = tornado.ioloop.PeriodicCallback(partial(app.poll_store, 'ios'),
                                                 1000 * settings['beat'], loop)
        itunes.start()
    if settings['android']:
        logger.info('Tracking Android apps: %s', ', '.join(settings['android']))
        google_play = tornado.ioloop.PeriodicCallback(partial(app.poll_store, 'android'),
                                                      1000 * settings['beat'], loop)
        google_play.start()

    echo_channel_map(channels)

    if settings['ios']:
        app.poll_store('ios', notify=notify)
    if settings['android']:
        app.poll_store('android', notify=notify)

    if settings['stats']:
        port = int(settings['stats'])
        logger.debug('Serving metrics server on port %s' % port)
        start_http_server(port)

    if settings['daemonize']:
        loop.start()


def setup_logging(settings):
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    if settings['verbose']:
        logger.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', "%Y-%m-%d %H:%M:%S"))
    else:
        logger.setLevel(logging.INFO)
    logger.propagate = False


def setup_languages(settings):
    if not settings['language']:
        settings['language'] = [get_locale()[:2]]

    languages = []
    language_names = []
    for lang_code in settings['language']:
        try:
            language_names.append(Locale(lang_code).english_name)
            languages.append(lang_code)
        except UnknownLocaleError:
            raise click.ClickException('Unknown language code: %s' % lang_code)

    logger.info('Languages: %s', ', '.join(language_names))
    return settings


def setup_channel_map(settings):
    channel_map = OrderedDict()
    if not settings['slack_webhook']:
        return channel_map
    if settings['ios'] and settings['ios_channel']:
        channel_map['ios'] = {}
        ios_channels = chain(settings['ios_channel'], repeat(settings['ios_channel'][-1]))
        for app_id, channel in zip(settings['ios'], ios_channels):
            channel_map['ios'][app_id] = channel
    if settings['android'] and settings['android_channel']:
        channel_map['android'] = {}
        android_channels = chain(settings['android_channel'], repeat(settings['android_channel'][-1]))
        for app_id, channel in zip(settings['android'], android_channels):
            channel_map['android'][app_id] = channel
    return channel_map


def echo_channel_map(channel_map):
    if not channel_map:
        return
    channel_output = ''
    for platform, app_mapping in channel_map.items():
        for app_id, channel in app_mapping.items():
            channel_output += '   {app_id} -> {channel}'.format(
                platform=platform, app_id=app_id, channel=channel)
    logger.info('Transport: slack channels:%s' % channel_output)
