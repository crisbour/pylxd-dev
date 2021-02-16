from setuptools import setup, find_namespace_packages, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name = 'devlxd',
	version = '0.1',
    description = "Testing/Development Environment in LXC/LXD containers",
    url = "https://github.com/cristi-bourceanu/devlxd",
	packages = find_packages(),
	install_requires = ['pylxd'],
	python_requires = '>=3.5',
	classifiers = [
		"Programming Language :: Python :: 3",
		"Operating System :: Linux"])