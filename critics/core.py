import os
import json
import logging
import tornado.web
from .parsers import get_android_reviews, get_ios_reviews
from .transport import post2slack


logger = logging.getLogger('critics')


class CriticApp(tornado.web.Application):

    def __init__(self, *args, **kwargs):
        super(CriticApp, self).__init__(*args, **kwargs)
        self.reviews = {
            'android': set(),
            'ios': set(),
        }
        # self.model_file = 'reviews.json'
        self.fetchers = {
            'android': get_android_reviews,
            'ios': get_ios_reviews
        }
        self.notifiers = {
            'slack': post2slack
        }

    def poll_store(self, platform, notify=True):
        for app_id in self.settings.get(platform):
            for language in self.settings['language']:
                self.poll_store_single_app(platform, app_id, language, notify)

    def poll_store_single_app(self, platform, app_id, language, notify):
        if platform not in self.fetchers.keys():
            raise Exception('Unknown platform %s', platform)
        fetcher = self.fetchers[platform]

        new_reviews = []
        parsed_review_ids = self.reviews[platform]
        logging.debug('parsed_review_ids = %s', parsed_review_ids)
        reviews = fetcher(app_id=app_id,
                          language=language,
                          limit=self.settings.get('parse_max_entries', None))
        for review in reviews:
            if review.id in parsed_review_ids:
                continue
            logger.debug(review)
            parsed_review_ids.add(review.id)
            new_reviews.append(review)

        logger.info('%(platform)s: %(app_id)s: %(language)s: Fetched %(num_reviews)s reviews, %(new_reviews)s new',
                    {'platform': platform, 'app_id': app_id, 'language': language,
                     'num_reviews': len(reviews), 'new_reviews': len(new_reviews)})

        if new_reviews:
            self.send_messages(new_reviews, platform, notify)

    def send_messages(self, new_reviews, platform, notify):
        self.save_model()
        channel = self.settings.get('%s_channel' % platform, None)
        if not notify:
            logger.debug('%s: Skip notification on first run', platform)
        elif not self.settings.get('notify', True):
            logger.debug('%(platform)s: Faking %(num)s notifications to %(channel)s', {
                'platform': platform, 'num': len(new_reviews), 'channel': channel
            })
        else:
            self.notifiers['slack'](new_reviews, self.settings['slack_webhook'], channel)
            logging.debug(new_reviews)

    def load_model(self):
        if not self.settings['persist']:
            return False
        if os.path.exists(self.settings['model']):
            logger.debug('Loading state')
            try:
                with open(self.settings['model']) as fp:
                    self.reviews = json.load(fp, object_hook=as_set)
            except Exception as e:
                logger.error('Problem loading prev. results from file: %s', e)
            else:
                return True
        return False

    def save_model(self):
        if not self.settings['persist']:
            return False
        logger.debug('Saving state')
        try:
            json.dump(self.reviews, open(self.settings['model'], 'w'), cls=SetEncoder, indent=4)
        except Exception as e:
            logger.error('Problem saving results to file: %s', e)
            return False
        else:
            return True


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return {'python_object': 'set', 'value': list(obj)}
        return json.JSONEncoder.default(self, obj)


def as_set(dct):
    if 'python_object' in dct:
        return set(dct['value'])
    return dct
