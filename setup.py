import os
import sys
from setuptools import setup, find_packages

__here__ = os.path.dirname(os.path.abspath(__file__))

package_info = {k: None for k in ["RELEASE", "COMMIT", "VERSION", "NAME"]}

for name in package_info:
    with open(os.path.join(__here__, "falafel", name)) as f:
        package_info[name] = f.read().strip()

BDIST_RPM_RUNNING = "bdist_rpm_running"

entry_points = {
    'console_scripts': [
        'insights-run = falafel.core:main',
        'insights-cli = falafel.console:main',
        'gen_api = falafel.tools.generate_api_config:main',
        'compare_api = falafel.tools.compare_uploader_configs:main',
        'falafel-web = falafel.web.daemon:main',
        'falafel-serve = falafel.web.server:main',
        'falafel-scaffold = falafel.scaffold:main',
        'falafel-content = falafel.content.server:main',
        'falafel-perf = falafel.tools.perf:main'
    ]
}
data_files = []

# If the install task is run, setuptools blindly tries to copy the service file
# under the /usr dir, causing a permissions error.  So we only want to include
# that file in the installation if we're building an RPM.
#
# When setuptools does a bdist_rpm, it creates a child task that runs `python
# setup.py install`.  It's this child process that really builds the data_files
# list; unfortunately there's no simple way for that process to know if it's
# running for an RPM build or not.
#
# To solve that, we are dropping a file from the parent process and checking
# for its existence in the child process.

if os.path.exists(os.path.join("../../../../..", BDIST_RPM_RUNNING)):
    data_files.append(('/usr/lib/systemd/system', ['falafel/web/falafel-web.service']))

if "bdist_rpm" in sys.argv:
    with open(BDIST_RPM_RUNNING, "w") as fp:
        fp.write("yes\n")

runtime = {
    'pyyaml',
    'tornado',
    'futures',
    'requests',
}

develop = {
    'flake8',
    'coverage',
    'pytest',
    'pytest-cov',
    'Sphinx',
    'sphinx_rtd_theme',
    'Jinja2',
}

if __name__ == "__main__":
    # allows for runtime modification of rpm name
    name = os.environ.get("FALAFEL_NAME", package_info["NAME"])

    try:
        setup(
            name=name,
            version=package_info["VERSION"],
            description="Insights Application Programming Interface",
            packages=find_packages(),
            package_data={"": package_info.keys() + ["*.json", "*.md", "*.html", "*.js", "*.yaml"]},
            install_requires=list(runtime),
            extras_require={
                'develop': list(runtime | develop),
                'optional': ['python-cjson', 'python-logstash', 'python-statsd', 'watchdog'],
            },
            entry_points=entry_points,
            data_files=data_files
        )
    finally:
        if os.path.exists(BDIST_RPM_RUNNING):
            os.unlink(BDIST_RPM_RUNNING)
