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
        "colored",
        "tk",
        "python-dateutil",
        "requests",
        "pyyaml",
    ],
    include_package_data=True,
    extras_require={
        "testing": [
            "pytest",
            "pytest-cov",
        ],
    },
    package_data={"bcsfe": ["py.typed"]},
    flake8={"max-line-length": 160},
)
