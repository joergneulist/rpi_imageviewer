from setuptools import setup, find_packages

setup(
    name="rpi_imageviewer",
    version="0.1.0",
    description="Image viewer for Raspberry Pi",
    author="Jörg Neulist",
    author_email="21063011+joergneulist@users.noreply.github.com",
    url="https://github.com/yourusername/rpi_imageviewer",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)