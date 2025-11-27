from setuptools import setup, find_packages

setup(
    name="primerlab",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "primer3-py>=2.0.0",
        "PyYAML>=6.0",
        "biopython>=1.80",
    ],
    entry_points={
        "console_scripts": [
            "primerlab=primerlab.cli.main:main",
        ],
    },
    author="Engki Nandatama",
    description="A modular, AI-friendly bioinformatics framework for automated primer and probe design.",
    python_requires=">=3.10",
)
