from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding= "utf-8") as f:
    long_description = f.read()

setup(
    name= "soundDB",
    version= "0.0.1",
    description= "A library for the NPS Natural Sounds & Night Skies Division to make going from data-somewhere-on-disk to data-ready-for-processing as painless as possible",
    # long_description= long_description,
    url= "https://github.com/nationalparkservice/soundDB",
    author= "Gabe Joseph",
    author_email= "gabriel_joseph@partner.nps.gov",
    license= "CC0 1.0",

    packages= find_packages(exclude= ["doc"]),
    install_requires= ['iyore', 'future', 'numpy', 'pandas']
    )
