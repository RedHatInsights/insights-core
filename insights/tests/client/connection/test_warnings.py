import warnings

from insights import load_default_plugins


def test_load_default_plugins_does_not_disable_warnings():
    """
    Default plugins import insights.client.connection, which must not
    globally suppress warnings.
    """
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        load_default_plugins()
        warnings.warn(
            "SampleCondition has been deprecated. Use AnotherCondition.",
            DeprecationWarning,
        )

    assert len(caught) == 1
    assert issubclass(caught[0].category, DeprecationWarning)
