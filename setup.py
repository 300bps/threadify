from setuptools import setup

# Build process summary:
# To build source and wheel distribution, execute:
# python setup.py sdist bdist_wheel
#
# To upload to test.pypi.org (requires an API key):
# twine upload --repository testpypi dist/*

# To upload to pypi.org (requires an API key):
# twine upload dist/*


setup(
    name='threadify',
    version='1.0.0',
    author='David Smith',
    author_email='x300bps@icloud.com',
    description='An enhancement to Python threads that adds cooperative pause, unpause, and kill capabilities.',
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    packages=['threadify'],
    url='https://github.com/300bps/threadify',
    license='MIT',
    keywords='thread threading concurrent cooperative multitasking multithreading pause kill',
    classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ]
)
