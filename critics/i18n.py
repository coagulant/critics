# coding: utf-8
from os.path import dirname, join, abspath

from babel import default_locale
from babel.support import Translations


translations_dir = abspath(join(dirname(__file__), 'locale'))


def get_locale():
    return default_locale()


def get_language():
    language = Translations.load(translations_dir)
    return language
