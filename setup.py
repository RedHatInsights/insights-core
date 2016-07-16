from setuptools import setup, find_packages

if __name__ == "__main__":
    import falafel

    setup(
        name=falafel.NAME,
        version=falafel.VERSION,
        description="Insights Application Programming Interface",
        packages=find_packages(),
        package_data={"": ["*.json", "RELEASE", "COMMIT"]},
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
                'Jinja2'
            ],
            'optional': [
                'python-cjson'
            ],
            'test': [
                'flake8',
                'coverage',
                'pytest',
                'pytest-cov'
            ]
        },
        entry_points={
            'console_scripts': [
                'insights-run = falafel.core:main'
            ]
        }
    )
