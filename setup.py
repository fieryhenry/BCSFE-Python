"""Setup for installing the package."""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("src/bcsfe/files/version.txt", "r", encoding="utf-8") as fh:
    version = fh.read()

setuptools.setup(
    name="bcsfe",
    version=version,
    author="fieryhenry",
    description="A battle cats save file editor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fieryhenry/BCSFE-Python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=[
        "aenum",
        "colored==1.4.4",
        "pyjwt",
        "requests",
        "pyyaml",
        "beautifulsoup4",
    ],
    include_package_data=True,
    package_data={"bcsfe": ["py.typed"]},
)
