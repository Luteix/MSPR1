import os
from setuptools import setup, find_packages

def read_requirements():
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
   name='futurekawa_api',
   version='1.0',
   description='FutureKawa API',
   author='Man Foo',
   author_email='foomail@foo.example',
   packages=find_packages(), # Trouve automatiquement services, controllers, repositories
   py_modules=['models', 'app', 'database', 'config'], # Fichiers à la racine
   install_requires=read_requirements(),
)
