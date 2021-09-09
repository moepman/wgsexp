from setuptools import setup, find_packages

setup(
    name="wgsexp",
    version="0.1.0",
    author="Markus Hauschild",
    author_email="markus@moepman.eu",
    description="WireGuard Simple Exporter",
    license="ISC",
    url="https://github.com/ffrgb/wgsexp",
    packages=find_packages(exclude="tests"),
    install_requires=["prometheus-client", "pyroute2"],
    setup_requires=["wheel"],
    entry_points={
        "console_scripts": [
        ],
    },
)
