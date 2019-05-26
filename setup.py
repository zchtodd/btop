import os
from setuptools import setup, find_packages

static = []
for (dirpath, dirnames, filenames) in os.walk(os.path.join("btop", "data")):
    dirpath = os.path.sep.join(dirpath.split(os.path.sep)[1:])
    static += [os.path.join(dirpath, filename) for filename in filenames]

setup(
   name="btop",
   version="1.0",
   packages=find_packages(),
   package_data={"btop": static},
   scripts=["btop/bin/btop-run.py"],
   install_requires=["websockets>=7.0.0", "psutil>=5.6.2"],
   author="Zach Todd",
   author_email="zchtodd@gmail.com",
   description="Server process monitoring viewable within a web browser.",
)
