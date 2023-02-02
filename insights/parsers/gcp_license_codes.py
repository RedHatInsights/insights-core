"""
GCPLicenseCodes
===============

This parser reads the output of a command
``curl -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/licenses/?recursive=True"``,
which is used to check whether the google cloud instance is a licensed marketplace instance.

For more details, See: https://cloud.google.com/compute/docs/reference/rest/v1/images/get#body.Image.FIELDS.license_code

"""
import json

from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.gcp_license_codes)
class GCPLicenseCodes(CommandParser):
    """
    Class for parsing the GCP License Codes returned by command
    ``curl -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/licenses/?recursive=True"``,


    Typical Output of this command is::

        [{"id": "601259152637613565"}]

    Raises:
        SkipComponent: When content is empty or no parse-able content.
        ParseException: When the json is unable to be parsed

    Attributes:
        ids (list): A list containing the IDs found on the instance
        raw (str): The full JSON of the plan returned by the ``curl`` command

    Examples:
        >>> gcp_licenses.ids == ["601259152637613565"]
        True
        >>> gcp_licenses.raw == [{"id": "601259152637613565"}]
        True
    """

    def parse_content(self, content):
        if not content or 'curl: ' in content[0]:
            raise SkipComponent()
        try:
            license_list = json.loads(content[0])
        except:
            raise ParseException("Unable to parse JSON")

        self.raw = license_list
        self.ids = None
        if len(license_list) >= 1:
            self.ids = [l["id"] for l in license_list]

    def __repr__(self):
        return "ids: {i}, raw: {r}".format(
            i=self.ids, r=self.raw
        )
