import os
import six
import copy
import base64
import tempfile
import pkgutil
import hashlib
import insights.client.apps.ansible
from logging import getLogger
from insights.client.apps.ansible.playbook_verifier.contrib import gnupg
from insights.client.apps.ansible.playbook_verifier.contrib.ruamel_yaml.ruamel import yaml
from insights.client.apps.ansible.playbook_verifier.contrib.ruamel_yaml.ruamel.yaml.comments import CommentedMap, CommentedSeq
from insights.client.apps.ansible.playbook_verifier.contrib.ruamel_yaml.ruamel.yaml.scalarint import ScalarInt
from insights.client.constants import InsightsConstants as constants

__all__ = ("load_playbook_yaml", "verify", "PlaybookVerificationError")

SIGKEY = 'insights_signature'
PUBLIC_KEY_PATH = pkgutil.get_data(insights.client.apps.ansible.__name__, 'playbook_verifier/public.gpg')    # Update this when we have the key generated
EXCLUDABLE_VARIABLES = ['hosts', 'vars']

logger = getLogger(__name__)

yaml = yaml.YAML(typ='rt')
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.default_flow_style = False
yaml.preserve_quotes = True
yaml.width = 200


class PlaybookVerificationError(Exception):
    """
    Exception raised when playbook verification fails

    Attributes:
        playbook -- stringified playbook yaml from stdin
        message -- explanation of why verification failed
    """

    def __init__(self, message="PLAYBOOK VALIDATION FAILED"):
        self.message = message
        super(PlaybookVerificationError, self).__init__(self.message)

    def __str__(self):
        return self.message


def decodeSignature(encodedSignature):
    try:
        decodedSignature = base64.b64decode(encodedSignature)
        return decodedSignature
    except:
        raise PlaybookVerificationError(message='VERIFICATION FAILED: Error Decoding Signature')


def hash_playbook_snippet(snippet):
    """Create SHA256 hash of a playbook snippet.

    :param snippet: The (part of) Ansible playbook.
    :type snippet: dict
    :returns: Hashed snippet.
    :rtype: bytes
    """
    sha = hashlib.sha256()
    if six.PY2:
        serialized = str(normalize_snippet(snippet)).encode("utf-8")
    else:
        serialized = str(snippet).encode("utf-8")

    sha.update(serialized)
    return sha.digest()


def get_public_key(gpg):
    """Import public GPG key.

    :param gpg: Path to the GPG key.
    :type gpg: gnupg.GPG
    :returns: Import result
    :rtype: ...
    """
    if not PUBLIC_KEY_PATH:
        raise PlaybookVerificationError(message="PUBLIC KEY IMPORT ERROR: Public key file not found")

    public_key = PUBLIC_KEY_PATH
    import_results = gpg.import_keys(public_key)
    if import_results.count < 1:
        raise PlaybookVerificationError(message="PUBLIC KEY NOT IMPORTED: Public key import failed")

    return import_results


def exclude_dynamic_elements(snippet):
    """Remove dynamic elements from the Ansible playbook snippet.

    Some parts of the Ansible playbook are dynamic (e.g. host systems) and cannot be signed,
    because the signature would have to be unique for every playbook that is generated.

    This function removes these variable sections.

    :returns: New playbook dictionary without the unwanted values.
    :rtype: dict
    """
    if 'insights_signature_exclude' not in snippet['vars']:
        raise PlaybookVerificationError(message='EXCLUDE MISSING: the insights_signature_exclude var does not exist.')

    exclusions = snippet['vars']['insights_signature_exclude'].split(',')

    for element in exclusions:
        element = element.split('/')

        # remove empty strings
        element = [string for string in element if string != '']

        if len(element) == 1 and element[0] in EXCLUDABLE_VARIABLES and element[0] in snippet.keys():
            del snippet[element[0]]
        elif len(element) == 2 and element[0] in EXCLUDABLE_VARIABLES:
            try:
                del snippet[element[0]][element[1]]
            except:
                raise PlaybookVerificationError(message='INVALID FIELD: the variable {0} defined in insights_signature_exclude does not exist.'.format(element))
        else:
            raise PlaybookVerificationError(message='INVALID EXCLUSION: the variable {0} is not a valid exclusion.'.format(element))

    return snippet


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
    snippet_hash = hash_playbook_snippet(snippet)
    decoded_signature = decodeSignature(encoded_signature)

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
    :rtype: Tuple[crypto.GPGCommandResult, bytes]
    """
    if 'vars' not in snippet.keys():
        raise PlaybookVerificationError(message='VERIFICATION FAILED: Vars field not found')
    elif snippet['vars'] is None:
        raise PlaybookVerificationError(message='VERIFICATION FAILED: Empty vars field')
    elif SIGKEY not in snippet['vars']:
        raise PlaybookVerificationError(message='VERIFICATION FAILED: Signature not found')

    encoded_signature = snippet['vars'][SIGKEY]
    snippet_copy = copy.deepcopy(snippet)

    snippet_copy = exclude_dynamic_elements(snippet_copy)

    return execute_verification(snippet_copy, encoded_signature)


def get_playbook_snippet_revocation_list():
    """
    Load the list of revoked playbook snippet hashes from the egg.

    :returns: Revocation entries in a form of `name:hash`.
    :rtype: dict[str, str]
    """
    try:
        # Import revoked list yaml.  The yaml is structured as a list of lists, so we can reuse the playbook signing and
        # verification code.  There will only ever be one list, so we just grab the first element...
        revoked_playbooks = yaml.load(pkgutil.get_data('insights', 'revoked_playbooks.yaml'))[0]

    except Exception:
        raise PlaybookVerificationError(message='VERIFICATION FAILED: Error loading revocation list')

    # verify the list signature!
    verified, snippet_hash = verify_playbook_snippet(revoked_playbooks)

    if not verified:
        raise PlaybookVerificationError(message='VERIFICATION FAILED: Revocation list signature invalid')

    revocation_list = revoked_playbooks.get('revoked_playbooks', [])
    return revocation_list


def verify(playbook, skip_verify=False):
    """
    Verify the signed playbook.

    :param playbook: Unverified playbook.
    :type playbook: list[dict]
    :returns: "verified" playbook
    :rtype: dict
    :raises PlaybookVerificationError:
    """
    logger.info('Playbook Verification has started')

    if not skip_verify:
        if not playbook:
            raise PlaybookVerificationError(message="PLAYBOOK VERIFICATION FAILURE: Playbook is empty")

        revocation_list = get_playbook_snippet_revocation_list()

        for snippet in playbook:
            verified, snippet_hash = verify_playbook_snippet(snippet)

            if not verified:
                name = snippet.get('name', 'NAME UNAVAILABLE')
                raise PlaybookVerificationError(message="SIGNATURE NOT VALID: Template [name: {0}] has invalid signature".format(name))

            # check if snippet_hash is on the revoked list
            for revokedItem in revocation_list:
                if snippet_hash == bytearray.fromhex(revokedItem['hash']):
                    raise PlaybookVerificationError(message="REVOKED PLAYBOOK: Template is on the revoked list [name: {0}]".format(revokedItem['name']))

    logger.info('All templates successfully validated')
    return playbook


def load_playbook_yaml(playbook):
    """
    Load playbook yaml using current yaml library implementation
        output: playbook yaml
    """
    try:
        playbook_yaml = yaml.load(playbook)
        return playbook_yaml
    except Exception:
        raise PlaybookVerificationError(message="PLAYBOOK VERIFICATION FAILURE: Failed to load playbook yaml because yaml is not valid")


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
