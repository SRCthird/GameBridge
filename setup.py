from setuptools import setup, find_packages

setup(
    name="GameBridge",
    version="0.1.0",
    author="Stephen Chryn",
    author_email="SRCthird@gmail.com",
    description="GameBridge is a flexible and easy to use application designed to manage game servers, like Minecraft, Project Zomboid or Valheim remotely. It provides a seamless interface to interact with game server executables from a socket connection, featuring basic authentication, real-time input/output management, and multi-executable support.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SRCthird/GameBridge",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
