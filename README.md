# LXD Environment

This is a python library to help automate creation of new LXC/LXD containers. Linux containers are more like a lightweight OS VM rather than meant for applications like Docker. While Docker has  a large variety of examples and huge community, its strongest point, minimal containers, could also be its defects when it comes to development and testing environments.

Therefore, this library handles launching linux containers with enabled ssh, in order to be capable of connecting `vs code` to it and develop your project like it would be on the host.

## Install library

```shell
pip install devlxd
```

## Usage Example

```python
from devlxd import ContainerFactory

if __name__=="__main__":
	devlxd_object = ContainerFactory()
	devlxd_object.start()
```

