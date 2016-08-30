import re
import os
import logging
from collections import defaultdict
from falafel.config.static import get_config
from falafel.config import AnalysisTarget, META_FILE_LIST, CommandSpec

logger = logging.getLogger(__name__)


class SpecMapper(object):
    """
    This class wraps a tarfile-like object with spec mapping of names.
    """

    def __init__(self, tf_object, data_spec_config=None):
        self.tf = tf_object
        self.all_names = self.tf.getnames()
        self.root = self._determine_root()
        logger.debug("SpecMapper.root: %s", self.root)
        self.data_spec_config = data_spec_config if data_spec_config else get_config()
        self.analysis_target = None
        self.symbolic_files = defaultdict(list)
        self._determine_analysis_target()
        self.create_symbolic_file_list()

    def _determine_root(self):
        multi_node = any(["metadata.json" in name for name in self.all_names])
        if multi_node:
            root = os.path.commonprefix([p for p in self.all_names])
        else:
            root = os.path.commonprefix([p for p in self.all_names if len(p) > 2])

        return root.rstrip("/") + "/"

    def _get_first_matching(self, pattern):
        for match in filter(
                re.compile(self.root + "?" + pattern + "$").match,
                self.all_names):
            return match

    def _determine_analysis_target(self):
        path = self._get_first_matching(META_FILE_LIST["analysis_target"])
        if path:
            section = self.get_content(path, symbolic=False)[0].strip()
            self.analysis_target = AnalysisTarget.get_class_for_section_name(section)

    def _extend_symbolic_files(self, symbolic_name, matches):
        if matches:
            self.symbolic_files[symbolic_name].extend(matches)

    def add_files(self, file_map):
        for symbolic_name, spec_group in file_map.iteritems():
            for spec in spec_group.get_all_specs():  # Usually just one item in paths
                r = spec.get_regex(prefix=self.root,
                                   analysis_target=self.analysis_target)
                match_func = r.match
                logging.debug("Matching [%s] with [%s]", symbolic_name, r.pattern)
                matches = filter(match_func, self.all_names)
                if matches:
                    # In order to prevent matching *dumb* symlinks in some
                    # archive formats, we are going to filter out symlinks when
                    # calculating matches for CommandSpecs
                    if isinstance(spec, CommandSpec):
                        matches = filter(lambda n: not self.tf.issym(n), matches)

                    # We should never match a directory
                    matches = filter(lambda n: not self.tf.isdir(n), matches)

                    if not matches:
                        continue
                    # In order to prevent accidental duplication when matching
                    # files, we only allow the first matched file to be added
                    # to the working set for non-pattern file specs.
                    if not spec.is_multi_output() and len(matches) > 1:
                        logger.debug("Non multi-output file had multiple matches: %s", matches)
                        self._extend_symbolic_files(symbolic_name, [matches[0]])
                    else:
                        self._extend_symbolic_files(symbolic_name, matches)
                    break  # only add the first matching pattern

    def _add_meta_files(self):
        for symbolic_name, suffix in META_FILE_LIST.items():
            self._extend_symbolic_files(symbolic_name, [self._get_first_matching(suffix)])

    def create_symbolic_file_list(self):
        self.add_files(self.data_spec_config.get_spec_lists())
        if not self.analysis_target:
            self.add_files(self.data_spec_config.get_meta_specs())
        else:
            self._add_meta_files()

    def get_content(self, path, split=True, symbolic=True, default=""):
        """Returns file content from path, where path is the full pathname inside
        the archive"""
        if symbolic:
            path = self.symbolic_files.get(path, [""])[0]
        content = self.tf.extractfile(path) if path in self.all_names else default
        return list(content.splitlines()) if split else content

    def exists(self, path, symbolic=True):
        return path in self.symbolic_files if symbolic else path in self.all_names
