import os
from setuptools import setup, find_packages

entry_points = {
    'console_scripts': [
        'insights-run = falafel.core:main',
        'insights-cli = falafel.console:main',
        'gen_api = falafel.tools.generate_api_config:main',
        'compare_api = falafel.tools.compare_uploader_configs:main'
    ]
}
data_files = []

if "OPENSHIFT_PYTHON_DIR" not in os.environ:
    data_files.append(('/usr/lib/systemd/system', ['falafel/web/falafel-web.service']))
    entry_points['console_scripts'].append('falafel-web = falafel.web.daemon:main')

if __name__ == "__main__":
    import falafel

    setup(
        name=falafel.NAME,
        version=falafel.VERSION,
        description="Insights Application Programming Interface",
        packages=find_packages(),
        package_data={"": ["*.json", "RELEASE", "COMMIT", "*.md"]},
        install_requires=[
            'pyyaml',
        ],
        extras_require={
            'develop': [
                'flake8',
                'coverage',
                'numpydoc',
                'pytest',
                'pytest-cov',
                'Sphinx',
                'sphinx_rtd_theme',
                'Jinja2',
                'tornado',
                'futures',
                'requests'
            ],
            'optional': [
                'python-cjson'
                'python-logstash',
                'python-statsd',
                'tornado',
                'futures',
            ],
            'test': [
                'flake8',
                'coverage',
                'pytest',
                'pytest-cov',
                'Jinja2'
            ]
        },
        entry_points=entry_points,
        data_files=data_files
    )
