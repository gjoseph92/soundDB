from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding= "utf-8") as f:
    long_description = f.read()

setup(
    name= "soundDB",
    version= "0.1.0",
    description= "Query and load NSNSD acoustic data into Python, minimize pain",
    long_description= long_description,
    url= "https://github.com/gjoseph92/soundDB",
    author= "Gabe Joseph",
    author_email= "gabriel_joseph@partner.nps.gov",
    license= "CC0 1.0",

    packages= find_packages(exclude= ["doc"]),
    install_requires= ['iyore', 'future', 'numpy', 'pandas == 0.18.1', 'tqdm']
    )
