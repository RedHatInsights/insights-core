import os
from setuptools import setup, find_packages

__here__ = os.path.dirname(os.path.abspath(__file__))

package_info = dict((k, None) for k in ["RELEASE", "COMMIT", "VERSION", "NAME"])

for name in package_info:
    with open(os.path.join(__here__, "insights", name)) as f:
        package_info[name] = f.read().strip()

entry_points = {
    'console_scripts': [
        'insights-run = insights.core:main',
        'gen_api = insights.tools.generate_api_config:main',
        'insights-perf = insights.tools.perf:main',
        'client = insights.client:run'
    ]
}

runtime = set([
    'argparse',
    'pyyaml>=3.10,<=3.12',
    'six',
    'requests',
    'pyOpenSSL',
    'importlib',
    'Jinja2==2.9.6',
])

develop = set([
    'flake8==3.3.0',
    'coverage==4.3.4',
    'pytest==3.0.6',
    'pytest-cov==2.4.0',
    'Sphinx',
    'sphinx_rtd_theme',
    'futures==3.0.5',
    'requests==2.13.0',
    'wheel',
    'six'
])

if __name__ == "__main__":
    # allows for runtime modification of rpm name
    name = os.environ.get("INSIGHTS_CORE_NAME", package_info["NAME"])

    setup(
        name=name,
        version=package_info["VERSION"],
        description="Insights Application Programming Interface",
        author_email="insights@redhat.com",
        license="Apache 2",
        url="https://access.redhat.com/insights",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "License :: OSI Approved :: Apache Software License",
            "Programming Language :: Python :: 2.7",
            "Topic :: System :: Monitoring",
            "Intended Audience :: Information Technology"
        ],
        packages=find_packages(),
        install_requires=list(runtime),
        extras_require={
            'develop': list(runtime | develop),
            'optional': ['python-cjson', 'python-logstash', 'python-statsd', 'watchdog'],
        },
        entry_points=entry_points,
        include_package_data=True
    )
