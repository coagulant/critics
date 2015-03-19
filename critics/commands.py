#!/usr/bin/env python
# coding: utf-8
from functools import partial
import logging

from babel import Locale, UnknownLocaleError, default_locale
import click
import tornado.web
import tornado.httpserver
import tornado.ioloop

from .core import CriticApp
import critics


logger = logging.getLogger('critics')


@click.command()
@click.option('--ios', multiple=True, help='ios app id, e.g. 122434343')
@click.option('--ios-channel', help='Slack channel for ios notifications, optional')
@click.option('--android', multiple=True, help='Android app name, e.g. "com.rovio.angrybirds"')
@click.option('--android-channel', help='Slack channel for android notifications, optional')
@click.option('--language', multiple=True, help='ISO 639-1 languages of review [default: system locale]')
@click.option('--slack-webhook', help='Slack webhook absolute URL, required')
@click.option('--parse-max-entries', default=10, help='Number of feed entries to look into [default: 10]')
@click.option('--beat', default=300, help='Number of seconds between polling feed [default: 300]')
@click.option('--verbose/--short', default=False)
@click.option('--notify/--no-notify', default=True)
@click.option('--persist/--no-persist', default=True)
@click.option('--model', type=click.Path(), default='reviews.json')
@click.option('--daemonize/--run-once', default=True)
@click.option('--version', is_flag=True)
def cli(**settings):
    """Notify about new reviews in AppStore and Google Play in slack.

       Launch command using supervisor or using screen/tmux/etc.
       Reviews are fetched for multiple apps and languages in --beat=300 interval.
    """

    setup_logging(settings)
    settings = setup_languages(settings)
    app = CriticApp(**settings)

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

    echo_channel_map(settings)

    if settings['ios']:
        app.poll_store('ios', notify=notify)
    if settings['android']:
        app.poll_store('android', notify=notify)

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
        try:
            settings['language'] = [default_locale()[:2]]
        except ValueError:
            settings['language'] = ['en']

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


def echo_channel_map(settings):
    if not settings['slack_webhook']:
        return
    channel_map = ''
    if settings['ios'] and settings['ios_channel']:
        channel_map += ' IOS -> %s  ' % settings['ios_channel']
    if settings['android'] and settings['android_channel']:
        channel_map += ' Android -> %s' % settings['android_channel']
    if channel_map:
        logger.info('Transport: slack channels:%s' % channel_map)
