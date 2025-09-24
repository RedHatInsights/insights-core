from insights.parsers.crictl_ps import CrictlPs
from insights.tests import context_wrap
from insights.core.exceptions import ParseException, SkipComponent
import pytest


CRICTL_PS = """
CONTAINER           IMAGE                                                                                                                        CREATED              STATE               NAME                                          ATTEMPT             POD ID              POD
93b10093a8263       bea2d277eb71530a376a68be9760260cedb59f2392bb6e7793b05d5350df8d4c                                                             About a minute ago   Running             oauth-apiserver                               185                 19d971fe5c478       apiserver-7cd97c59ff-dwckz
e34ce05ade472       2c96c7c72cf99490b4bdbb7389020b7e4b5bb7dc43ea9cadc4d5af43cb300b3f                                                             9 days ago           Running             guard                                         1                   c48cc19e5b0b1       etcd-guard-nah-4jnq5-master-v8z5h-0
471d75b135b5b       90e50eece96ef2a252b729a76a2ee3360d3623295cceb7d3e623b55cb7aef30a                                                             9 days ago           Running             etcd                                          39                  d2dd84f8db754       etcd-nah-4jnq5-master-v8z5h-0
""".strip()

CRICTL_PS_WITH_DIFFERENT_STATES = """
CONTAINER           IMAGE                                                                                                                        CREATED              STATE               NAME                                          ATTEMPT             POD ID              POD
93b10093a8263       bea2d277eb71530a376a68be9760260cedb59f2392bb6e7793b05d5350df8d4c                                                             About a minute ago   Running             oauth-apiserver                               185                 19d971fe5c478       apiserver-7cd97c59ff-dwckz
e34ce05ade472       2c96c7c72cf99490b4bdbb7389020b7e4b5bb7dc43ea9cadc4d5af43cb300b3f                                                             2 hours ago          Exited              guard                                         1                   c48cc19e5b0b1       etcd-guard-nah-4jnq5-master-v8z5h-0
471d75b135b5b       90e50eece96ef2a252b729a76a2ee3360d3623295cceb7d3e623b55cb7aef30a                                                             1 day ago            ContainerCreating   etcd                                          39                  d2dd84f8db754       etcd-nah-4jnq5-master-v8z5h-0
abc123def456        sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef             3 weeks ago         Unknown              test-container                              5                   f1f2f3f4f5f6       test-pod-123
""".strip()

CRICTL_PS_EMPTY = """
CONTAINER           IMAGE                                                                                                                        CREATED              STATE               NAME                                          ATTEMPT             POD ID              POD
""".strip()

CRICTL_PS_INVALID_HEADER = """
INVALID HEADER
93b10093a8263       bea2d277eb71530a376a68be9760260cedb59f2392bb6e7793b05d5350df8d4c                                                             About a minute ago   Running             oauth-apiserver                               185                 19d971fe5c478       apiserver-7cd97c59ff-dwckz
""".strip()


def test_crictl_ps():
    """Test basic crictl ps parsing with standard output"""
    result = CrictlPs(context_wrap(CRICTL_PS))

    # Test number of records
    assert len(result) == 3

    # Test first record
    first_record = result[0]
    assert first_record['container_id'] == '93b10093a8263'
    assert first_record['image'] == 'bea2d277eb71530a376a68be9760260cedb59f2392bb6e7793b05d5350df8d4c'
    assert first_record['created'] == 'About a minute ago'
    assert first_record['state'] == 'Running'
    assert first_record['name'] == 'oauth-apiserver'
    assert first_record['attempt'] == '185'
    assert first_record['pod_id'] == '19d971fe5c478'
    assert first_record['pod'] == 'apiserver-7cd97c59ff-dwckz'

    # Test second record
    second_record = result[1]
    assert second_record['container_id'] == 'e34ce05ade472'
    assert second_record['image'] == '2c96c7c72cf99490b4bdbb7389020b7e4b5bb7dc43ea9cadc4d5af43cb300b3f'
    assert second_record['created'] == '9 days ago'
    assert second_record['state'] == 'Running'
    assert second_record['name'] == 'guard'
    assert second_record['attempt'] == '1'
    assert second_record['pod_id'] == 'c48cc19e5b0b1'
    assert second_record['pod'] == 'etcd-guard-nah-4jnq5-master-v8z5h-0'

    # Test third record
    third_record = result[2]
    assert third_record['container_id'] == '471d75b135b5b'
    assert third_record['image'] == '90e50eece96ef2a252b729a76a2ee3360d3623295cceb7d3e623b55cb7aef30a'
    assert third_record['created'] == '9 days ago'
    assert third_record['state'] == 'Running'
    assert third_record['name'] == 'etcd'
    assert third_record['attempt'] == '39'
    assert third_record['pod_id'] == 'd2dd84f8db754'
    assert third_record['pod'] == 'etcd-nah-4jnq5-master-v8z5h-0'


def test_crictl_ps_different_states():
    """Test crictl ps parsing with different container states"""
    result = CrictlPs(context_wrap(CRICTL_PS_WITH_DIFFERENT_STATES))

    # Test number of records
    assert len(result) == 4

    # Test different states
    states = [record['state'] for record in result]
    assert 'Running' in states
    assert 'Exited' in states
    assert 'ContainerCreating' in states
    assert 'Unknown' in states

    # Test different created formats
    created_values = [record['created'] for record in result]
    assert 'About a minute ago' in created_values
    assert '2 hours ago' in created_values
    assert '1 day ago' in created_values
    assert '3 weeks ago' in created_values

    # Test record with different image format (sha256:)
    sha256_record = result[3]
    assert sha256_record['container_id'] == 'abc123def456'
    assert sha256_record['image'] == 'sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
    assert sha256_record['state'] == 'Unknown'
    assert sha256_record['name'] == 'test-container'
    assert sha256_record['attempt'] == '5'
    assert sha256_record['pod_id'] == 'f1f2f3f4f5f6'
    assert sha256_record['pod'] == 'test-pod-123'


def test_crictl_ps_empty():
    """Test crictl ps parsing with empty data"""
    with pytest.raises(SkipComponent) as excinfo:
        CrictlPs(context_wrap(CRICTL_PS_EMPTY))

    assert "No container records found" in str(excinfo.value)


def test_crictl_ps_invalid_header():
    """Test crictl ps parsing with invalid header"""
    with pytest.raises(ParseException) as excinfo:
        CrictlPs(context_wrap(CRICTL_PS_INVALID_HEADER))

    assert "invalid content" in str(excinfo.value)


def test_crictl_ps_container_ids():
    """Test accessing container IDs"""
    result = CrictlPs(context_wrap(CRICTL_PS))

    # Test container_ids property
    expected_ids = ['93b10093a8263', 'e34ce05ade472', '471d75b135b5b']
    assert result.container_ids == expected_ids


def test_crictl_ps_indexing():
    """Test indexing and iteration"""
    result = CrictlPs(context_wrap(CRICTL_PS))

    # Test indexing
    assert result[0]['container_id'] == '93b10093a8263'
    assert result[1]['container_id'] == 'e34ce05ade472'
    assert result[2]['container_id'] == '471d75b135b5b'

    # Test length
    assert len(result) == 3

    # Test iteration
    container_ids = []
    for record in result:
        container_ids.append(record['container_id'])

    expected_ids = ['93b10093a8263', 'e34ce05ade472', '471d75b135b5b']
    assert container_ids == expected_ids


def test_crictl_ps_contains():
    """Test contains method"""
    result = CrictlPs(context_wrap(CRICTL_PS))

    # Test that records are in the data
    first_record = result[0]
    assert first_record in result

    # Test that a non-existent record is not in the data
    fake_record = {
        'container_id': 'fake', 'image': 'fake', 'created': 'fake',
        'state': 'fake', 'name': 'fake', 'attempt': 'fake',
        'pod_id': 'fake', 'pod': 'fake'
    }
    assert fake_record not in result


def test_crictl_ps_field_types():
    """Test that all required fields are present and have correct types"""
    result = CrictlPs(context_wrap(CRICTL_PS))

    required_fields = ['container_id', 'image', 'created', 'state', 'name', 'attempt', 'pod_id', 'pod']

    for record in result:
        # Check all required fields are present
        for field in required_fields:
            assert field in record
            assert isinstance(record[field], str)
            assert record[field] != ''  # Fields should not be empty


def test_crictl_ps_edge_cases():
    """Test edge cases in parsing"""
    # Test with minimal valid data
    minimal_data = """
CONTAINER           IMAGE                                                                                                                        CREATED              STATE               NAME                                          ATTEMPT             POD ID              POD
abc123             def456                                                                                                                      1 hour ago           Running             test                                         1                   pod123              test-pod
""".strip()

    result = CrictlPs(context_wrap(minimal_data))
    assert len(result) == 1

    record = result[0]
    assert record['container_id'] == 'abc123'
    assert record['image'] == 'def456'
    assert record['created'] == '1 hour ago'
    assert record['state'] == 'Running'
    assert record['name'] == 'test'
    assert record['attempt'] == '1'
    assert record['pod_id'] == 'pod123'
    assert record['pod'] == 'test-pod'


def test_crictl_ps_examples():
    """Test the examples from the docstring"""
    result = CrictlPs(context_wrap(CRICTL_PS))

    # Test the examples from the docstring
    assert len(result) == 3
    assert result[0]['container_id'] == '93b10093a8263'
    assert result[0]['image'] == 'bea2d277eb71530a376a68be9760260cedb59f2392bb6e7793b05d5350df8d4c'
    assert result[0]['created'] == 'About a minute ago'
    assert result[0]['state'] == 'Running'
    assert result[0]['name'] == 'oauth-apiserver'
    assert result[0]['attempt'] == '185'
    assert result[0]['pod_id'] == '19d971fe5c478'
    assert result[0]['pod'] == 'apiserver-7cd97c59ff-dwckz'
