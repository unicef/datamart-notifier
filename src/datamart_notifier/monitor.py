import logging
from datetime import datetime
from threading import Thread

import requests
from django.apps import apps
from django.core.cache import caches
from django.db.models.signals import post_save
from django.db.transaction import on_commit
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from . import config

logger = logging.getLogger(__name__)
#
# client = Client(settings.RAVEN_CONFIG['dsn'])

cache = caches['default']
KEY = 'datamart_notifier'


def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504),
                           session=None):
    session = session or requests.Session()
    retry = Retry(total=retries, read=retries, connect=retries,
                  backoff_factor=backoff_factor, status_forcelist=status_forcelist)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def failure():
    dt = datetime.utcnow()
    cache.set(KEY, dt.strftime("%s"))


def success():
    # last_failure = datetime.fromtimestamp(cache.get(KEY))
    dt = datetime.utcnow()
    cache.set(KEY, dt.strftime("%s"))


def check():
    dt = datetime.utcnow()
    cache.set(KEY, dt.strftime("%s"))


class Sender(Thread):
    def __init__(self, tables):
        Thread.__init__(self)
        self.tables = tables
        self.session = Session()
        self.session.auth = (config.USERNAME, config.PASSWORD)

    def run(self):
        try:
            r = requests_retry_session(session=self.session).post(config.WEBHOOK,
                                                                  json={'tables': self.tables},
                                                                  timeout=config.TIMEOUT)
            if r.status_code != 200:
                raise requests.exceptions.HTTPError
        except requests.exceptions.Timeout as e:
            # datamart too slow
            logger.exception(e)
            cache.set('datamart_notifier', 1)
            # client.captureException()
        except requests.exceptions.HTTPError as e:
            # datamart response != 200
            logger.exception(e)
        except ConnectionError as e:
            # DNS failure, refused connection
            logger.exception(e)
        except Exception as e:
            # other
            logger.exception(e)


class Monitor:

    def __init__(self) -> None:
        self.monitored = []
        self.changed_models = set()

        for entry in config.MODELS:
            app_label, model_name = entry.split('.')
            if model_name == '*':
                app_config = apps.get_app_config(app_label)
                self.monitored.extend(app_config.get_models())
            else:
                self.monitored.append(apps.get_model(app_label, model_name))

    def install(self):
        post_save.connect(monitor.on_save, dispatch_uid='datamart_monitor_post_save')

    def on_save(self, sender, **kwargs):
        if sender in self.monitored:
            monitor.changed_models.add(sender)
            on_commit(self.on_commit)

    def on_commit(self):
        if monitor.changed_models:
            tables = set()
            while True:
                try:
                    tables.add(monitor.changed_models.pop()._meta.db_table)
                except KeyError:
                    break
            Sender(list(tables)).start()


monitor = Monitor()
