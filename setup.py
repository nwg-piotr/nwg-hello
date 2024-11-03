import os

from setuptools import setup, find_packages


def read(f_name):
    return open(os.path.join(os.path.dirname(__file__), f_name)).read()


setup(
    name='nwg-hello',
    version='0.2.5',
    description='GTK3-based greeter for greetd',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["img/*", "langs/*", "template.glade"]
    },
    url='https://github.com/nwg-piotr/nwg-greeter',
    license='MIT',
    author='Piotr Miller',
    author_email='nwg.piotr@gmail.com',
    python_requires='>=3.6.0',
    install_requires=[],
    entry_points={
        'gui_scripts': [
            'nwg-hello = nwg_hello.main:main',
        ]
    }
)
