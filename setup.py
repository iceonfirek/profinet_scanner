from setuptools import setup, find_packages

setup(
    name="profinet_scanner",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'asyncio>=3.4.3',
        'pysnmp>=4.4.12',
    ],
)
