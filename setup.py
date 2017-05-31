import os
from setuptools import setup, find_packages

__here__ = os.path.dirname(os.path.abspath(__file__))

package_info = {k: None for k in ["RELEASE", "COMMIT", "VERSION", "NAME"]}

for name in package_info:
    with open(os.path.join(__here__, "falafel", name)) as f:
        package_info[name] = f.read().strip()

entry_points = {
    'console_scripts': [
        'insights-run = falafel.core:main',
        'gen_api = falafel.tools.generate_api_config:main',
        'falafel-scaffold = falafel.scaffold:main',
        'falafel-perf = falafel.tools.perf:main'
    ]
}
data_files = []

runtime = {
    'pyyaml>=3.10,<=3.12',
    'tornado>=4.2.1',
    'futures==3.0.5',
    'requests==2.13.0',
}

develop = {
    'flake8==3.3.0',
    'coverage==4.3.4',
    'pytest==3.0.6',
    'pytest-cov==2.4.0',
    'Sphinx',
    'sphinx_rtd_theme',
    'Jinja2==2.9.6',
    'wheel'
}

if __name__ == "__main__":
    # allows for runtime modification of rpm name
    name = os.environ.get("FALAFEL_NAME", package_info["NAME"])

    setup(
        name=name,
        version=package_info["VERSION"],
        description="Insights Application Programming Interface",
        packages=find_packages(),
        package_data={"": list(package_info) + ["*.json", "*.md", "*.html", "*.js", "*.yaml"]},
        install_requires=list(runtime),
        extras_require={
            'develop': list(runtime | develop),
            'optional': ['python-cjson', 'python-logstash', 'python-statsd', 'watchdog'],
        },
        entry_points=entry_points,
        data_files=data_files
    )
