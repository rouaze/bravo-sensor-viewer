import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyhidpp", # Replace with your own username
    version="1.0.7",
    author="vhernicot",
    author_email="vhernicot@logitech.com",
    description="A python hidpp communication module",
    install_requires = [
        'hidapi',
        'pycryptodome'
    ], 
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.logitech.com/mtx/librairies/pyhidpp",
    packages=setuptools.find_packages(),
    package_data={'pyhidpp.security': ['x1602.ini']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
