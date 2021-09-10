"""
Handle adding files and preparing the archive for upload
"""
from __future__ import absolute_import
import time
import os
import shutil
import subprocess
import shlex
import logging
import tempfile
import re
import atexit
from tempfile import NamedTemporaryFile
from subprocess import Popen, PIPE
from .collection_rules import InsightsUploadConf
from .constants import InsightsConstants as constants

from .utilities import determine_hostname, _expand_paths, write_data_to_file, write_rhsm_facts
from .insights_spec import InsightsFile, InsightsCommand
from ..contrib.soscleaner import SOSCleaner

logger = logging.getLogger(__name__)
# python 2.7
SOSCLEANER_LOGGER = logging.getLogger('soscleaner')
SOSCLEANER_LOGGER.setLevel(logging.ERROR)
# python 2.6
SOSCLEANER_LOGGER = logging.getLogger('insights-client.soscleaner')
SOSCLEANER_LOGGER.setLevel(logging.ERROR)


def _process_content_redaction(filepath, exclude, regex=False):
    '''
    Redact content from a file, based on
    /etc/insights-client/.exp.sed and and the contents of "exclude"

    filepath    file to modify
    exclude     list of strings to redact
    regex       whether exclude is a list of regular expressions

    Returns the file contents with the specified data removed
    '''
    logger.debug('Processing %s...', filepath)

    # password removal
    sedcmd = Popen(['sed', '-rf', constants.default_sed_file, filepath], stdout=PIPE)
    # patterns removal
    if exclude:
        exclude_file = NamedTemporaryFile()
        exclude_file.write("\n".join(exclude).encode('utf-8'))
        exclude_file.flush()
        if regex:
            flag = '-E'
        else:
            flag = '-F'
        grepcmd = Popen(['grep', '-v', flag, '-f', exclude_file.name], stdin=sedcmd.stdout, stdout=PIPE)
        sedcmd.stdout.close()
        stdout, stderr = grepcmd.communicate()
        logger.debug('Process status: %s', grepcmd.returncode)
    else:
        stdout, stderr = sedcmd.communicate()
        logger.debug('Process status: %s', sedcmd.returncode)
    logger.debug('Process stderr: %s', stderr)
    return stdout


class InsightsArchive(object):
    """
    This class is an interface for adding command output
    and files to the insights archive, as well as redaction
    and obfuscation of the archive prior to upload.

    Attributes:
        config          - an InsightsConfig object
        tmp_dir         - a temporary directory in /var/tmp
        archive_dir     - location to collect archive data inside tmp_dir
        archive_tmp_dir - a temporary directory to write the final archive file
        archive_name    - filename of the archive and archive_dir
        cmd_dir         - insights_commands directory inside archive_dir
        compressor      - tar compression flag to use
        tar_file        - path of the final archive file
        rm_conf         - contents of the denylist
        hostname_path   - location of the file containing the
                          hostname in the archive, provided by the data collector
    """
    def __init__(self, config, rm_conf=None):
        """
        Initialize the Insights Archive
        """
        self.config = config
        # input this to core collector as `tmp_path`
        self.tmp_dir = tempfile.mkdtemp(prefix='/var/tmp/')

        # we don't really need this anymore...
        self.archive_tmp_dir = tempfile.mkdtemp(prefix='/var/tmp/')

        self.archive_name = ("insights-%s-%s" %
                             (determine_hostname(),
                              time.strftime("%Y%m%d%H%M%S")))

        # lazy create these, only if needed when certain
        #   functions are called
        # classic collection and compliance needs these
        # core collection will set "archive_dir" on its own
        self.archive_dir = None
        self.cmd_dir = None

        self.compressor = config.compressor
        self.tar_file = None

        if rm_conf is not None:
            self.rm_conf = rm_conf
        else:
            # if not provided, initialize it from config (need this for non-advisor collections)
            self.rm_conf = InsightsUploadConf(config).get_rm_conf()
        self.hostname_path = None

        atexit.register(self.cleanup_tmp)

    def create_archive_dir(self):
        """
        Create the archive directory if it is undefined or does not exist.
        """
        if self.archive_dir and os.path.exists(self.archive_dir):
            # attr defined and exists. move along
            return self.archive_dir

        archive_dir = os.path.join(self.tmp_dir, self.archive_name)
        if not os.path.exists(archive_dir):
            logger.debug('Creating archive directory %s...', archive_dir)
            os.makedirs(archive_dir, 0o700)
        self.archive_dir = archive_dir
        return self.archive_dir

    def create_command_dir(self):
        """
        Create the "insights_commands" dir
        """
        self.create_archive_dir()
        cmd_dir = os.path.join(self.archive_dir, "insights_commands")
        logger.debug('Creating command directory %s...', cmd_dir)
        if not os.path.exists(cmd_dir):
            os.makedirs(cmd_dir, 0o700)
        self.cmd_dir = cmd_dir
        return self.cmd_dir

    def get_full_archive_path(self, path):
        """
        Returns the full archive path
        """
        self.create_archive_dir()
        return os.path.join(self.archive_dir, path.lstrip('/'))

    def _copy_file(self, path):
        """
        Copy just a single file
        """
        full_path = self.get_full_archive_path(path)
        # Try to make the dir, eat exception if it fails
        try:
            os.makedirs(os.path.dirname(full_path))
        except OSError:
            pass
        logger.debug("Copying %s to %s", path, full_path)
        shutil.copyfile(path, full_path)
        return path

    def copy_file(self, path):
        """
        Copy a single file or regex, creating the necessary directories
        """
        if "*" in path:
            paths = _expand_paths(path)
            if paths:
                for path in paths:
                    self._copy_file(path)
        else:
            if os.path.isfile(path):
                return self._copy_file(path)
            else:
                logger.debug("File %s does not exist", path)
                return False

    def copy_dir(self, path):
        """
        Recursively copy directory
        """
        self.create_archive_dir()
        for directory in path:
            if os.path.isdir(path):
                full_path = os.path.join(self.archive_dir, directory.lstrip('/'))
                logger.debug("Copying %s to %s", directory, full_path)
                shutil.copytree(directory, full_path)
            else:
                logger.debug("Not a directory: %s", directory)
        return path

    def get_compression_flag(self, compressor):
        return {
            "gz": "z",
            "xz": "J",
            "bz2": "j",
            "none": ""
        }.get(compressor, "z")

    def create_tar_file(self):
        """
        Generate the archive output.
        "create_tar_file" is an anachronism provided for compatibility.
        Perform redaction, and obfuscation if required.

        Returns a path.
        If --output-dir is specified, return the tmp path.
        Otherwise run tar and return the tar file.

        default:
            path to generated tarfile
        conf.obfuscate==True:
            path to generated tarfile, scrubbed by soscleaner
        conf.output_dir:
            path to a generated directory
        conf.obfuscate==True && conf.output_dir:
            path to generated directory, scubbed by soscleaner
        """
        self._redact()
        if self.config.obfuscate:
            # run obfuscation
            soscleaner = self._obfuscate()
            # generate RHSM facts at this point
            write_rhsm_facts(self.config, soscleaner.hashed_fqdn, soscleaner.ip_report)

            if self.config.output_dir:
                # return the entire soscleaner dir
                #   see additions to soscleaner.SOSCleaner.clean_report
                #   for details
                return soscleaner.dir_path
            else:
                # return the generated soscleaner archive
                self.tar_file = soscleaner.archive_path
                return soscleaner.archive_path

        if self.config.output_dir:
            # return the directory
            return self.archive_dir

        # create tar file
        if not self.archive_tmp_dir:
            # we should never get here but bail out if we do
            raise RuntimeError('Archive temporary directory not defined.')
        tar_file_name = os.path.join(self.archive_tmp_dir, self.archive_name)
        ext = "" if self.compressor == "none" else ".%s" % self.compressor
        tar_file_name = tar_file_name + ".tar" + ext
        logger.debug("Tar File: " + tar_file_name)
        return_code = subprocess.call(shlex.split("tar c%sfS %s -C %s ." % (
            self.get_compression_flag(self.compressor),
            tar_file_name, self.tmp_dir)),
            stderr=subprocess.PIPE)
        if (self.compressor in ["bz2", "xz"] and return_code != 0):
            logger.error("ERROR: %s compressor is not installed, cannot compress file", self.compressor)
            return None
        self.delete_archive_dir()
        logger.debug("Tar File Size: %s", str(os.path.getsize(tar_file_name)))
        self.tar_file = tar_file_name
        return tar_file_name

    def delete_tmp_dir(self):
        """
        Delete the entire tmp dir
        """
        if self.tmp_dir:
            logger.debug("Deleting: " + self.tmp_dir)
            shutil.rmtree(self.tmp_dir, True)

    def delete_archive_dir(self):
        """
        Delete the entire archive dir
        """
        if self.archive_dir:
            logger.debug("Deleting: " + self.archive_dir)
            shutil.rmtree(self.archive_dir, True)

    def delete_archive_file(self):
        """
        Delete the directory containing the constructed archive
        """
        if self.archive_tmp_dir:
            logger.debug("Deleting %s", self.archive_tmp_dir)
            shutil.rmtree(self.archive_tmp_dir, True)

    def add_to_archive(self, spec):
        '''
        Add files and commands to archive
        Use InsightsSpec.get_output() to get data
        '''
        ab_regex = [
            "^timeout: failed to run command .+: No such file or directory$",
            "^Missing Dependencies:"
        ]
        if isinstance(spec, InsightsCommand):
            archive_path = os.path.join(self.cmd_dir, spec.archive_path.lstrip('/'))
        if isinstance(spec, InsightsFile):
            archive_path = self.get_full_archive_path(spec.archive_path.lstrip('/'))
        output = spec.get_output()
        if output and not any(re.search(rg, output) for rg in ab_regex):
            write_data_to_file(output, archive_path)

    def add_metadata_to_archive(self, metadata, meta_path):
        '''
        Add metadata to archive
        '''
        archive_path = self.get_full_archive_path(meta_path.lstrip('/'))
        write_data_to_file(metadata, archive_path)

    def cleanup_tmp(self):
        '''
        Only used during built-in collection.
        Delete archive and tmp dirs on exit unless --keep-archive is specified
            and tar_file exists.
        '''
        if self.config.keep_archive and self.tar_file:
            if self.config.no_upload:
                logger.info('Archive saved at %s', self.tar_file)
            else:
                logger.info('Insights archive retained in %s', self.tar_file)
            if self.config.obfuscate:
                return  # return before deleting tmp_dir
        else:
            self.delete_archive_file()
        self.delete_tmp_dir()

    def _redact(self):
        '''
        Perform data redaction (password sed command and patterns),
        on an InsightsArchive. The files under self.archive_dir
        will have redaction applied based on the values in self.rm_conf.

        Raises RuntimeError when self.archive_dir is invalid
        '''
        logger.debug('Running content redaction...')

        # normalize path to prevent any ../ from happening
        searchpath = os.path.normpath(self.archive_dir)

        if not re.match(r'/var/tmp/\w+/insights-.+', searchpath):
            # sanity check to make sure we're only modifying
            #   our own stuff in temp
            # we should never get here but just in case
            raise RuntimeError('ERROR: invalid Insights archive temp path: %s' % searchpath)

        if self.rm_conf is None:
            self.rm_conf = {}
        exclude = None
        regex = False
        if self.rm_conf:
            try:
                exclude = self.rm_conf['patterns']
                if isinstance(exclude, dict) and exclude['regex']:
                    # if "patterns" is a dict containing a non-empty "regex" list
                    logger.debug('Using regular expression matching for patterns.')
                    exclude = exclude['regex']
                    regex = True
                logger.warn("WARNING: Skipping patterns defined in denylist configuration")
            except LookupError:
                # either "patterns" was undefined in rm conf, or
                #   "regex" was undefined in "patterns"
                exclude = None
        if not exclude:
            logger.debug('Patterns section of denylist configuration is empty.')

        for dirpath, dirnames, filenames in os.walk(searchpath):
            relative_dirpath = os.path.relpath(dirpath, start=searchpath)
            if relative_dirpath in constants.redact_skip_dirs:
                # skip the meta_data directory
                logger.debug("Ignoring directory %s", relative_dirpath)
            else:
                for f in filenames:
                    fullpath = os.path.join(dirpath, f)
                    relative_path = os.path.relpath(fullpath, start=searchpath)

                    if relative_path in constants.redact_skip_files:
                        # do not redact the ID files or other top-level data
                        logger.debug("Ignoring file %s", relative_path)
                    else:
                        redacted_contents = _process_content_redaction(fullpath, exclude, regex)
                        with open(fullpath, 'wb') as dst:
                            dst.write(redacted_contents)

    def _obfuscate(self):
        """
        Initialize a SOScleaner to obfuscate the archive contents.

        Returns a SOScleaner object.
        """
        if self.rm_conf and self.rm_conf.get('keywords'):
            logger.warn("WARNING: Skipping keywords defined in blacklist configuration")
        cleaner = SOSCleaner(quiet=True)
        clean_opts = CleanOptions(
            self.config, self.tmp_dir, self.rm_conf, self.hostname_path)
        cleaner.clean_report(clean_opts, self.archive_dir)
        if clean_opts.keyword_file is not None:
            os.remove(clean_opts.keyword_file.name)
        return cleaner


class CleanOptions(object):
    """
    Options for soscleaner
    """
    def __init__(self, config, tmp_dir, rm_conf, hostname_path):
        self.report_dir = tmp_dir
        self.domains = []
        self.files = []
        self.quiet = True
        self.keyword_file = None
        self.keywords = None
        self.no_tar_file = config.output_dir

        self.skip_files = constants.redact_skip_files
        self.skip_dirs = constants.redact_skip_dirs

        if rm_conf:
            try:
                keywords = rm_conf['keywords']
                self.keyword_file = NamedTemporaryFile(delete=False)
                self.keyword_file.write("\n".join(keywords).encode('utf-8'))
                self.keyword_file.flush()
                self.keyword_file.close()
                self.keywords = [self.keyword_file.name]
                logger.debug("Attmpting keyword obfuscation")
            except LookupError:
                pass

        if config.obfuscate_hostname:
            # default to its original location
            self.hostname_path = hostname_path or 'insights_commands/hostname'
        else:
            self.hostname_path = None
