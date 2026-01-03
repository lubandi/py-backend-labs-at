from setuptools import find_packages, setup

setup(
    name="resilient_importer",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "importer=main:main",
        ],
    },
    install_requires=[],
    python_requires=">=3.10",
)
