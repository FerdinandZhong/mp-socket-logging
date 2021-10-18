from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="mp-socket-logging",
    version="0.1.0",
    description="A small toolkit for python multiprocessing file logging",
    long_description=readme,
    author="Zhong Qishuai",
    author_email="ferdinandzhong@gmail.com",
    url="https://git.garena.com/shopee-ds/ml-platform/sre-utils",
    packages=find_packages(exclude=["tests*", "example*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires=">3",
    extras_require={
        "dev": [
            "pytest>=6",
            "flake8>=3.8",
            "black>=20.8b1",
            "isort>=5.6",
            "autoflake>=1.4",
        ],
    },
)
