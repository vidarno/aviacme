from setuptools import setup, find_packages

exec(open("./aviacme/version.py").read())

setup(
    name="aviacme",
    author="Vidar Normann",
    description="An ACME client for AVI",
    long_description="Command-line program for installing and renewing certificates from an ACME CA on AVI",
    version=__version__,
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "attrs",
        "click>=7.0",
        "avisdk",
        "josepy",
        "acme>=0.22.0",
        "cryptography",
        "PyOpenSSL",
    ],
    entry_points={"console_scripts": ["aviacme = aviacme.main:cli"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
    ],
)
