"""Setup for installing the package."""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("src/BCSFE_Python/files/version.txt", "r", encoding="utf-8") as fh:
    version = fh.read()

setuptools.setup(
    name="battle-cats-save-editor",
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
    python_requires=">=3.8",
    install_requires=["colored", "tk", "python-dateutil", "requests"],
    include_package_data=True,
)
