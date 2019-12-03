import pytest
from insights.client.archive import InsightsArchive


def test_force_reregister():
    with pytest.raises(RuntimeError):
        archive1 = InsightsArchive('/')
    with pytest.raises(RuntimeError):
        archive2 = InsightsArchive('/tmp')
    with pytest.raises(RuntimeError):
        archive3 = InsightsArchive('/tmp/')
    archive4 = InsightsArchive('/tmp/abc')
    assert archive4
    archive5 = InsightsArchive('/tmp/abc/')
    assert archive5
    archive6 = InsightsArchive('/tmp/abc/def')
    assert archive6
    # config = InsightsConfig(reregister=True)
    # client = InsightsClient(config)
    # client.connection = FakeConnection(registered=None)
    # client.session = True

    # # initialize comparisons
    # old_machine_id = None
    # new_machine_id = None

    # # register first
    # assert client.register() is True
    # for r in constants.registered_files:
    #     assert os.path.isfile(r) is True

    # # get modified time of .registered to ensure it's regenerated
    # old_reg_file1_ts = os.path.getmtime(constants.registered_files[0])
    # old_reg_file2_ts = os.path.getmtime(constants.registered_files[1])

    # old_machine_id = generate_machine_id()
