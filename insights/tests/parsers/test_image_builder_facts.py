import doctest

from insights.parsers import image_builder_facts
from insights.parsers.image_builder_facts import ImageBuilderFacts
from insights.tests import context_wrap
from insights.tests.parsers import skip_component_check


IB_FACTS = """
{
  "image-builder.insights.compliance-policy-id": "61812cce-c884-4d52-bf05-15b41370db23",
  "image-builder.insights.compliance-profile-id": "xccdf_org.ssgproject.content_profile_cis",
  "image-builder.osbuild-composer.api-type": "cloudapi-v2"
}
""".strip()


def test_image_builder_facts():
    result = ImageBuilderFacts(context_wrap(IB_FACTS))

    assert result.data == {
        "image-builder.insights.compliance-policy-id": "61812cce-c884-4d52-bf05-15b41370db23",
        "image-builder.insights.compliance-profile-id": "xccdf_org.ssgproject.content_profile_cis",
        "image-builder.osbuild-composer.api-type": "cloudapi-v2"
    }


def test_image_builder_facts_empty():
    assert 'Empty output.' in skip_component_check(ImageBuilderFacts)


def test_image_builder_facts_doc_examples():
    env = {
        'ImageBuilderFacts': ImageBuilderFacts,
        'image_builder_facts': ImageBuilderFacts(context_wrap(IB_FACTS)),
    }
    failed, total = doctest.testmod(image_builder_facts, globs=env)
    assert failed == 0
