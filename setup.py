import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="battle-cats-save-editor",
    version="1.2.0",
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
    package_dir={"" : "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    include_package_data=True
)