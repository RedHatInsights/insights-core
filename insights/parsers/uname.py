"""
Uname - command ``uname -a``
============================

The ``Uname`` class reads the output of the ``uname -a`` command and
interprets it.  It also does a number of handy extra things, like deriving
the RHEL release from the kernel version.

Uname objects can also be compared by their kernel versions.

An example from the following ``uname -a`` output::

    Linux server1.example.com 2.6.32-504.el6.x86_64 #1 SMP Tue Sep 16 01:56:35 EDT 2014 x86_64 x86_64 x86_64 GNU/Linux

Example:

    >>> type(uname)
    <class 'insights.parsers.uname.Uname'>
    >>> uname.version
    '2.6.32'
    >>> uname.release
    '504.el6'
    >>> uname.arch
    'x86_64'
    >>> uname.nodename
    'server1.example.com'

Uname objects can be created from, and compared to, other Uname objects or
kernel strings::

    >>> early_rhel6 = Uname.from_kernel('2.6.32-71')
    >>> late_rhel6 = Uname.from_release('6.7')
    >>> late_rhel6 > early_rhel6
    True
    >>> early_rhel6 > '2.6.32-279.el6.x86_64'
    False

"""

from collections import namedtuple
from distutils.version import LooseVersion, StrictVersion
from .. import parser, CommandParser
from insights.core.context import Context
from insights.specs import Specs

rhel_release_map = {
    "2.4.21-4": "3.0",
    "2.4.21-9": "3.1",
    "2.4.21-15": "3.2",
    "2.4.21-20": "3.3",
    "2.4.21-27": "3.4",
    "2.4.21-32": "3.5",
    "2.4.21-37": "3.6",
    "2.4.21-40": "3.7",
    "2.4.21-47": "3.8",
    "2.4.21-50": "3.9",
    "2.6.9-5": "4.0",
    "2.6.9-11": "4.1",
    "2.6.9-22": "4.2",
    "2.6.9-34": "4.3",
    "2.6.9-42": "4.4",
    "2.6.9-55": "4.5",
    "2.6.9-67": "4.6",
    "2.6.9-78": "4.7",
    "2.6.9-89": "4.8",
    "2.6.9-100": "4.9",
    "2.6.18-8": "5.0",
    "2.6.18-53": "5.1",
    "2.6.18-92": "5.2",
    "2.6.18-128": "5.3",
    "2.6.18-164": "5.4",
    "2.6.18-194": "5.5",
    "2.6.18-238": "5.6",
    "2.6.18-274": "5.7",
    "2.6.18-308": "5.8",
    "2.6.18-348": "5.9",
    "2.6.18-371": "5.10",
    "2.6.18-398": "5.11",
    "2.6.18-400": "5.11",
    "2.6.18-402": "5.11",
    "2.6.18-404": "5.11",
    "2.6.18-408": "5.11",
    "2.6.32-71": "6.0",
    "2.6.32-131": "6.1",
    "2.6.32-220": "6.2",
    "2.6.32-279": "6.3",
    "2.6.32-358": "6.4",
    "2.6.32-431": "6.5",
    "2.6.32-504": "6.6",
    "2.6.32-573": "6.7",
    "2.6.32-642": "6.8",
    "2.6.32-696": "6.9",
    "2.6.32-754": "6.10",
    "3.10.0-123": "7.0",
    "3.10.0-229": "7.1",
    "3.10.0-327": "7.2",
    "3.10.0-514": "7.3",
    "3.10.0-693": "7.4",
    "3.10.0-862": "7.5",
    "3.10.0-957": "7.6"
}

release_to_kernel_map = dict((v, k) for k, v in rhel_release_map.items())
RedhatRelease = namedtuple("RedhatRelease", ("major", "minor"))


class UnameError(Exception):
    """
    Exception subclass for errors related to uname content data and the
    Uname class.

    This exception should not be caught by rules plugins unless it is necessary
    for the plugin to return a particular answer when a problem occurs with
    uname data.  If a plugin catches this exception it must reraise it so that
    the engine has the opportunity to handle it/log it as necessary.
    """

    def __init__(self, msg, uname_line):
        """Class constructor

        :Parameters:
            - `msg`: Specific description of the error that occurred.
            - `uname_line`: Uname content that was being evaluated with the error
              occurred.
        """
        super(UnameError, self).__init__(msg, uname_line)
        self.msg = msg
        self.uname_line = uname_line

    def __str__(self):
        return "{0}:'{1}'".format(self.msg, self.uname_line)


@parser(Specs.uname)
class Uname(CommandParser):
    """
    A utility class to parse uname content data and compare version and release
    information.

    The input is a uname content string.  The content is parsed into specific
    uname elements that are made available through instance variables.
    Operators are provided for comparison of version and release information.
    Uname content is expected to be in the format returned by the ``uname -a``
    command.  The following instance variables are provided by this class:

    - `kernel`: Provides an unparsed copy of the full version and release
      string provided in the uname content input.  No validation is performed
      on this information. Generally in the format ``#.#.#-#.#.#.el#.arch``.
    - `name`: The kernel name, usually ``Linux``.
    - `nodename`: Hostname of the computer where the uname command was
      executed.  This information may obfuscated for security.
    - `version`: The major identification number for the kernel release. It
      should be in the format ``#.#.#[.#]`` or a UnameError exception will be
      raised.
    - `release`: The minor identification number for the kernel release. This
      information is generally in the format #.#.#.el#, however this is not
      strictly enforced.  If the release.arch information cannot be reliably
      parsed then `release` and `release_arch` will be the same value.
    - `release_arch`: This is the `release` plus the kernel architecture
      information as provided in `arch`.
    - `arch`: This contains the kernel architecture information like ``x86_64``
      or `s390`.  A list of known architectures is provided by the global
      variable `KNOWN_ARCHITECTURES`.  This information is not always
      present in the uname content.
    - `ver_rel`: This is a combination of `version` and `release` in the format
      ``version-release``.
    - `rhel_release`: A list of two elements, the major and minor RHEL product
      release numbers.

    """
    keys = [
        'os',
        'hw_platform',
        'processor',
        'machine',
        'kernel_date',
        'kernel_type',
        'kernel',
        'name',
        'nodename',
        'version',
        'release',
        'release_arch',
        'arch',
        'ver_rel',
        'rhel_release',
        '_lv_release',
        '_rel_maj',
        '_sv_version',
        '_lv_version'
    ]

    defaults = dict.fromkeys(keys)

    def __init__(self, context):
        super(Uname, self).__init__(context)
        if not context:
            return
        data = dict(self.defaults)
        data.update(self.data)
        self.data = data
        for k, v in self.data.items():
            setattr(self, k, v)

    def parse_content(self, content):
        """
        Parses uname content into individual uname components.

        :Parameters:
            - `content`: Uname content from Insights to be parsed.

        :Exceptions:
            - `UnameError`: Raised when there are any errors evaluating
              the uname content.
        """
        # Remove extra whitespace prior to parsing, preserve original line
        if not content:
            raise UnameError('Empty uname line', '')

        data = {}
        uname_list = [line for line in content if line.startswith("Linux")]
        if not uname_list:
            raise UnameError("Uname string appears invalid", '')
        uname_line = uname_list[0]
        uname_parts = uname_line.split(' ')
        if len(uname_parts) < 3:
            raise UnameError("Uname string appears invalid", uname_line)
        else:
            data['kernel'] = uname_parts[2]
            data['name'] = uname_parts[0]
            data['nodename'] = uname_parts[1]
        has_arch = "el" not in data['kernel'].split(".")[-1]
        try:
            data = self.parse_nvr(data['kernel'], data, arch=has_arch)
        except UnameError as error:
            error.uname_line = uname_line
            raise error

        # Additional uname content parsing, may not be as reliable
        if len(uname_parts) >= 15:
            data['os'] = uname_parts[-1]
            data['hw_platform'] = uname_parts[-2]
            data['processor'] = uname_parts[-3]
            data['machine'] = uname_parts[-4]
            data['kernel_date'] = " ".join(uname_parts[-10:-4])
            data['kernel_type'] = uname_parts[-11]
        else:
            data['os'] = None
            data['hw_platform'] = None
            data['processor'] = None
            data['machine'] = None
            data['kernel_date'] = None
            data['kernel_type'] = None
        self.data = data

    @classmethod
    def from_kernel(cls, kernel):
        """
        Create a Uname object from a kernel NVR (e.g. '2.6.32-504.el6.x86_64').

        :Parameters:
            - `kernel` - the kernel version and release string.
        """
        data = cls.parse_nvr(kernel, arch=False)
        content = ["{name} {nodename} {kernel} {kernel_type} {kernel_date} {machine} {processor} {hw_platform} {os}".format(
            name="Linux",
            nodename=data['nodename'],
            kernel=kernel,
            kernel_type=data['kernel_type'],
            kernel_date=data['kernel_date'],
            machine=data['machine'],
            processor=data['processor'],
            hw_platform=data['hw_platform'],
            os=data['os'])]
        return cls(Context(content=content, path=None))

    @classmethod
    def from_uname_str(cls, uname_str):
        """
        Create a Uname object from a string containing the output of 'uname -a'.

        :Parameters:
            - `uname_str` - the string output of `uname -a`
        """
        if len(uname_str.split(' ')) == 1:
            uname_str = "Linux " + "hostname " + uname_str
        return cls(Context(content=[uname_str.strip()], path=None))

    @classmethod
    def from_release(cls, release):
        """
        Attempt to create a Uname object from a release (e.g. '7.2').

        This translates from the release to the kernel version for that
        release, and then uses that to generate a Uname object using the
        class `from_kernel` method.  If the release does not match a known
        release, it returns None.

        :Parameters:
            - `release`: RHEL release version.
        """
        if isinstance(release, tuple):
            release = '.'.join(release)
        nvr = release_to_kernel_map.get(release)
        # return cls(Context(content=[nvr], path=None))
        return cls.from_kernel(nvr)

    @classmethod
    def parse_nvr(cls, nvr, data=None, arch=True):
        """
        Called by `parse_uname_line` to separate the version, release and arch
        information.

        :Parameters:
            - `nvr`: Uname content to parse.
            - `arch`: Flag to indicate whether there is architecture
              information in the release.

        :Exceptions:
            - `UnameError`: Raised on errors in evaluating the uname content.
        """
        if len(nvr.split('-')) < 2:
            raise UnameError("Too few parts in the uname version-release", nvr)

        if data is None:
            data = dict(cls.defaults)

        data['version'], data['release_arch'] = nvr.split('-', 1)
        if arch:
            try:
                data['release'], data['arch'] = data['release_arch'].rsplit('.', 1)
            except ValueError:
                data['release'] = data['release_arch']
                data['arch'] = None
        else:
            data['release'] = data['release_arch']
            data['arch'] = None
        data['_rel_maj'] = data['release'].split(".")[0]
        rhel_key = "-".join([data['version'], data['_rel_maj']])
        rhel_release = rhel_release_map.get(rhel_key, '-1.-1')
        data['rhel_release'] = rhel_release.split('.')
        try:
            data['_sv_version'] = StrictVersion(data['version'])
        except ValueError:
            data['_sv_version'] = None
        # LooseVersion doesn't raise errors, it just goes with what it gets
        data['_lv_version'] = LooseVersion(data['version'])
        num_sections = 7 if 'rt' in data['release'] else 5
        data['_lv_release'] = LooseVersion(pad_release(data['release'], num_sections=num_sections))
        data['ver_rel'] = '%s-%s' % (data['version'], data['release'])
        return data

    def _best_version(self, other):
        """
        Use strict versions for comparisons, or loose versions if strict are
        not available.
        """
        if self._sv_version and other._sv_version:
            return self._sv_version, other._sv_version
        else:
            return self._lv_version, other._lv_version

    def __str__(self):
        return "version: %s; release: %s; rel_maj: %s; lv_release: %s" % (
            self.version, self.release, self._rel_maj, self._lv_release
        )

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, str(self))

    def __eq__(self, other):
        """
        Operator to perform equal comparison of a Uname object to another Uname
        object or a string.

        The overloaded operators ``=``,``!=``,``<``,``>``,``<=``, and ``>=``
        provide logical comparison for a Uname object.  If the `other` object
        is a Uname or a string then comparison will be performed.  If `other`
        is any other type then currently a `NotImplementedError` exception is
        raised.

        Comparison is performed on the version and release information.
        Version comparison is strict, meaning that a the Uname class will only
        accept three integers as a version number such as "3.10.0".  Release
        comparison is also strict in that Uname expect a set of three numbers
        and a RHEL product string, however less than three numbers is accepted
        as long as there is at least one number.  For example "327.10.1.el7",
        "327.10.el7", and "327.el7" are all valid releases.  Also, for
        comparison purposes all missing numbers are assumed to be "0".
        For example:
            "327.10.0.el7" == "327.10.el7" and "327.0.0.el7" == "327.el7".

        :Parameters:
            - `other`: Uname object or version-release string to compare.

        :Exceptions:
            - `UnameError`: This exception is raised when there are any errors
              evaluating the uname content.
            - `ValueError`: This exception is raised when a version-release
              string is in an unparsable format.
            - `NotImplementedError`: This exception is thrown if a type other
              than ``Uname`` or ``str`` is provided as a parameter.
        """
        if isinstance(other, Uname):
            other_uname = other
        else:
            other_uname = Uname.from_uname_str(other)

        s_version, o_version = self._best_version(other_uname)

        return s_version == o_version and self._lv_release == other_uname._lv_release

    def __ne__(self, other):
        """
        Operator to perform inequality comparison of a Uname object to another
        Uname object or a string.

        See the `__eq__` operator for a detailed description.
        """
        return not(self == other)

    def __lt__(self, other):
        """
        Operator to perform less than comparison of a Uname object to another
        Uname object or a string.

        See the `__eq__` operator for a detailed description.
        """
        if isinstance(other, Uname):
            other_uname = other
        else:
            other_uname = Uname.from_uname_str(other)

        s_version, o_version = self._best_version(other_uname)

        return s_version < o_version or \
            (s_version == o_version and self._lv_release < other_uname._lv_release)

    def __le__(self, other):
        """
        Operator to perform less than or equal comparison of a Uname object
        to another Uname object or a string.

        See the :__eq__: operator for a detailed description.
        """
        return self < other or self == other

    def __gt__(self, other):
        """
        Operator to perform greater than comparison of a Uname object to
        another Uname object or a string.

        See the :__eq__: operator for a detailed description.
        """
        if isinstance(other, Uname):
            other_uname = other
        else:
            other_uname = Uname.from_uname_str(other)

        s_version, o_version = self._best_version(other_uname)

        return s_version > o_version or \
            (s_version == o_version and self._lv_release > other_uname._lv_release)

    def __ge__(self, other):
        """
        Operator to perform greater than or equal comparison of a Uname object
        to another Uname object or a string.

        See the :__eq__: operator for a detailed description.
        """
        return self.__gt__(other) or self.__eq__(other)

    def _less_than(self, other):
        """
        Compare two ``Uname`` classes.  This function is used like one might
        use ``__lt__``. However, if an invalid ``_lv_release`` indicated by a
        value of ``None``, ``False`` is returned.

        Since this behavior is not optimal for the the '<' comparison
        operator (raising an Error would probably be better) we'll keep it
        internal to the class.
        """
        s_version, o_version = self._best_version(other)

        if s_version == o_version:
            ret = self._lv_release < other._lv_release
        else:
            ret = s_version < o_version
        return ret

    def fixed_by(self, *fixes, **kwargs):
        """
        Determine whether the Uname object is fixed by a range of releases or
        by a specific release.

        :Parameters:
            - `fixes`: List of one or more Uname objects to compare to the
              current object.  `fixes` is a list of one or more Uname objects
              and each will be compared with the current object to determine
              a match.
            - `kwargs`: List of key word argument/Uname object pairs.
              Currently only `introduced_in` is supported as a keyword.  When
              used the current Uname object is checked to see if it is prior to
              the `introduced_in` release.  It will be further checked against
              fixes only if it is the same as or newer than the
              `introduced_in` release.
        """
        introduced_in = kwargs.get("introduced_in")
        if introduced_in and self._less_than(self.from_kernel(introduced_in)):
            return []
        fix_unames = sorted((self.from_kernel(f) for f in fixes))
        fix_kernels = [f.kernel for f in fix_unames]

        # If there is a fix in your kernel release stream
        # See if you are fixed by it
        for i, fixed in enumerate(fix_unames):
            if self._rel_maj == fixed._rel_maj:
                if self._less_than(fixed):
                    return fix_kernels[i:]
                else:
                    return []

        # No fixes for your specific release so just return
        # all fixes that are greater
        return [fix.kernel for fix in fix_unames if self._less_than(fix)]

    @property
    def release_tuple(self):
        return tuple(map(int, self.data["rhel_release"]))

    @property
    def redhat_release(self):
        return RedhatRelease(major=int(self.rhel_release[0]), minor=int(self.rhel_release[1]))


def pad_release(release_to_pad, num_sections=4):
    '''
    Pad out package and kernel release versions so that
    ``LooseVersion`` comparisons will be correct.

    Release versions with less than num_sections will
    be padded in front of the last section with zeros.

    For example ::

        pad_release("390.el6", 4)

    will return ``390.0.0.el6`` and ::

        pad_release("390.11.el6", 4)

    will return ``390.11.0.el6``.

    If the number of sections of the release to be padded is
    greater than num_sections, a ``ValueError`` will be raised.
    '''
    parts = release_to_pad.split('.')

    if len(parts) > num_sections:
        raise ValueError("Too many sections encountered ({found} > {num} in release string {rel}".format(
            found=len(parts), num=num_sections, rel=release_to_pad
        ))

    pad_count = num_sections - len(parts)
    return ".".join(parts[:-1] + ['0'] * pad_count + parts[-1:])
