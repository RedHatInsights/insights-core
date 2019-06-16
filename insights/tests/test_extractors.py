#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import shlex
import subprocess
import tempfile
import zipfile
from contextlib import closing

from insights.core import archives
from insights.core.archives import extract


def test_with_zip():
    tmp_dir = tempfile.mkdtemp()

    d = os.path.join(tmp_dir, 'sys', 'kernel')
    os.makedirs(d)
    with open(os.path.join(d, 'kexec_crash_size'), "w") as f:
        f.write("ohyeahbaby")

    try:
        os.unlink("/tmp/test.zip")
    except:
        pass

    # stolen from zipfile.py:main
    def _add_to_zip(zf, path, zippath):
        if os.path.isfile(path):
            zf.write(path, zippath, zipfile.ZIP_DEFLATED)
        elif os.path.isdir(path):
            if zippath:
                zf.write(path, zippath)
            for nm in os.listdir(path):
                _add_to_zip(zf, os.path.join(path, nm), os.path.join(zippath, nm))
        # else: ignore

    with closing(zipfile.ZipFile("/tmp/test.zip", "w")) as zf:
        _add_to_zip(zf, tmp_dir, os.path.basename(tmp_dir))

    try:
        with extract("/tmp/test.zip") as ex:
            assert any(f.endswith("/sys/kernel/kexec_crash_size") for f in archives.get_all_files(ex.tmp_dir))

    finally:
        os.unlink("/tmp/test.zip")

    subprocess.call(shlex.split("rm -rf %s" % tmp_dir))
