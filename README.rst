=======
critics
=======

.. image:: https://img.shields.io/travis/coagulant/critics.svg
        :target: https://travis-ci.org/coagulant/critics

.. image:: https://img.shields.io/coveralls/coagulant/critics.svg
    :target: https://coveralls.io/r/coagulant/critics

.. image:: https://img.shields.io/pypi/v/critics.svg
        :target: https://pypi.python.org/pypi/critics

.. image:: https://img.shields.io/badge/licence-BSD-blue.svg

.. image:: https://img.shields.io/badge/status-beta-yellow.svg

::

    Usage: critics [OPTIONS]

      Notify about new reviews in AppStore and Google Play in slack.

      Launch command using supervisor or using screen/tmux/etc. Reviews are
      fetched for multiple apps and languages in --beat=300 interval.

    Options:
      --ios TEXT                   ios app id, e.g. 122434343
      --ios-channel TEXT           Slack channel for ios notifications, optional
      --android TEXT               Android app name, e.g. "com.rovio.angrybirds"
      --android-channel TEXT       Slack channel for android notifications, optional
      --language TEXT              ISO 639-1 languages of review [default: system locale]
      --slack-webhook TEXT         Slack webhook absolute URL, required
      --parse-max-entries INTEGER  Number of feed entries to look into [default: 10]
      --beat INTEGER               Number of seconds between polling feed [default: 300]
      --verbose / --short
      --notify / --no-notify
      --persist / --no-persist
      --model PATH
      --daemonize / --run-once
      --version
      --help                       Show this message and exit.


Examples
~~~~~~~~

Track English and Russian reviews for iOS and Android Angry Birds apps
and post them to separate channels::

    critics --ios=343200656 --android=com.rovio.angrybirds \
            --slack-webhook=YOUR_SLACK_WEBHOOK_URL \
            --language=en --language=ru \
            --ios-channel="#ios_reviews" --android-channel="#android_reviews"

Previous command, but using env variables::

    CRITICS_IOS=343200656 CRITICS_ANDROID=com.rovio.angrybirds \
    CRITICS_SLACK_WEBHOOK=YOUR_SLACK_WEBHOOK_URL CRITICS_LANGUAGE="en ru" \
    CRITICS_IOS_CHANNEL="#ios_reviews" CRITICS_ANDROID_CHANNEL="#android_reviews" \
    critics

For demo purpose (does not require slack): parse ios feed for MyBook app
and print reviews in stdout::

    critics --ios=556540446 --run-once --no-notify --no-persist --verbose


How it looks
~~~~~~~~~~~~

.. image:: https://github.com/coagulant/critics/raw/master/docs/screenshots/screenshot_01.png
   :height: 356 px
   :width: 492 px
   :alt: Heroes HD Android reviews
