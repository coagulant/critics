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

::

    Usage: critics [OPTIONS]
    
      Notify about new reviews in AppStore and Google Play in slack
    
    Options:
      --ios TEXT                   ios app id, e.g. 122434343
      --ios-channel TEXT           Slack channel for ios notifications
      --android TEXT               Android app name, e.g. "com.rovio.angrybirds"
      --android-channel TEXT       Slack channel for android notifications
      --slack-webhook TEXT         Slack webhook absolute URL, required
      --parse-max-entries INTEGER  Number of feed entries to look into
      --beat INTEGER               Number of seconds between polling feed
      --verbose / --short
      --notify / --no-notify
      --persist / --no-persist
      --model PATH
      --daemonize / --run-once
      --version
      --help                       Show this message and exit.


Example
~~~~~~~

::

    critics --ios=343200656 --android=com.rovio.angrybirds --slack-webhook=<SLACK_WEBHOOK_URL> \
            --ios-channel=#ios_reviews --android-channel=#android_reviews
