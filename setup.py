from setuptools import setup, find_packages

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name="debugprint",
    version="0.1.8",
    license="Apache 2.0",
    packages=find_packages(),
    author="Phil Howe",
    author_email="philhbusiness@gmail.com",
    description="A clone of the npm debug module with ability to implement custom formatting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="debug print",
    url="https://github.com/phil-arh/debugprint",
)
