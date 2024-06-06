import base64
import copy
import hashlib
import logging
import os
import pkgutil
import tempfile

import six

import insights.client.apps.ansible
from insights.client.apps.ansible.playbook_verifier.contrib import gnupg
from insights.client.apps.ansible.playbook_verifier.contrib.ruamel_yaml.ruamel import yaml
from insights.client.apps.ansible.playbook_verifier.contrib.ruamel_yaml.ruamel.yaml.comments import CommentedMap, CommentedSeq
from insights.client.apps.ansible.playbook_verifier.contrib.ruamel_yaml.ruamel.yaml.scalarint import ScalarInt
from insights.client.constants import InsightsConstants as constants


__all__ = ("load_playbook_yaml", "verify", "PlaybookVerificationError")

yaml = yaml.YAML(typ='rt')
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.default_flow_style = False
yaml.preserve_quotes = True
yaml.width = 200

PLAYBOOK_SIGNATURE_LABEL = 'insights_signature'
PLAYBOOK_DYNAMIC_LABELS = ['hosts', 'vars']

PUBLIC_KEY_PATH = pkgutil.get_data(insights.client.apps.ansible.__name__, 'playbook_verifier/public.gpg')

logger = logging.getLogger(__name__)


class PlaybookVerificationError(Exception):
    """Exception raised when playbook verification fails."""
    def __init__(self, message="Could not verify Ansible playbook"):
        self.message = message
        super(PlaybookVerificationError, self).__init__(self.message)

    def __str__(self):
        return self.message


def load_playbook_yaml(playbook):
    """Parse a string into a dictionary.

    :param playbook: The Ansible playbook
    :type playbook: str

    :returns: The playbook dictionary
    :rtype: list[dict]

    :raises PlaybookVerificationError: The input is empty or corrupted.
    """
    if not playbook:
        raise PlaybookVerificationError("Cannot load a playbook from an empty input.")

    try:
        return yaml.load(playbook)
    except Exception:
        raise PlaybookVerificationError("Could not load the playbook.")


def normalize_snippet(snippet):
    """In Python 2, get rid of any default unicode values.

    :param snippet: The (part of) Ansible playbook.
    :type snippet: dict | yaml.comments.CommentedMap

    :returns: Snippet with any Unicode text converted to ASCII.
    :rtype: CommentedMap
    """
    result = CommentedMap()
    for key, value in snippet.iteritems():
        if isinstance(value, CommentedMap):
            result[key] = CommentedMap(normalize_snippet(value))
            continue

        if isinstance(value, CommentedSeq):
            new_sequence = CommentedSeq()
            for item in value:
                if isinstance(item, six.text_type):
                    new_sequence.append(item.encode('ascii', 'ignore'))
                    continue
                if isinstance(item, CommentedMap):
                    new_sequence.append(normalize_snippet(item))
                    continue
                new_sequence.append(item)

            result[key] = new_sequence
            continue

        if isinstance(value, six.text_type):
            result[key] = value.encode('ascii', 'ignore')
            continue

        if isinstance(value, ScalarInt):
            result[key] = int(value)
            continue

        result[key] = value

    return result


def serialize_playbook_snippet(snippet):
    """Convert the snippet object to bytes.

    :param snippet: The (part of) Ansible playbook.
    :type snippet: dict
    :returns: Serialized snippet.
    :rtype: bytes
    """
    if six.PY2:
        return str(normalize_snippet(snippet)).encode("utf-8")
    return str(snippet).encode("utf-8")


def hash_playbook_snippet(serialized_snippet):
    """Create SHA256 hash of a playbook snippet.

    :param serialized_snippet: The (part of) Ansible playbook.
    :type serialized_snippet: bytes
    :returns: Hashed snippet.
    :rtype: bytes
    """
    sha = hashlib.sha256()
    sha.update(serialized_snippet)
    return sha.digest()


def get_public_key(gpg):
    """Import public GPG key.

    :param gpg: Path to the GPG key.
    :type gpg: gnupg.GPG
    :returns: Import result
    :rtype: ...
    """
    if not PUBLIC_KEY_PATH:
        raise PlaybookVerificationError(message="Public key file not found.")

    public_key = PUBLIC_KEY_PATH
    import_results = gpg.import_keys(public_key)
    if import_results.count < 1:
        raise PlaybookVerificationError(message="Public key import failed.")

    return import_results


def exclude_dynamic_elements(snippet):
    """Remove dynamic elements from the Ansible playbook snippet.

    Some parts of the Ansible playbook are dynamic (e.g. host systems) and cannot be signed,
    because the signature would have to be unique for every playbook that is generated.

    This function removes these variable sections.

    :returns: New playbook dictionary without the unwanted values.
    :rtype: dict

    :raises PlaybookVerificationError:
    """
    if 'insights_signature_exclude' not in snippet.get('vars', {}):
        raise PlaybookVerificationError(
            "The playbook snippet does not have the key 'vars/insights_signature_exclude', "
            "dynamic exclusion cannot be performed."
        )

    exclusions = snippet['vars']['insights_signature_exclude'].split(',')  # type: list[str]
    result = copy.deepcopy(snippet)  # type: dict[str, ...]

    for element in exclusions:
        elements = [string for string in element.split("/") if string != '']  # type: list[str]

        if len(elements) == 1 and elements[0] in PLAYBOOK_DYNAMIC_LABELS:
            try:
                del result[elements[0]]
            except Exception:
                raise PlaybookVerificationError(
                    "Dynamic key '{key}' does not exist and could not be excluded.".format(key=element)
                )
            continue

        if len(elements) == 2 and elements[0] in PLAYBOOK_DYNAMIC_LABELS:
            try:
                del result[elements[0]][elements[1]]
            except Exception:
                raise PlaybookVerificationError(
                    "Dynamic key '{key}' does not exist and could not be excluded.".format(key=element)
                )
            continue

        raise PlaybookVerificationError(
            "Dynamic key '{key}' cannot be excluded from verification.".format(key=element)
        )

    return result


def execute_verification(snippet, encoded_signature):
    """Use GPG to verify the snippet.

    :param snippet: The (part of) Ansible playbook.
    :type snippet: dict
    :param encoded_signature: The base64-encoded signature.
    :type encoded_signature: str

    :returns: Result of the GPG verification and a hash of the snippet.
    :rtype: Tuple[..., bytes]
    """
    gpg = gnupg.GPG(gnupghome=constants.insights_core_lib_dir)
    serialized_snippet = serialize_playbook_snippet(snippet)
    snippet_hash = hash_playbook_snippet(serialized_snippet)
    decoded_signature = base64.b64decode(encoded_signature)

    # load public key
    get_public_key(gpg)

    fd, fn = tempfile.mkstemp()
    os.write(fd, decoded_signature)
    os.close(fd)

    result = gpg.verify_data(fn, snippet_hash)
    os.unlink(fn)

    return result, snippet_hash


def verify_playbook_snippet(snippet):
    """Verify the signature in a playbook.

    :param snippet: The (part of) Ansible playbook.
    :type snippet: dict

    :returns: Result of the GPG verification and a hash of the snippet.
    :rtype: Tuple[..., bytes]
    """
    if not isinstance(snippet.get("vars", None), dict):
        raise PlaybookVerificationError("The playbook snippet doesn't have a section 'vars'.")
    if snippet.get("vars", {}).get(PLAYBOOK_SIGNATURE_LABEL, None) is None:
        raise PlaybookVerificationError("The playbook snippet doesn't contain the Insights signature.")

    cleaned_snippet = exclude_dynamic_elements(snippet)  # type: dict
    encoded_signature = snippet["vars"][PLAYBOOK_SIGNATURE_LABEL]  # type: str

    return execute_verification(cleaned_snippet, encoded_signature)


def get_playbook_snippet_revocation_list(revoked_playbooks_yaml):
    """
    Load the list of revoked playbook snippet hashes from the egg.

    :param revoked_playbooks_yaml: The YAML containing revoked playbooks.
    :type revoked_playbooks_yaml: bytes
    :returns: Revocation entries in a form of `name:hash`.
    :rtype: dict[str, str]
    """
    try:
        # We know the structure of the YAML will stay like this:
        # > - name: revocation list
        # >   timestamp: ...
        # >   vars:
        # >     insights_signature_exclude: ...
        # >     insights_signature: !!binary | ...
        # >   revoked_playbooks:
        # >     - name: ...
        # >       hash: ...
        # >     - name: ...
        # >       hash: ...
        # There will never be more than one top-level object, we can safely do [0].
        revoked_playbooks = yaml.load(revoked_playbooks_yaml)[0]  # type: dict
    except Exception:
        raise PlaybookVerificationError("Could not load snippet revocation list.")

    verified, snippet_hash = verify_playbook_snippet(revoked_playbooks)

    if not verified:
        raise PlaybookVerificationError("List of revocation signatures is invalid.")

    revocation_list = revoked_playbooks.get("revoked_playbooks", [])  # type: list[str]
    return revocation_list


def verify(playbook):
    """Verify the GPG-signed Ansible playbook.

    :param playbook: Unverified playbook.
    :type playbook: dict
    :returns: Verified Ansible playbook.
    :rtype: dict
    :raises PlaybookVerificationError: An error occurred when trying to verify the playbook.
    """
    logger.info("Verifying Ansible playbook")

    if not playbook:
        raise PlaybookVerificationError("Empty playbooks cannot be verified.")

    revocation_list_file_content = pkgutil.get_data('insights', 'revoked_playbooks.yaml')  # type: bytes
    revocation_list = get_playbook_snippet_revocation_list(revocation_list_file_content)  # type: dict[str, str]

    name = playbook.get("name", "NAME UNAVAILABLE")
    verified, playbook_hash = verify_playbook_snippet(playbook)  # type: ..., str

    if not verified:
        raise PlaybookVerificationError(message="Template '{0}' has invalid signature".format(name))

    for revoked_item in revocation_list:
        if playbook_hash == bytearray.fromhex(revoked_item['hash']):
            raise PlaybookVerificationError(message="Template '{0}' is on the revoked list.".format(name))

    logger.info("All templates in the Ansible playbook were verified.")
    return playbook
