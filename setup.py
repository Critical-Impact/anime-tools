
from setuptools import setup, find_packages
from anime_tools.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='anime_tools',
    version=VERSION,
    description='Provides various tools surrounding plex and anime',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Critical_Impact',
    author_email='criticalimpact@gmail.com',
    url='https://github.com/johndoe/myapp/',
    license='unlicensed',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'anime_tools': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        anime_tools = anime_tools.main:main
    """,
)
