import setuptools  # type: ignore

MAJOR, MINOR, PATCH = 0, 1, 0
VERSION = f"{MAJOR}.{MINOR}.{PATCH}"
"""This project uses semantic versioning.
See https://semver.org/
Before MAJOR = 1, there is no promise for
backwards compatibility between minor versions.
"""

setuptools.setup(
    name="walkman_modules.aeolian",
    version=VERSION,
    license="GPL",
    author="Levin Eric Zimmermann",
    author_email="levin.eric.zimmermann@posteo.eu",
    packages=[
        package
        for package in setuptools.find_namespace_packages(include=["walkman_modules.*"])
        if package[:5] != "tests"
    ],
    setup_requires=[],
    install_requires=[
        # core package
        "audiowalkman>=0.20.2, <1.0.0",
        # for audio
        "pyo==1.0.4",
        # for linear interpolation of decibel values
        "numpy>=1.18, <2.00",
    ],
    python_requires=">=3.10",
)
