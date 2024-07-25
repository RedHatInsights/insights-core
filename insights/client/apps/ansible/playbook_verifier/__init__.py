import base64
import copy
import hashlib
import logging
import os
import pkgutil
import sys
import tempfile

import six

import insights.client.apps.ansible
from insights.client.apps.ansible.playbook_verifier.serializer import PlaybookSerializer
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
logging.getLogger('insights.client.apps.ansible.playbook_verifier.contrib').setLevel(logging.INFO)


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


def normalize_play_py2(play):
    """In Python 2, get rid of any default unicode values.

    :param play: The Ansible play.
    :type play: dict | yaml.comments.CommentedMap

    :returns: Play with Unicode characters removed.
    :rtype: CommentedMap
    """
    result = CommentedMap()
    for key, value in play.iteritems():
        if isinstance(value, CommentedMap):
            result[key] = CommentedMap(normalize_play_py2(value))
            continue

        if isinstance(value, CommentedSeq):
            new_sequence = CommentedSeq()
            for item in value:
                if isinstance(item, six.text_type):
                    new_sequence.append(item.encode('ascii', 'ignore'))
                    continue
                if isinstance(item, CommentedMap):
                    new_sequence.append(normalize_play_py2(item))
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


def serialize_play(play):
    """Convert the play object to bytes.

    :param play: The Ansible play.
    :type play: dict
    :returns: Serialized play.
    :rtype: bytes
    """
    if six.PY2:
        return str(normalize_play_py2(play)).encode("utf-8")
    if sys.version_info < (3, 12):
        return str(play).encode("utf-8")
    return PlaybookSerializer.serialize(play).encode("utf-8")


def hash_play(serialized_play):
    """Create SHA256 hash of a play.

    :param serialized_play: The Ansible play.
    :type serialized_play: bytes
    :returns: Hashed play.
    :rtype: bytes
    """
    sha = hashlib.sha256()
    sha.update(serialized_play)
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


def exclude_dynamic_elements(play):
    """Remove dynamic elements from the Ansible play.

    Some parts of the Ansible play are dynamic (e.g. host systems) and cannot be signed,
    because the signature would have to be unique for every play that is generated.

    This function removes these variable sections.

    :returns: New play dictionary without the unwanted values.
    :rtype: dict

    :raises PlaybookVerificationError:
    """
    if 'insights_signature_exclude' not in play.get('vars', {}):
        raise PlaybookVerificationError(
            "Play does not have the key 'vars/insights_signature_exclude', "
            "dynamic exclusion cannot be performed."
        )

    exclusions = play['vars']['insights_signature_exclude'].split(',')  # type: list[str]
    result = copy.deepcopy(play)  # type: dict[str, ...]

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


def execute_verification(play, encoded_signature):
    """Use GPG to verify the play.

    :param play: The Ansible play.
    :type play: dict
    :param encoded_signature: The base64-encoded signature.
    :type encoded_signature: str

    :returns: Result of the GPG verification and a hash of the play.
    :rtype: Tuple[..., bytes]
    """
    play_name = play.get("name", "unnamed")  # type: str
    logger.debug("Play '{play_name}' is being validated".format(play_name=play_name))

    gpg = gnupg.GPG(gnupghome=constants.insights_core_lib_dir)
    serialized_play = serialize_play(play)
    play_hash = hash_play(serialized_play)
    decoded_signature = base64.b64decode(encoded_signature)

    # load public key
    get_public_key(gpg)

    fd, fn = tempfile.mkstemp()
    os.write(fd, decoded_signature)
    os.close(fd)

    result = gpg.verify_data(fn, play_hash)
    os.unlink(fn)

    logger.debug("Play '{play_name}' validation result: valid={valid}, status={status}".format(
        play_name=play_name, valid=result.valid, status=result.status
    ))
    return result, play_hash


def verify_play(play):
    """Verify the signature in a play.

    :param play: The Ansible play.
    :type play: dict

    :returns: Result of the GPG verification and a hash of the play.
    :rtype: Tuple[..., bytes]
    """
    if not isinstance(play.get("vars", None), dict):
        raise PlaybookVerificationError("Play doesn't have a section 'vars'.")
    if play.get("vars", {}).get(PLAYBOOK_SIGNATURE_LABEL, None) is None:
        raise PlaybookVerificationError("Play doesn't contain the Insights signature.")

    cleaned_play = exclude_dynamic_elements(play)  # type: dict
    encoded_signature = play["vars"][PLAYBOOK_SIGNATURE_LABEL]  # type: str

    return execute_verification(cleaned_play, encoded_signature)


def get_play_revocation_list(revoked_plays_yaml):
    """
    Load the list of revoked play hashes from the egg.

    :param revoked_plays_yaml: The YAML containing hashes of revoked plays.
    :type revoked_plays_yaml: bytes
    :returns: Revocation entries in a form of `name:hash`.
    :rtype: list[dict[str, str]]
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
        revoked_plays = yaml.load(revoked_plays_yaml)[0]  # type: dict
    except Exception:
        raise PlaybookVerificationError("Could not load play revocation list.")

    verified, _ = verify_play(revoked_plays)

    if not verified:
        raise PlaybookVerificationError("List of revocation signatures is invalid.")

    revocation_list = revoked_plays.get("revoked_playbooks", [])  # type: list[str]
    return revocation_list


def verify(play):
    """Verify the GPG-signed Ansible play.

    :param play: Unverified Ansible play.
    :type play: dict
    :returns: Verified Ansible play.
    :rtype: dict
    :raises PlaybookVerificationError: An error occurred when trying to verify the play.
    """
    play_name = play.get("name", "unnamed")  # type: str
    logger.info("Play '{name}' is being verified.".format(name=play_name))

    if not play:
        raise PlaybookVerificationError("Empty plays cannot be verified.")

    revocation_list_file_content = pkgutil.get_data('insights', 'revoked_playbooks.yaml')  # type: bytes
    revocation_list = get_play_revocation_list(revocation_list_file_content)  # type: list[dict[str, str]]
    logger.debug("List of revoked playbooks was loaded.")

    verified, play_hash = verify_play(play)  # type: ..., str

    if not verified:
        raise PlaybookVerificationError(message="Play '{0}' has invalid signature".format(play_name))

    for revoked_item in revocation_list:
        if play_hash == bytearray.fromhex(revoked_item['hash']):
            raise PlaybookVerificationError(message="Play '{0}' is on the revoked list.".format(play_name))

    logger.info("Play '{name}' passed verification.".format(name=play_name))
    return play
