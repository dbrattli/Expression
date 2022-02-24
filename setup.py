# coding=utf-8
# read the contents of your README file
from os import path

import setuptools

import versioneer

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="Expression",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Practical functional programming for Python 3.8+",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dag Brattli",
    author_email="dag.brattli@cognite.com",
    license="MIT License",
    url="https://github.com/cognitedata/expression",
    download_url="https://github.com/cognitedata/expression",
    zip_safe=True,
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # "Development Status :: 3 - Alpha",
        # 'Development Status :: 4 - Beta',
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=["typing_extensions"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-cov", "pytest-asyncio", "hypothesis"],
    package_data={"expression": ["py.typed"]},
    packages=setuptools.find_packages(),
    package_dir={"expression": "expression"},
    include_package_data=True,
)
