from setuptools import setup

setup(
        name="whackastreamdeck",
        version="0.0.1",
        author="Jack Mudge",
        author_email="jack@mudge.dev",
        packages=["whackastreamdeck"],
        scripts=[],
        url="https://github.com/jmudge14/whackastreamdeck",
        license="LICENSE",
        description="A Whack-A-Mole game for the Elgato Stream Deck",
        long_description=open("README.md","r").read(),
        install_requires=[ 
            "streamdeck",
            "pillow"
        ],
        package_data={'whackastreamdeck': ['Assets/*']},
)
        

