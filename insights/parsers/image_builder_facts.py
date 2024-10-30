"""
ImageBuilderFacts - file ``/etc/rhsm/facts/osbuild.facts``
==========================================================

This module provides parsing for the ``/etc/rhsm/facts/osbuild.facts`` file.
The ``ImageBuilderFacts`` class is based on a shared class which processes the JSON
information into a dictionary.
"""

from insights.core import JSONParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.image_builder_facts)
class ImageBuilderFacts(JSONParser):
    """
    Parses the ``/etc/rhsm/facts/osbuild.facts`` file.

    Sample input::

        {
          "image-builder.insights.compliance-policy-id": "61812cce-c884-4d52-bf05-15b41370db23",
          "image-builder.insights.compliance-profile-id": "xccdf_org.ssgproject.content_profile_cis",
          "image-builder.osbuild-composer.api-type": "cloudapi-v2"
        }

    Output will be a python object with the same structure as the JSON::

        {
          "image-builder.insights.compliance-policy-id": "61812cce-c884-4d52-bf05-15b41370db23",
          "image-builder.insights.compliance-profile-id": "xccdf_org.ssgproject.content_profile_cis",
          "image-builder.osbuild-composer.api-type": "cloudapi-v2"
        }

    Example:

        >>> type(image_builder_facts)
        <class 'insights.parsers.image_builder_facts.ImageBuilderFacts'>
        >>> image_builder_facts["image-builder.insights.compliance-policy-id"] == "61812cce-c884-4d52-bf05-15b41370db23"
        True
    """
    pass
