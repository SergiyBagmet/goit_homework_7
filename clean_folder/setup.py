from setuptools import setup, find_namespace_packages

setup(
    name='clean_folder',
    version='1',
    description='sorted your folder',
    url='https://github.com/SergiyBagmet/goit_homework_7',
    author='Sergiy Bagmet',
    author_email='sergey94bagmet@gmail.com',
    license='MIT',
    packages=find_namespace_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'cleaner = clean_folder.clean:main',
        ],
    },
)