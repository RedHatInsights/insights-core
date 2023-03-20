import doctest

from insights.parsers import qpid_stat
from insights.tests import context_wrap


QPID_STAT_Q_DOCS = '''
Queues
  queue                                                                      dur  autoDel  excl  msg   msgIn  msgOut  bytes  bytesIn  bytesOut  cons  bind
  ==========================================================================================================================================================
  00d6cc19-15fc-4b7c-af3c-6a38e7bb386d:1.0                                        Y        Y        0     2      2       0    486      486         1     2
  0f7f1a3d-daff-42a6-a994-29050a2eabde:1.0                                        Y        Y        0     8      8       0   4.88k    4.88k        1     2
'''

QPID_STAT_U_DOCS = '''
Subscriptions
  subscr               queue                                                                      conn                                    procName          procId  browse  acked  excl  creditMode  delivered  sessUnacked
  ===========================================================================================================================================================================================================================
  0                    00d6cc19-15fc-4b7c-af3c-6a38e7bb386d:1.0                                   qpid.10.20.1.10:5671-10.20.1.10:33787   celery            21409                        CREDIT      2          0
  0                    pulp.agent.c6a430bc-5ec7-42f8-99ce-f320ed0b9113                            qpid.10.20.1.10:5671-10.30.0.148:57423  goferd            32227           Y            CREDIT      0          0
  1                    server.example.com:event                                                   qpid.10.20.1.10:5671-10.20.1.10:33848   Qpid Java Client  21066           Y      Y     WINDOW      2,623      0
  0                    celeryev.4c77bd03-1cde-49eb-bdc0-b7c38f9ff93d                              qpid.10.20.1.10:5671-10.20.1.10:33777   celery            21356           Y            CREDIT      363,228    0
  1                    celery                                                                     qpid.10.20.1.10:5671-10.20.1.10:33786   celery            21409           Y            CREDIT      5          0
'''

QPID_STAT_G_DOCS = '''
Broker Summary:
  uptime          cluster       connections  sessions  exchanges  queues
  ========================================================================
  97d 0h 16m 24s  <standalone>  23           37        14         33

Aggregate Broker Statistics:
  Statistic                   Messages    Bytes
  ========================================================
  queue-depth                 0           0
  total-enqueues              1,727,129   42,597,828,309
  total-dequeues              1,727,129   42,597,828,309
  persistent-enqueues         28,733      23,896,468
  persistent-dequeues         28,733      23,896,468
  transactional-enqueues      0           0
  transactional-dequeues      0           0
  flow-to-disk-depth          0           0
  flow-to-disk-enqueues       0           0
  flow-to-disk-dequeues       0           0
  acquires                    1,727,129
  releases                    0
  discards-no-route           41,171,496
  discards-ttl-expired        0
  discards-limit-overflow     0
  discards-ring-overflow      0
  discards-lvq-replace        0
  discards-subscriber-reject  0
  discards-purged             0
  reroutes                    0
  abandoned                   0
  abandoned-via-alt           0
'''


def test_qpid_stat_q_docs():
    env = {
        'qpid_stat_g': qpid_stat.QpidStatG(context_wrap(QPID_STAT_G_DOCS)),
        'qpid_stat_q': qpid_stat.QpidStatQ(context_wrap(QPID_STAT_Q_DOCS)),
        'qpid_stat_u': qpid_stat.QpidStatU(context_wrap(QPID_STAT_U_DOCS))
    }
    failed, total = doctest.testmod(qpid_stat, globs=env)
    assert failed == 0


QPID_STAT_Q = """
COMMAND> qpid-stat -q --ssl-certificate=/etc/pki/katello/qpid_client_striped.crt -b amqps://localhost:5671

Queues
  queue                                                                      dur  autoDel  excl  msg   msgIn  msgOut  bytes  bytesIn  bytesOut  cons  bind
  ==========================================================================================================================================================
  00d6cc19-15fc-4b7c-af3c-6a38e7bb386d:1.0                                        Y        Y        0     2      2       0    486      486         1     2
  server.example.com:event                                                   Y             Y        0  2.62k  2.62k      0   45.5m    45.5m        1     2
  celery                                                                     Y                      4    41     37    4.12k  37.5k    33.4k        8     2
  pulp.agent.836a7366-4790-482d-b3bc-efee9d42b3cd                            Y                      1     1      0     463    463        0         0     1
  reserved_resource_worker-7@server.example.com.celery.pidbox                     Y                 0     0      0       0      0        0         1     2
  reserved_resource_worker-7@server.example.com.dq                           Y    Y                 0   182    182       0    229k     229k        1     2
""".strip()


def test_qpid_stat_q():
    qpid_list = qpid_stat.QpidStatQ(context_wrap(QPID_STAT_Q))
    assert qpid_list.data[0].get('queue') == '00d6cc19-15fc-4b7c-af3c-6a38e7bb386d:1.0'
    assert qpid_list.data[0].get('dur') == ''
    assert qpid_list.data[1].get('queue') == 'server.example.com:event'
    assert qpid_list.data[1].get('dur') == 'Y'
    assert qpid_list.data[1].get('autoDel') == ''
    assert qpid_list.data[1].get('excl') == 'Y'
    assert qpid_list.data[1].get('msg') == '0'
    assert qpid_list.data[1].get('msgIn') == '2.62k'
    assert qpid_list.data[1].get('msgOut') == '2.62k'
    assert qpid_list.data[1].get('bytes') == '0'
    assert qpid_list.data[1].get('bytesIn') == '45.5m'
    assert qpid_list.data[1].get('bytesOut') == '45.5m'
    assert qpid_list.data[1].get('cons') == '1'
    assert qpid_list.data[1].get('bind') == '2'
    assert qpid_list.data[2].get('msg') == '4'
    assert qpid_list.data[3].get('cons') == '0'
    assert qpid_list.data[4].get('bytesIn') == '0'
    assert qpid_list.data[5].get('queue') == 'reserved_resource_worker-7@server.example.com.dq'
    assert qpid_list.data[5].get('dur') == 'Y'
    assert qpid_list.data[5].get('autoDel') == 'Y'
    assert qpid_list.data[5].get('excl') == ''
    assert qpid_list.data[5].get('msg') == '0'
    assert qpid_list.data[5].get('msgIn') == '182'
    assert qpid_list.data[5].get('msgOut') == '182'
    assert qpid_list.data[5].get('bytes') == '0'
    assert qpid_list.data[5].get('bytesIn') == '229k'
    assert qpid_list.data[5].get('bytesOut') == '229k'
    assert qpid_list.data[5].get('cons') == '1'
    assert qpid_list.data[5].get('bind') == '2'

    # test iteration
    assert [d['queue'] for d in qpid_list] == [
        '00d6cc19-15fc-4b7c-af3c-6a38e7bb386d:1.0',
        'server.example.com:event',
        'celery',
        'pulp.agent.836a7366-4790-482d-b3bc-efee9d42b3cd',
        'reserved_resource_worker-7@server.example.com.celery.pidbox',
        'reserved_resource_worker-7@server.example.com.dq',
    ]


QPID_STAT_U = """
COMMAND> qpid-stat -u --ssl-certificate=/etc/pki/katello/qpid_client_striped.crt -b amqps://localhost:5671

Subscriptions
  subscr               queue                                                                      conn                                    procName          procId  browse  acked  excl  creditMode  delivered  sessUnacked
  ===========================================================================================================================================================================================================================
  0                    00d6cc19-15fc-4b7c-af3c-6a38e7bb386d:1.0                                   qpid.10.20.1.10:5671-10.20.1.10:33787   celery            21409                        CREDIT      2          0
  0                    pulp.agent.c6a430bc-5ec7-42f8-99ce-f320ed0b9113                            qpid.10.20.1.10:5671-10.30.0.148:57423  goferd            32227           Y            CREDIT      0          0
  1                    server.example.com:event                                                   qpid.10.20.1.10:5671-10.20.1.10:33848   Qpid Java Client  21066           Y      Y     WINDOW      2,623      0
  0                    celeryev.4c77bd03-1cde-49eb-bdc0-b7c38f9ff93d                              qpid.10.20.1.10:5671-10.20.1.10:33777   celery            21356           Y            CREDIT      363,228    0
  1                    celery                                                                     qpid.10.20.1.10:5671-10.20.1.10:33786   celery            21409           Y            CREDIT      5          0
  katello_event_queue  katello_event_queue                                                        qpid.10.20.1.10:5671-10.20.1.10:33911   ruby              21801           Y            CREDIT      7,642      0
""".strip()


def test_qpid_stat_u():
    qpid_list = qpid_stat.QpidStatU(context_wrap(QPID_STAT_U))
    assert qpid_list.data[0].get('subscr') == '0'
    assert qpid_list.data[0].get('queue') == '00d6cc19-15fc-4b7c-af3c-6a38e7bb386d:1.0'
    assert qpid_list.data[0].get('conn') == 'qpid.10.20.1.10:5671-10.20.1.10:33787'
    assert qpid_list.data[0].get('procName') == 'celery'
    assert qpid_list.data[0].get('procId') == '21409'
    assert qpid_list.data[0].get('browse') == ''
    assert qpid_list.data[0].get('acked') == ''
    assert qpid_list.data[0].get('excl') == ''
    assert qpid_list.data[0].get('creditMode') == 'CREDIT'
    assert qpid_list.data[0].get('delivered') == '2'
    assert qpid_list.data[0].get('sessUnacked') == '0'
    assert qpid_list.data[1].get('queue') == 'pulp.agent.c6a430bc-5ec7-42f8-99ce-f320ed0b9113'
    assert qpid_list.data[1].get('conn') == 'qpid.10.20.1.10:5671-10.30.0.148:57423'
    assert qpid_list.data[1].get('acked') == 'Y'
    assert qpid_list.data[1].get('procName') == 'goferd'
    assert qpid_list.data[2].get('subscr') == '1'
    assert qpid_list.data[2].get('queue') == 'server.example.com:event'
    assert qpid_list.data[2].get('conn') == 'qpid.10.20.1.10:5671-10.20.1.10:33848'
    assert qpid_list.data[2].get('procName') == 'Qpid Java Client'
    assert qpid_list.data[2].get('procId') == '21066'
    assert qpid_list.data[2].get('browse') == ''
    assert qpid_list.data[2].get('acked') == 'Y'
    assert qpid_list.data[2].get('excl') == 'Y'
    assert qpid_list.data[2].get('creditMode') == 'WINDOW'
    assert qpid_list.data[2].get('delivered') == '2,623'
    assert qpid_list.data[2].get('sessUnacked') == '0'
    assert qpid_list.data[3].get('delivered') == '363,228'
    assert qpid_list.data[5].get('subscr') == 'katello_event_queue'

    # test iteration
    assert [d['queue'] for d in qpid_list] == [
        '00d6cc19-15fc-4b7c-af3c-6a38e7bb386d:1.0',
        'pulp.agent.c6a430bc-5ec7-42f8-99ce-f320ed0b9113',
        'server.example.com:event',
        'celeryev.4c77bd03-1cde-49eb-bdc0-b7c38f9ff93d',
        'celery',
        'katello_event_queue',
    ]


QPID_STAT_G = """
COMMAND> qpid-stat -g --ssl-certificate=/etc/pki/katello/qpid_client_striped.crt -b amqps://localhost:5671

Broker Summary:
  uptime          cluster       connections  sessions  exchanges  queues
  ========================================================================
  97d 0h 16m 24s  <standalone>  23           37        14         33

Aggregate Broker Statistics:
  Statistic                   Messages    Bytes
  ========================================================
  queue-depth                 0           0
  total-enqueues              1,727,129   42,597,828,309
  total-dequeues              1,727,129   42,597,828,309
  persistent-enqueues         28,733      23,896,468
  persistent-dequeues         28,733      23,896,468
  transactional-enqueues      0           0
  transactional-dequeues      0           0
  flow-to-disk-depth          0           0
  flow-to-disk-enqueues       0           0
  flow-to-disk-dequeues       0           0
  acquires                    1,727,129
  releases                    0
  discards-no-route           41,171,496
  discards-ttl-expired        0
  discards-limit-overflow     0
  discards-ring-overflow      0
  discards-lvq-replace        0
  discards-subscriber-reject  0
  discards-purged             0
  reroutes                    0
  abandoned                   0
  abandoned-via-alt           0
"""


def test_qpid_stat_g():
    qpid_list = qpid_stat.QpidStatG(context_wrap(QPID_STAT_G))
    assert qpid_list.data[0].get('uptime') == '97d 0h 16m 24s'
    assert qpid_list.data[0].get('cluster') == '<standalone>'
    assert qpid_list.data[0].get('connections') == '23'
    assert qpid_list.data[0].get('sessions') == '37'
    assert qpid_list.data[0].get('exchanges') == '14'
    assert qpid_list.data[0].get('queues') == '33'
    assert qpid_list.data[1].get('Statistic') == 'queue-depth'
    assert qpid_list.data[1].get('Messages') == '0'
    assert qpid_list.data[1].get('Bytes') == '0'
    assert qpid_list.data[11].get('Statistic') == 'acquires'
    assert qpid_list.data[11].get('Messages') == '1,727,129'
    assert qpid_list.data[11].get('Bytes') == ''

    # test iteration
    assert [d.get('Messages') for d in qpid_list] == [
            None, '0', '1,727,129', '1,727,129', '28,733',
            '28,733', '0', '0', '0', '0', '0', '1,727,129',
            '0', '41,171,496', '0', '0', '0', '0', '0',
            '0', '0', '0', '0'
    ]
    assert qpid_list.by_queue['<standalone>'] == {
            'uptime': '97d 0h 16m 24s',
            'sessions': '37',
            'queues': '33',
            'connections': '23',
            'cluster': '<standalone>',
            'exchanges': '14'
    }
