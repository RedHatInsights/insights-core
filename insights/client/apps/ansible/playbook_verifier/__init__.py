import os
import copy
import pickle
import base64
import requests
import gnupg
import tempfile
from logging import getLogger
from requests.exceptions import HTTPError
from insights.client.utilities import get_version_info

__all__ = ("verify", "PlaybookVerificationError")

SIGKEY = 'insights_signature'
PUBLIC_KEY_FOLDER = './insights/client/apps/ansible/playbook_verifier/public.gpg'    # Update this when we have the key generated
VERSIONING_URL = 'https://cloud.redhat.com/api/v1/static/egg_version'
EXCLUDABLE_VARIABLES = ['hosts', 'vars']

logger = getLogger(__name__)
gpg = gnupg.GPG(gnupghome='./insights/client/apps/ansible/playbook_verifier/gnupg')

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


def eggVersioningCheck(checkVersion):
    currentVersion = requests.get(VERSIONING_URL)
    currentVersion = currentVersion.text
    runningVersion = get_version_info()['core_version']

    if checkVersion:
        if currentVersion.strip() != runningVersion:
            raise PlaybookVerificationError(message="EGG VERSION ERROR: Current running egg is not the most recent version")

    return currentVersion


def getPublicKey():
    try:
        with open(PUBLIC_KEY_FOLDER, 'r') as keyFile:
            publicKey = keyFile.read()
            importResults = gpg.import_keys(publicKey)
            if (importResults.count < 1):
                raise PlaybookVerificationError(message="PUBLIC KEY NOT IMPORTED: Public key not imported from key file")

            return importResults
    except Exception as e:
        raise PlaybookVerificationError(message="PUBLIC KEY IMPORT ERROR: {0}".format(e))


def excludeDynamicElements(snippet):
    exclusions = snippet['vars']['insights_signature_exclude'].split(',')

    for element in exclusions:
        element = element.split('/')

        # remove empty strings
        element = [string for string in element if string != '']

        if (len(element) == 1 and element[0] in EXCLUDABLE_VARIABLES):
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
    serializedSnippet = pickle.dumps(snippet)
    decodedSignature = base64.b64decode(encodedSignature)

    # load public key
    getPublicKey()

    fd, fn = tempfile.mkstemp()
    os.write(fd, decodedSignature)
    os.close(fd)

    result = gpg.verify_data(fn, serializedSnippet)
    os.unlink(fn)

    return result


def verifyPlaybookSnippet(snippet):
    if ('vars' not in snippet.keys()):
        raise PlaybookVerificationError(message='VARS FIELD NOT FOUND: Verification failed')
    elif (SIGKEY not in snippet['vars']):
        raise PlaybookVerificationError(message='SIGNATURE NOT FOUND: Verification failed')

    encodedSignature = snippet['vars'][SIGKEY]
    snippetCopy = copy.deepcopy(snippet)

    snippetCopy = excludeDynamicElements(snippetCopy)

    return executeVerification(snippetCopy, encodedSignature)


def verify(playbook, checkVersion = True, skipVerify = False):
    """
    Verify the signed playbook.

    Input: unverified playbook (dictionary format)
    Output: "verified" playbook (dictionary format)
    Error: Playbook Verification failure / Playbook Signature not found.
    """
    logger.info('Playbook Verification has started')

    # Egg Version Check
    eggVersioningCheck(checkVersion)

    if not skipVerify:
        for snippet in playbook:
            verified = verifyPlaybookSnippet(snippet)

            if not verified:
                raise PlaybookVerificationError(message="SIGNATURE NOT VALID: Template [name: {0}] has invalid signature".format(snippet['name']))

    logger.info('All templates successfully validated')
    return playbook
