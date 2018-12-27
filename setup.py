from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="graph-state",
    version="0.0.1",
    author="Adam Kelly",
    author_email="adamkelly2201@gmail.com",
    description="An implementation of a stabilizer circuit simulator based on the graph state formalism.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qcgpu/stabilizer-simulator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['networkx', 'numpy', 'matplotlib']
)