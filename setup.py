import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sonarq-runner",
    version="0.0.1",
    author="dnx",
    author_email="auraltension@riseup.net",
    description="A runner for local SonarQube scans",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/0x646e78/sonarq",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
