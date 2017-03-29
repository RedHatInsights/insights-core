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
        'compare_api = falafel.tools.compare_uploader_configs:main',
        'falafel-scaffold = falafel.scaffold:main',
        'falafel-perf = falafel.tools.perf:main'
    ]
}
data_files = []

runtime = {
    'pyyaml',
    'tornado',
    'futures',
    'requests',
}

develop = {
    'flake8',
    'coverage',
    'pytest==3.0.6',
    'pytest-cov',
    'Sphinx',
    'sphinx_rtd_theme',
    'Jinja2',
}

if __name__ == "__main__":
    # allows for runtime modification of rpm name
    name = os.environ.get("FALAFEL_NAME", package_info["NAME"])

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
