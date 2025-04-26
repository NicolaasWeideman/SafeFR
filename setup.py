from setuptools import setup, find_packages

setup(
    name="safefr",
    version="0.1",
    url="https://github.com/NicolaasWeideman/SafeFR",
    author="Nicolaas Weideman",
    description="Safe Find & Replace: Find and replace a unique hexadecimal sequence in a file.",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["safefr=safefr.safefr:main"],
    },
)
