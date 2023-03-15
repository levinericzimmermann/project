import setuptools  # type: ignore

MAJOR, MINOR, PATCH = 0, 1, 0
VERSION = f"{MAJOR}.{MINOR}.{PATCH}"
"""This project uses semantic versioning.
See https://semver.org/
Before MAJOR = 1, there is no promise for
backwards compatibility between minor versions.
"""

setuptools.setup(
    name="walkmanio",
    version=VERSION,
    license="GPL",
    author="Levin Eric Zimmermann",
    author_email="levin.eric.zimmermann@posteo.eu",
    packages=["walkmanio"],
    setup_requires=[],
    install_requires=[],
    python_requires=">=3.10",
)
