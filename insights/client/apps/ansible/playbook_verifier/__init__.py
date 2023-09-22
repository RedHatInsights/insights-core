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

__all__ = ("loadPlaybookYaml", "verify", "PlaybookVerificationError")

SIGKEY = 'insights_signature'
PUBLIC_KEY_FOLDER = pkgutil.get_data(insights.client.apps.ansible.__name__, 'playbook_verifier/public.gpg')    # Update this when we have the key generated
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


def createSnippetHash(snippet):
    """
    Function that creates and returns a hash of the snippet given to the function.
        output: snippetHash (bytes)
    """
    snippetHash = hashlib.sha256()
    if six.PY2:
        normalizedSnippet = normalizeSnippet(snippet)
        serializedSnippet = str(normalizedSnippet).encode("UTF-8")
    else:
        serializedSnippet = str(snippet).encode("UTF-8")
    snippetHash.update(serializedSnippet)

    return snippetHash.digest()


def getPublicKey(gpg):
    if not PUBLIC_KEY_FOLDER:
        raise PlaybookVerificationError(message="PUBLIC KEY IMPORT ERROR: Public key file not found")

    publicKey = PUBLIC_KEY_FOLDER
    importResults = gpg.import_keys(publicKey)
    if (importResults.count < 1):
        raise PlaybookVerificationError(message="PUBLIC KEY NOT IMPORTED: Public key import failed")

    return importResults


def excludeDynamicElements(snippet):
    if 'insights_signature_exclude' not in snippet['vars']:
        raise PlaybookVerificationError(message='EXCLUDE MISSING: the insights_signature_exclude var does not exist.')

    exclusions = snippet['vars']['insights_signature_exclude'].split(',')

    for element in exclusions:
        element = element.split('/')

        # remove empty strings
        element = [string for string in element if string != '']

        if (len(element) == 1 and element[0] in EXCLUDABLE_VARIABLES and element[0] in snippet.keys()):
            del snippet[element[0]]
        elif (len(element) == 2 and element[0] in EXCLUDABLE_VARIABLES):
            try:
                del snippet[element[0]][element[1]]
            except:
                raise PlaybookVerificationError(message='INVALID FIELD: the variable {0} defined in insights_signature_exclude does not exist.'.format(element))
        else:
            raise PlaybookVerificationError(message='INVALID EXCLUSION: the variable {0} is not a valid exclusion.'.format(element))

    return snippet


def executeVerification(snippet, encodedSignature):
    gpg = gnupg.GPG(gnupghome=constants.insights_core_lib_dir)
    snippetHash = createSnippetHash(snippet)
    decodedSignature = decodeSignature(encodedSignature)

    # load public key
    getPublicKey(gpg)

    fd, fn = tempfile.mkstemp()
    os.write(fd, decodedSignature)
    os.close(fd)

    result = gpg.verify_data(fn, snippetHash)
    os.unlink(fn)

    return result, snippetHash


def verifyPlaybookSnippet(snippet):
    if ('vars' not in snippet.keys()):
        raise PlaybookVerificationError(message='VERIFICATION FAILED: Vars field not found')
    elif (snippet['vars'] is None):
        raise PlaybookVerificationError(message='VERIFICATION FAILED: Empty vars field')
    elif (SIGKEY not in snippet['vars']):
        raise PlaybookVerificationError(message='VERIFICATION FAILED: Signature not found')

    encodedSignature = snippet['vars'][SIGKEY]
    snippetCopy = copy.deepcopy(snippet)

    snippetCopy = excludeDynamicElements(snippetCopy)

    return executeVerification(snippetCopy, encodedSignature)


def getRevocationList():
    """
    Load the list of revoked playbook snippet hashes from the egg

    Returns:
        dictionary of revocation list entries (name, hash)
    """
    try:
        # Import revoked list yaml.  The yaml is structured as a list of lists, so we can reuse the playbook signing and
        # verification code.  There will only ever be one list, so we just grab the first element...
        revoked_playbooks = yaml.load(pkgutil.get_data('insights', 'revoked_playbooks.yaml'))[0]

    except Exception:
        raise PlaybookVerificationError(message='VERIFICATION FAILED: Error loading revocation list')

    # verify the list signature!
    verified, snippetHash = verifyPlaybookSnippet(revoked_playbooks)

    if not verified:
        raise PlaybookVerificationError(message='VERIFICATION FAILED: Revocation list signature invalid')

    revocationList = revoked_playbooks.get('revoked_playbooks', [])
    return revocationList


def verify(playbook, skipVerify=False):
    """
    Verify the signed playbook.

    Input: unverified playbook (dictionary format)
    Output: "verified" playbook (dictionary format)
    Error: Playbook Verification failure / Playbook Signature not found.
    """
    logger.info('Playbook Verification has started')

    if not skipVerify:
        if not playbook:
            raise PlaybookVerificationError(message="PLAYBOOK VERIFICATION FAILURE: Playbook is empty")

        revocationList = getRevocationList()

        for snippet in playbook:
            verified, snippetHash = verifyPlaybookSnippet(snippet)

            if not verified:
                name = snippet.get('name', 'NAME UNAVAILABLE')
                raise PlaybookVerificationError(message="SIGNATURE NOT VALID: Template [name: {0}] has invalid signature".format(name))

            # check if snippetHash is on the revoked list
            for revokedItem in revocationList:
                if snippetHash == bytearray.fromhex(revokedItem['hash']):
                    raise PlaybookVerificationError(message="REVOKED PLAYBOOK: Template is on the revoked list [name: {0}]".format(revokedItem['name']))

    logger.info('All templates successfully validated')
    return playbook


def loadPlaybookYaml(playbook):
    """
    Load playbook yaml using current yaml library implementation
        output: playbook yaml
    """
    try:
        playbookYaml = yaml.load(playbook)
        return playbookYaml
    except:
        raise PlaybookVerificationError(message="PLAYBOOK VERIFICATION FAILURE: Failed to load playbook yaml because yaml is not valid")


def normalizeSnippet(snippet):
    """
    Normalize python2 snippet and get rid of any default unicode values
        output: normalized snippet
    """
    new = CommentedMap()
    for key, value in snippet.iteritems():
        if isinstance(value, CommentedMap):
            new[key] = CommentedMap(normalizeSnippet(value))
        elif isinstance(value, CommentedSeq):
            new_sequence = CommentedSeq()
            for item in value:
                if isinstance(item, six.text_type):
                    new_sequence.append(item.encode('ascii', 'ignore'))
                elif isinstance(item, CommentedMap):
                    new_sequence.append(normalizeSnippet(item))
                else:
                    new_sequence.append(item)
            new[key] = new_sequence
        elif isinstance(value, six.text_type):
            new[key] = value.encode('ascii', 'ignore')
        elif isinstance(value, ScalarInt):
            new[key] = int(value)
        else:
            new[key] = value

    return new
