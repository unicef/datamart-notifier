from datamart_notifier.monitor import monitor
from demoproject.demoapp1 import models as models1
from demoproject.demoapp2 import models as models2


def test_init(db):
    assert monitor.monitored == [models1.Monitored1, models1.Monitored2, models1.Monitored3,
                                 models2.Monitored1, models2.Monitored2, models2.Monitored3,
                                 ]
