#!/usr/bin/python
from devlxd import ContainerFactory

if __name__ == "__main__":
    lxd_creation = ContainerFactory()
    lxd_creation.start()