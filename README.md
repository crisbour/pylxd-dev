# LXD Environment

This is a python library to help automate creation of new LXC/LXD containers. Linux containers are system containers compared with application containers like Docker. That is, the container behaves like a generic host, rather than having a minimalistic container meant to run in a cluster of applications containers. This enables using them for development and testing environments of any kind of software, removing the need to worry about software versions and what paths you might break in your personal host.

Therefore, this library handles launching linux containers with enabled ssh, in order to be capable of connecting `vs code` to it (or any other text editor capable of remote editing) and develop your project like it would be on the host.

## Install library

```shell
git clone https://github.com/cristi-bourceanu/pylxd-dev
cd pylxd-dev
pip install .
```

## Usage Example

### Script to make use of the library

The following is the default script through which you can use the library. You may enable execution for this and added to the path so you have it available globally.

```python
from devlxd import ContainerFactory

if __name__=="__main__":
	devlxd_object = ContainerFactory()
	devlxd_object.start()
```



### CLI options

```shell
--- LXD/pylxd-dev ‹master› » python example.py -h
Usage: example.py [options] <container_name>

Options:
  -h, --help            show this help message and exit
  -a ALIAS, --alias=ALIAS
                        specify image alias at container creation
  -p, --priv            privileged container: security.privileged=true
  -m MOUNTS, --mount=MOUNTS
                        mount specified directory in container at
                        /home/ubuntu/<directory>
  -l SCRIPTS, --load=SCRIPTS
                        load shell script to be run in the container as root
  --arch=ARCH           specify architecture
  --sysarch             use system architecure
```

#### Create container

Let's create a new container. You will be prompted to introduce a password for ubuntu user, such that we can ssh into it.

```shell
--- LXD/pylxd-dev ‹master* ?› » python example.py -a ubuntu/20.10 lxc-test
14:32:44: Building container with config={'architecture': '', 'config': {}, 'devices': {}, 'name': 'lxc-test', 'source': {'type': 'image', 'alias': 'ubuntu/20.10', 'mode': 'pull', 'protocol': 'simplestreams', 'server': 'https://images.linuxcontainers.org'}}
14:32:46: Container started! Wait to establish connection...
14:32:47: Update, passwd and setup ssh.
Password for user ubuntu: 
...
...
...
14:34:29: Addresses = [{'family': 'inet', 'address': '10.102.37.41', 'netmask': '24', 'scope': 'global'}, {'family': 'inet6', 'address': 'fd42:e96a:3c03:c316:216:3eff:fee1:ace6', 'netmask': '64', 'scope': 'global'}, {'family': 'inet6', 'address': 'fe80::216:3eff:fee1:ace6', 'netmask': '64', 'scope': 'link'}]
```

At the end you will be given address information about the container which we can use to ssh into it.

```shell
ssh ubuntu@10.102.37.41
```

#### Share files

Unprivileged:

```shell
--- LXD/pylxd-dev ‹master* M?› » python example.py -m devlxd lxc-test
01:51:56: Container with name lxc-test already exists.                            
Accepting only configurations options.
01:51:56: Container lxc-test info: (alias, arch, privileged) = (Ubuntu/groovy,amd64,False)
01:51:56: Container unprivileged: Copy directory devlxd to /home/ubuntu
```

Privileged:

```shell
--- LXD/pylxd-dev ‹master* M?› » python example.py -m devlxd lxc-test
02:23:30: Container with name lxc-test already exists.                            
Accepting only configurations options.
02:23:30: Container lxc-test info: (alias, arch, privileged) = (Ubuntu/groovy,amd64,True)
02:23:30: Container privileged: Mounting host directory /home/cristi/Documents/Scripts/Python/LXD/pylxd-dev/devlxd at container path /home/ubuntu/devlxd
```

