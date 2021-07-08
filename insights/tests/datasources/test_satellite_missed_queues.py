import pytest
from mock.mock import Mock

from insights.core.dr import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs import Specs
from insights.specs.datasources.satellite_missed_queues import LocalSpecs, satellite_missed_pulp_agent_queues


MESSAGE_WITH_ERRORS = """
Jan 16 00:06:13 satellite qpidd: 2018-01-16 00:06:13 [Protocol] error Error on attach: Node not found: pulp.agent.09008eec-aba6-4174-aa9f-e930004ce5c9
Jan 16 00:06:13 satellite qpidd[51948]: 2018-01-16 00:06:13 [Protocol] error Error on attach: Node not found: pulp.agent.09008eec-aba6-4174-aa9f-e930004ce5c9
Jan 16 00:06:16 satellite qpidd: 2018-01-16 00:06:16 [Protocol] error Error on attach: Node not found: pulp.agent.fac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024
Jan 16 00:06:16 satellite qpidd[51948]: 2018-01-16 00:06:16 [Protocol] error Error on attach: Node not found: pulp.agent.fac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024
Jan 16 00:06:17 satellite qpidd[51948]: 2018-01-16 00:06:17 [Protocol] error Error on attach: Node not found: pulp.agent.a91bbcad-4310-47d3-b550-57b904ef815d
Jan 16 00:06:17 satellite qpidd: 2018-01-16 00:06:17 [Protocol] error Error on attach: Node not found: pulp.agent.a91bbcad-4310-47d3-b550-57b904ef815d
Jan 16 00:06:21 satellite qpidd: 2018-01-16 00:06:21 [Protocol] error Error on attach: Node not found: pulp.agent.5fc8b4e2-1d2e-47e9-a34f-2017bb3bb417
Jan 16 00:06:21 satellite qpidd[51948]: 2018-01-16 00:06:21 [Protocol] error Error on attach: Node not found: pulp.agent.5fc8b4e2-1d2e-47e9-a34f-2017bb3bb417
Jan 16 00:06:23 satellite qpidd: 2018-01-16 00:06:23 [Protocol] error Error on attach: Node not found: pulp.agent.8330f90a-d4f0-41e2-8792-4f1b9960ceef
Jan 16 00:06:23 satellite qpidd[51948]: 2018-01-16 00:06:23 [Protocol] error Error on attach: Node not found: pulp.agent.8330f90a-d4f0-41e2-8792-4f1b9960ceef
Jan 16 00:06:25 satellite qpidd: 2018-01-16 00:06:25 [Protocol] error Error on attach: Node not found: pulp.agent.4caf276f-644a-4327-8975-fb34c83a788c
Jan 16 00:06:25 satellite qpidd[51948]: 2018-01-16 00:06:25 [Protocol] error Error on attach: Node not found: pulp.agent.4caf276f-644a-4327-8975-fb34c83a788c
Jan 16 00:06:32 satellite qpidd: 2018-01-16 00:06:32 [Protocol] error Error on attach: Node not found: pulp.agent.076a1c3f-3dde-4523-b26c-fcfffbd93b0e
Jan 16 00:06:32 satellite qpidd[51948]: 2018-01-16 00:06:32 [Protocol] error Error on attach: Node not found: pulp.agent.076a1c3f-3dde-4523-b26c-fcfffbd93b0e
Jan 16 00:06:34 satellite qpidd: 2018-01-16 00:06:34 [Protocol] error Error on attach: Node not found: pulp.agent.076a1c3f-3dde-4523-b26c-fcfffbd93bde
Jan 16 00:06:34 satellite qpidd[51948]: 2018-01-16 00:06:34 [Protocol] error Error on attach: Node not found: pulp.agent.076a1c3f-3dde-4523-b26c-fcfffbd93bde
Jan 16 00:06:35 satellite qpidd: 2018-01-16 00:06:35 [Protocol] error Error on attach: Node not found: pulp.agent.076a1c3f-3dde-4523-b26c-fcfffbd93bae
Jan 16 00:06:35 satellite qpidd[51948]: 2018-01-16 00:06:35 [Protocol] error Error on attach: Node not found: pulp.agent.076a1c3f-3dde-4523-b26c-fcfffbd93bae
Jan 16 00:06:36 satellite qpidd: 2018-01-16 00:06:36 [Protocol] error Error on attach: Node not found: pulp.agent.076a1c3f-3dde-4523-b26c-fcfffbd93bfe
Jan 16 00:06:36 satellite qpidd[51948]: 2018-01-16 00:06:36 [Protocol] error Error on attach: Node not found: pulp.agent.076a1c3f-3dde-4523-b26c-fcfffbd93bfe
""".strip()

MESSAGE_WITHOUT_ERROR = """
Jun 13 03:28:03 ab.cd pulp: gofer.messaging.adapter.qpid.connection:INFO: closed: qpid+ssl://localhost:5671
Jun 13 03:28:04 ab.cd pulp: gofer.messaging.adapter.qpid.connection:INFO: closed: qpid+ssl://localhost:5671
Jun 13 03:28:07 ab.cd pulp: pulp.server.db.connection:INFO: Attempting to connect to localhost:27017
Jun 13 03:28:07 ab.cd pulp: pulp.server.db.connection:INFO: Attempting to connect to localhost:27017
Jun 13 03:28:07 ab.cd pulp: pulp.server.db.connection:INFO: Attempting to connect to localhost:27017
Jun 13 03:28:07 ab.cd pulp: pulp.server.db.connection:INFO: Attempting to connect to localhost:27017
Jun 13 03:28:07 ab.cd pulp: pulp.server.db.connection:INFO: Attempting to connect to localhost:27017
Jun 13 03:28:07 ab.cd pulp: pulp.server.db.connection:INFO: Attempting to connect to localhost:27017
Jun 13 03:28:07 ab.cd pulp: pulp.server.db.connection:INFO: Attempting to connect to localhost:27017
Jun 13 03:28:07 ab.cd pulp: pulp.server.db.connection:INFO: Attempting to connect to localhost:27017
Jun 13 03:28:08 ab.cd pulp: pulp.server.db.connection:INFO: Write concern for Mongo connection: {}
Jun 13 03:28:08 ab.cd pulp: pulp.server.db.connection:INFO: Write concern for Mongo connection: {
""".strip()

MESSAGE_WITH_ERROR_BUT_QUEUE_EXISTS = """
Jan 16 00:06:13 satellite qpidd: 2018-01-16 00:06:13 [Protocol] error Error on attach: Node not found: pulp.agent.49041b8c-cf5b-4ec6-a8db-66ea70d04566
Jan 16 00:06:13 satellite qpidd[51948]: 2018-01-16 00:06:13 [Protocol] error Error on attach: Node not found: pulp.agent.49041b8c-cf5b-4ec6-a8db-66ea70d04566
Jan 16 00:06:16 satellite qpidd: 2018-01-16 00:06:16 [Protocol] error Error on attach: Node not found: pulp.agent.39f7b444-1532-43c2-ab1f-dd62a69a3be2
Jan 16 00:06:16 satellite qpidd[51948]: 2018-01-16 00:06:16 [Protocol] error Error on attach: Node not found: pulp.agent.39f7b444-1532-43c2-ab1f-dd62a69a3be2
Jan 16 00:06:17 satellite qpidd[51948]: 2018-01-16 00:06:17 [Protocol] error Error on attach: Node not found: pulp.agent.70d37c60-26d5-415d-ae95-722806b802b1
Jan 16 00:06:17 satellite qpidd: 2018-01-16 00:06:17 [Protocol] error Error on attach: Node not found: pulp.agent.70d37c60-26d5-415d-ae95-722806b802b1
""".strip()

HOST_UUIDS = """
                 uuid
--------------------------------------
 49041b8c-cf5b-4ec6-a8db-66ea70d04566
 c274234a-bd93-4868-8267-a5ea3a434c33
 70d37c60-26d5-415d-ae95-722806b802b1
 39f7b444-1532-43c2-ab1f-dd62a69a3be2
 09008eec-aba6-4174-aa9f-e930004ce5c9
 fac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024
(6 rows)
""".strip()

HOST_UUIDS_1 = """
                 uuid
--------------------------------------
(0 rows)
""".strip()

HOST_UUIDS_2 = """
                 uuid
--------------------------------------
 49041b8c-cf5b-4ec6-a8db-66ea70d04566
 c274234a-bd93-4868-8267-a5ea3a434c33
 70d37c60-26d5-415d-ae95-722806b802b1
 39f7b444-1532-43c2-ab1f-dd62a69a3be2
 09008eec-aba6-4174-aa9f-e930004ce5c9
 fac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024
 a91bbcad-4310-47d3-b550-57b904ef815d
 5fc8b4e2-1d2e-47e9-a34f-2017bb3bb417
 8330f90a-d4f0-41e2-8792-4f1b9960ceef
 4caf276f-644a-4327-8975-fb34c83a788c
 076a1c3f-3dde-4523-b26c-fcfffbd93b0e
 076a1c3f-3dde-4523-b26c-fcfffbd93bde
 076a1c3f-3dde-4523-b26c-fcfffbd93bae
 076a1c3f-3dde-4523-b26c-fcfffbd93bfe
(14 rows)
""".strip()

QPID_QUEUES = """
Queues
  queue                                                                           dur  autoDel  excl  msg   msgIn  msgOut  bytes  bytesIn  bytesOut  cons  bind
  ===============================================================================================================================================================
  1c82aae4-3f19-4739-8799-2140e47d8af6:1.0                                             Y        Y        0     8      8       0   5.04k    5.04k        1     2
  1c82aae4-3f19-4739-8799-2140e47d8af6:2.0                                             Y        Y        0     4      4       0   2.55k    2.55k        1     2
  28899b04-2085-4366-ae85-fe70b1e930ff:1.0                                             Y        Y        0     1      1       0    243      243         1     2
  2dc38953-d515-4f93-92b0-6dd13d872632:1.0                                             Y        Y        0     8      8       0   5.04k    5.04k        1     2
  2dc38953-d515-4f93-92b0-6dd13d872632:2.0                                             Y        Y        0     4      4       0   2.55k    2.55k        1     2
  41fa4a8d-7061-4527-b4ec-19f33085cde3:1.0                                             Y        Y        0     4      4       0   2.46k    2.46k        1     2
  50570ead-86c5-410a-bc82-8d3c84fbfc6e:1.0                                             Y        Y        0     8      8       0   5.04k    5.04k        1     2
  50570ead-86c5-410a-bc82-8d3c84fbfc6e:2.0                                             Y        Y        0     4      4       0   2.55k    2.55k        1     2
  6d51a877-f190-4d84-80bd-ee75bd2571ec:1.0                                             Y        Y        0     1      1       0    243      243         1     2
  8023568e-6343-4010-8f7b-420c4c05bcb9:1.0                                             Y        Y        0     4      4       0   2.42k    2.42k        1     2
  80841d92-2539-42b2-941d-9ccbf6513be2:1.0                                             Y        Y        0     8      8       0   4.89k    4.89k        1     2
  828ac1e2-520a-4df1-954c-f219e6ba811f:0.0                                             Y        Y        0     0      0       0      0        0         1     2
  916ba27c-08f6-4854-9e6f-80db7dee6cfd:1.0                                             Y        Y        0     1      1       0    243      243         1     2
  927aefc9-ebe6-4548-a52f-83565ab0c75e:1.0                                             Y        Y        0     8      8       0   5.04k    5.04k        1     2
  927aefc9-ebe6-4548-a52f-83565ab0c75e:2.0                                             Y        Y        0     4      4       0   2.47k    2.47k        1     2
  a3b72515-b58d-4217-a060-bd871fe53418:1.0                                             Y        Y        0     1      1       0    243      243         1     2
  b5e362ac-926a-4a57-a42d-de8dfb747fd1:1.0                                             Y        Y        0     8      8       0   5.04k    5.04k        1     2
  b5e362ac-926a-4a57-a42d-de8dfb747fd1:2.0                                             Y        Y        0     4      4       0   2.55k    2.55k        1     2
  b8995e8a-9d78-4665-86d8-7b3cded8a8f2:1.0                                             Y        Y        0     8      8       0   4.89k    4.89k        1     2
  bcf2f3fc-6b74-4329-8db6-3b90f62c5fd9:1.0                                             Y        Y        0     8      8       0   4.89k    4.89k        1     2
  c0b5d7ab-ef90-404d-90ff-f2623846f375:1.0                                             Y        Y        0     4      4       0   2.42k    2.42k        1     2
  c8ccd59e-4581-4287-b910-6bf1ede38297:1.0                                             Y        Y        0     8      8       0   4.89k    4.89k        1     2
  cebd9c62-42ff-4fa4-b148-6e8339751b4e:1.0                                             Y        Y        0     1      1       0    243      243         1     2
  celery                                                                          Y                      0  15.0k  15.0k      0   12.7m    12.7m        4     2
  e688cf97-9868-4d91-a3b1-9e60655331ac:1.0                                             Y        Y        0     8      8       0   4.89k    4.89k        1     2
  e79c3bd9-ada3-4b0e-86e3-062564e26488:1.0                                             Y        Y        0     8      8       0   4.89k    4.89k        1     2
  pulp.agent.39f7b444-1532-43c2-ab1f-dd62a69a3be2                                 Y                      6     6      0    3.67k  3.67k       0         0     1
  pulp.agent.49041b8c-cf5b-4ec6-a8db-66ea70d04566                                 Y                      2     2      0    1.18k  1.18k       0         0     1
  pulp.agent.70d37c60-26d5-415d-ae95-722806b802b1                                 Y                      0     4      4       0   2.70k    2.70k        1     1
  pulp.task                                                                       Y                      0    12     12       0   8.61k    8.61k        3     1
  reserved_resource_worker-0@ab.cd.def.com.celery.pidbox       Y                 0     0      0       0      0        0         1     2
  reserved_resource_worker-0@ab.cd.def.com.dq2            Y                      0  1.20k  1.20k      0   9.87m    9.87m        1     2
  reserved_resource_worker-1@ab.cd.def.com.celery.pidbox       Y                 0     0      0       0      0        0         1     2
  reserved_resource_worker-1@ab.cd.def.com.dq2            Y                      0   398    398       0    507k     507k        1     2
  reserved_resource_worker-2@ab.cd.def.com.celery.pidbox       Y                 0     0      0       0      0        0         1     2
  reserved_resource_worker-2@ab.cd.def.com.dq2            Y                      0   488    488       0    622k     622k        1     2
  reserved_resource_worker-3@ab.cd.def.com.celery.pidbox       Y                 0     0      0       0      0        0         1     2
  reserved_resource_worker-3@ab.cd.def.com.dq2            Y                      0   574    574       0    732k     732k        1     2
  resource_manager                                                                Y                      0  1.33k  1.33k      0   10.6m    10.6m        1     2
  resource_manager@ab.cd.def.com.celery.pidbox                 Y                 0     0      0       0      0        0         1     2
  resource_manager@ab.cd.def.com.dq2                      Y                      0     0      0       0      0        0         1     2
""".strip()

MISSED_QUEUES_OUTPUT = """
pulp.agent.09008eec-aba6-4174-aa9f-e930004ce5c9:2018-01-16 00:06:13
pulp.agent.fac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024:2018-01-16 00:06:16
0
""".strip()

MISSED_QUEUES_OUTPUT_2 = """
pulp.agent.09008eec-aba6-4174-aa9f-e930004ce5c9:2018-01-16 00:06:13
pulp.agent.fac7ebbc-ee4f-44b4-9fe0-3f4e42c7f024:2018-01-16 00:06:16
pulp.agent.a91bbcad-4310-47d3-b550-57b904ef815d:2018-01-16 00:06:17
pulp.agent.5fc8b4e2-1d2e-47e9-a34f-2017bb3bb417:2018-01-16 00:06:21
pulp.agent.8330f90a-d4f0-41e2-8792-4f1b9960ceef:2018-01-16 00:06:23
pulp.agent.4caf276f-644a-4327-8975-fb34c83a788c:2018-01-16 00:06:25
pulp.agent.076a1c3f-3dde-4523-b26c-fcfffbd93b0e:2018-01-16 00:06:32
pulp.agent.076a1c3f-3dde-4523-b26c-fcfffbd93bde:2018-01-16 00:06:34
pulp.agent.076a1c3f-3dde-4523-b26c-fcfffbd93bae:2018-01-16 00:06:35
pulp.agent.076a1c3f-3dde-4523-b26c-fcfffbd93bfe:2018-01-16 00:06:36
1
""".strip()

RELATIVE_PATH = "insights_commands/satellite_missed_qpid_queues"


def mock_stream():
    for line in MESSAGE_WITH_ERRORS.splitlines():
        yield line


def mock_stream_without_error():
    for line in MESSAGE_WITHOUT_ERROR.splitlines():
        yield line


def mock_stream_with_queue_exists():
    for line in MESSAGE_WITH_ERROR_BUT_QUEUE_EXISTS.splitlines():
        yield line


def test_satellite_missed_queues():
    host_uuids = Mock()
    host_uuids.content = HOST_UUIDS.splitlines()
    qpid_queues = Mock()
    qpid_queues.content = QPID_QUEUES.splitlines()
    messages = Mock()
    messages.stream = mock_stream
    broker = {
        Specs.messages: messages,
        LocalSpecs.content_host_uuids: host_uuids,
        LocalSpecs.qpid_queues: qpid_queues,
    }
    result = satellite_missed_pulp_agent_queues(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=MISSED_QUEUES_OUTPUT.splitlines(), relative_path=RELATIVE_PATH)
    assert sorted(result.content) == sorted(expected.content)
    assert result.relative_path == expected.relative_path


def test_satellite_missed_queues_with_more_data():
    host_uuids = Mock()
    host_uuids.content = HOST_UUIDS_2.splitlines()
    qpid_queues = Mock()
    qpid_queues.content = QPID_QUEUES.splitlines()
    messages = Mock()
    messages.stream = mock_stream
    broker = {
        Specs.messages: messages,
        LocalSpecs.content_host_uuids: host_uuids,
        LocalSpecs.qpid_queues: qpid_queues,
    }
    result = satellite_missed_pulp_agent_queues(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=MISSED_QUEUES_OUTPUT_2.splitlines(), relative_path=RELATIVE_PATH)
    assert sorted(result.content) == sorted(expected.content)
    assert result.relative_path == expected.relative_path


def test_exception():
    host_uuids = Mock()
    host_uuids.content = HOST_UUIDS_2.splitlines()
    qpid_queues = Mock()
    qpid_queues.content = QPID_QUEUES.splitlines()
    messages = Mock()
    messages.stream = mock_stream_without_error
    broker = {
        Specs.messages: messages,
        LocalSpecs.content_host_uuids: host_uuids,
        LocalSpecs.qpid_queues: qpid_queues,
    }
    with pytest.raises(SkipComponent):
        satellite_missed_pulp_agent_queues(broker)

    new_messages = Mock()
    new_messages.stream = mock_stream_with_queue_exists
    broker[Specs.messages] = new_messages
    with pytest.raises(SkipComponent):
        satellite_missed_pulp_agent_queues(broker)

    empty_uuids = Mock()
    empty_uuids.content = HOST_UUIDS_1.splitlines()
    broker[LocalSpecs.content_host_uuids] = empty_uuids
    with pytest.raises(SkipComponent):
        satellite_missed_pulp_agent_queues(broker)
