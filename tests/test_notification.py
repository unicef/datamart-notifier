from time import sleep

import pytest
import requests.exceptions
import responses
from demoproject.demoapp1.models import Monitored1, Monitored2
from demoproject.demoapp2.models import Ignored1
from django.db.transaction import atomic

from datamart_notifier import config


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.mark.django_db(transaction=True)
def test_base_notification(mocked_responses):
    mocked_responses.add(responses.POST, config.WEBHOOK, body='{}', status=200,
                         content_type='application/json')
    with atomic():
        m = Monitored1()
        m.save()
    sleep(0.1)
    assert mocked_responses.calls[0].request.url == 'https://datamart.unicef.io/hook/update'


@pytest.mark.django_db(transaction=True)
def test_multi_notification(mocked_responses):
    mocked_responses.add(responses.POST, config.WEBHOOK, body='{}', status=200,
                         content_type='application/json')
    with atomic():
        m = Monitored1()
        m.save()
    sleep(0.5)
    with atomic():
        m = Monitored2()
        m.save()
    sleep(0.1)
    assert mocked_responses.calls[0].request.url == 'https://datamart.unicef.io/hook/update'
    assert mocked_responses.calls[0].request.body == b'{"tables": ["demoapp1_monitored1"]}'

    assert mocked_responses.calls[1].request.url == 'https://datamart.unicef.io/hook/update'
    assert mocked_responses.calls[1].request.body == b'{"tables": ["demoapp1_monitored2"]}'


@pytest.mark.django_db(transaction=True)
def test_status_code(mocked_responses):
    mocked_responses.add(responses.POST, config.WEBHOOK, body='{}', status=401,
                         content_type='application/json')
    with atomic():
        m = Monitored1()
        m.save()
    sleep(0.5)
    assert mocked_responses.calls[0].request.url == 'https://datamart.unicef.io/hook/update'
    assert mocked_responses.calls[0].request.body == b'{"tables": ["demoapp1_monitored1"]}'


@pytest.mark.parametrize("exc", [requests.exceptions.Timeout,
                                 requests.exceptions.HTTPError,
                                 ConnectionError,
                                 Exception])
def test_timeout(transactional_db, exc):
    def callback(resp):
        raise exc()

    with responses.RequestsMock(response_callback=callback) as rsps:
        with atomic():
            m = Monitored1()
            m.save()
        sleep(0.1)
        assert rsps.calls[0].request.body == b'{"tables": ["demoapp1_monitored1"]}'


@pytest.mark.django_db(transaction=True)
def test_ignored(mocked_responses):
    with atomic():
        m = Ignored1()
        m.save()
    sleep(0.5)
    assert not mocked_responses.calls
