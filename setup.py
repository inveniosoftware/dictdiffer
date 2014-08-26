from setuptools import setup

setup(
    name='dictdiffer',
    version='0.0.5.dev0',
    description='Dictdiffer is a helper module that helps you '
                'to diff and patch dictionaries',
    author='Fatih Erikli',
    author_email='info@invenio-software.org',
    url='https://github.com/inveniosoftware/dictdiffer',
    py_modules=['dictdiffer'],
    extras_require={
        "docs": ["sphinx_rtd_theme"],
    },
)
