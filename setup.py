from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = "sdcapi.py",
    version = "1.0.dev0",
    author = "Torbjorn Tyridal",
    author_email = "sdcapi@tyridal.no",
    description = ("SDC Banking api"),
    requires = [
        "pycrypto",
        "certifi",
        "requests",
        "requests_toolbelt",
        ],
    license = "GPLv3",
    keywords = "internet-banking, sdc",
    url = "https://github.com/ttyridal/sdcapi.py",
    download_url = "",
    packages = ['sdcapi'],
    package_dir = {'sdcapi': 'sdcapi'},
    package_data = {'sdcapi': ['sdc.pem']},
    include_package_data=True,
    long_description=read('README.md'),
    classifiers=[
        "Environment :: Console",
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Topic :: Communications",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],

    zip_safe=True
)
