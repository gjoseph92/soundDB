from setuptools import setup, find_packages

setup(
    name= "soundDB",
    version= "0.0.1",
    description= "A library for the NPS Natural Sounds & Night Skies Division to make going from data-somewhere-on-disk to data-ready-for-processing as painless as possible",
    url= "https://github.com/nationalparkservice/soundDB",
    author= "Gabe Joseph",
    author_email= "gabriel_joseph@partner.nps.gov",
    license= "CC0 1.0",

    packages= find_packages(exclude= ["doc"]),
    install_requires= ['iyore', 'future', 'numpy', 'pandas']
    )
