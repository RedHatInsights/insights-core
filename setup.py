import os
from pkg_resources import parse_version
from setuptools import setup, find_packages
from sys import version_info

__here__ = os.path.dirname(os.path.abspath(__file__))

package_info = dict.fromkeys(["RELEASE", "COMMIT", "VERSION", "NAME"])

for name in package_info:
    with open(os.path.join(__here__, "insights", name)) as f:
        package_info[name] = f.read().strip()

entry_points = {
    'console_scripts': [
        'insights-run = insights:main',
        'insights-info = insights.tools.query:main',
        'gen_api = insights.tools.generate_api_config:main',
        'insights-perf = insights.tools.perf:main',
        'client = insights.client:run',
        'mangle = insights.util.mangle:main'
    ]
}

runtime = set([
    'pyyaml>=3.10,<=3.13',
    'six',
])


def maybe_require(pkg):
    try:
        __import__(pkg)
    except ImportError:
        runtime.add(pkg)


maybe_require("importlib")
maybe_require("argparse")


client = set([
    'requests',
    'pyOpenSSL',
])


python_version = "%d.%d.%d" % version_info[:3]
if parse_version(python_version) < parse_version("2.7"):
    flake8_version = "2.6.2"  # Python 2.6 support was dropped with Flake8 version 3.0.0.
else:
    flake8_version = "3.3.0"

develop = set([
    'flake8==%s' % flake8_version,
    'coverage==4.3.4',
    'pytest==3.0.6',
    'pytest-cov==2.4.0',
    'mock==2.0.0',
    'Sphinx',
    'nbsphinx==0.3.1',
    'sphinx_rtd_theme',
    'futures==3.0.5',
    'requests==2.13.0',
    'wheel',
    'ipython<6',
    'colorama',
])

optional = set([
    'jinja2',
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
            'develop': list(runtime | develop | client),
            'client': list(runtime | client),
            'optional': list(optional),
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
