import os
import sys
from setuptools import setup, find_packages

__here__ = os.path.dirname(os.path.abspath(__file__))

package_info = dict.fromkeys(["RELEASE", "COMMIT", "VERSION", "NAME"])

for name in package_info:
    with open(os.path.join(__here__, "insights", name)) as f:
        package_info[name] = f.read().strip()

entry_points = {
    'console_scripts': [
        'insights-collect = insights.collect:main',
        'insights-run = insights:main',
        'insights = insights.command_parser:main',
        'insights-cat = insights.tools.cat:main',
        'insights-dupkeycheck = insights.tools.dupkeycheck:main',
        'insights-inspect = insights.tools.insights_inspect:main',
        'insights-info = insights.tools.query:main',
        'insights-ocpshell= insights.ocpshell:main',
        'client = insights.client:run',
        'mangle = insights.util.mangle:main'
    ]
}

runtime = set([
    'six',
    'requests',
    'redis',
    'cachecontrol',
    'cachecontrol[redis]',
    'cachecontrol[filecache]',
    'defusedxml',
    'lockfile',
    'jinja2',
])

if (sys.version_info < (2, 7)):
    runtime.add('pyyaml>=3.10,<=3.13')
else:
    runtime.add('pyyaml')


def maybe_require(pkg):
    try:
        __import__(pkg)
    except ImportError:
        runtime.add(pkg)


maybe_require("importlib")
maybe_require("argparse")


client = set([
    'requests',
    'python-gnupg==0.4.6',
    'oyaml'
])

develop = set([
    'futures==3.0.5',
    'wheel',
])

docs = set([
    'docutils==0.16',
    'Sphinx<=3.0.2',
    'nbsphinx',
    'sphinx_rtd_theme',
    'ipython',
    'colorama',
    'jinja2',
    'Pygments',
    'jedi<0.18.0'    # Open issue with jedi 0.18.0 and iPython <= 7.19
                     # https://github.com/davidhalter/jedi/issues/1714
])

testing = set([
    'coverage==4.3.4',
    'pytest==3.0.6',
    'pytest-cov==2.4.0',
    'mock==2.0.0',
])

cluster = set([
    'ansible',
    'pandas',
    'colorama',
])

openshift = set([
    'openshift'
])

linting = set([
    'flake8==2.6.2',
])

optional = set([
    'python-cjson',
    'python-logstash',
    'python-statsd',
    'watchdog',
])

if __name__ == "__main__":
    # allows for runtime modification of rpm name
    name = os.environ.get("INSIGHTS_CORE_NAME", package_info["NAME"])

    setup(
        name=name,
        version=package_info["VERSION"],
        description="Insights Core is a data collection and analysis framework",
        long_description=open("README.rst").read(),
        url="https://github.com/redhatinsights/insights-core",
        author="Red Hat, Inc.",
        author_email="insights@redhat.com",
        packages=find_packages(),
        install_requires=list(runtime),
        package_data={'': ['LICENSE']},
        license='Apache 2.0',
        extras_require={
            'develop': list(runtime | develop | client | docs | linting | testing | cluster),
            'develop26': list(runtime | develop | client | linting | testing | cluster),
            'client': list(runtime | client),
            'client-develop': list(runtime | develop | client | linting | testing),
            'cluster': list(runtime | cluster),
            'openshift': list(runtime | openshift),
            'optional': list(optional),
            'docs': list(docs),
            'linting': list(linting | client),
            'testing': list(testing | client)
        },
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6'
        ],
        entry_points=entry_points,
        include_package_data=True
    )
