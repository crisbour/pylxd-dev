#!/usr/bin/python
from pylxd import Client
import platform
from optparse import OptionParser
import time
import logging
import crypt
import getpass
import os

class ContainerFactory(object):
    arch = ''
    alias = ''
    privileged = False
    scripts = []
    mounts = []
    _available_arch = ['amd64', 'x86_64', 'aarch64', 'i686', 'ppc64le', 's390x']
    def __init__(self):
        logging.basicConfig(format="%(asctime)s: %(message)s", 
                            level=logging.INFO, datefmt="%H:%M:%S")
        self.client = Client()
    
    def start(self):
        # Get existing containters
        containers = self.client.containers.all()

        # Options parser
        self.option_parser()

        # Verify if the container exists
        launch = True
        for container in containers:
            if(container.name == self.name):
                launch = False
                self.container = container
                logging.info(f'Container with name {container.name} already exists.\
                            \nAccepting only configurations options.')

        # Check that options have been specified correctly
        if(not launch):
            assert self.alias == '', f'Alias {self.alias} specified, but container already exists.'
            assert self.arch == '', f'Arch {self.arch} specified, but container already exists.'
        else:
            assert self.alias, f'Alias must be specified for launching a new container.'

        if(launch):
            self.launch_container()
            self.setup_container()
        else:
            self.fill_object()
        
        for script in self.scripts:
            self.run_script(script)

        for dir_path in self.mounts:
            self.share_directory(dir_path)
        

    # Add Option parser to configure container creation
    def option_parser(self):
        usage = "usage: %prog [options] <container_name>"
        parser = OptionParser(usage)
        parser.add_option('-a','--alias', dest="alias",
                        help="specify image alias at container creation")
        parser.add_option('-p','--priv', dest="privileged", action="store_true",
                        help="privileged container: security.privileged=true")
        parser.add_option('-m','--mount', dest='mounts', action='append',
                        help="mount specified directory in container at /home/ubuntu/<directory>")
        parser.add_option('-l','--load', dest='scripts', action='append',
                        help="load shell script to be run in the container as root")
        parser.add_option('--arch', dest="arch",
                        help="specify architecture")
        parser.add_option('--sysarch', dest="sysarch", action="store_true",
                        help="use system architecure")
        
        (options, args) = parser.parse_args()

        assert len(args) == 1, f"Expected one argument, but received {args}"
        self.name = args[0]

        # Parse options
        assert not(options.arch and options.sysarch), f'Both --arch and --sysarch options have been used.'
        if(options.arch):
            assert options.arch in self._available_arch, f'{options.arch} is not a valid architecture.'
            self.arch = options.arch
        if(options.sysarch):
            self.arch = platform.machine()
        
        if(options.alias):
            self.alias = options.alias

        if(options.scripts):
            self.scripts = options.scripts

        if(options.privileged):
            self.privileged = options.privileged

        if(options.mounts):
            self.mounts = options.mounts


    def fill_object(self):
        def resolve_bool(bool_str):
            return True if bool_str=='true' else False
        self.alias = self.container.config['image.os'] + '/' + self.container.config['image.release']
        self.arch = self.container.config['image.architecture']
        try:
            self.privileged = resolve_bool(self.container.config['security.privileged'])
        except:
            self.privileged = False
        logging.info(f'Container {self.container.name} info: (alias, arch, privileged) = ({self.alias},{self.arch},{self.privileged})')

    def launch_container(self):
        # Default config for our container
        def resolve_bool(bool_val):
            return 'true' if bool_val else 'false'

        config = {
            'architecture': self.arch,
            'config': {
                'security.privileged': resolve_bool(self.privileged)
            },
            'devices': {},
            'name': self.name,
            'source': {
                'type': 'image',
                'alias': self.alias,
                'mode': 'pull',
                'protocol': 'simplestreams',
                'server': 'https://images.linuxcontainers.org'
                }
            }

        # Create and start te container
        logging.info(f"Building container with config={config}")
        self.container = self.client.containers.create(config,wait=True)
        self.container.start(wait=True)

        logging.info("Container started! Wait to establish connection...")
        while len(self.container.state().network["eth0"]["addresses"]) < 2:
            time.sleep(1)


    def setup_container(self):

        # Update and setup ssh
        logging.info('Update, passwd and setup ssh.')

        password = getpass.getpass('Password for user ubuntu: ')
        crypted_passwd = crypt.crypt(password, crypt.mksalt(crypt.METHOD_SHA512))  #crypt.mksalt(crypt.METHOD_SHA512)

        commands = [
            ['apt', 'update'],
            ['apt', 'install', '-y', 'openssh-server'],
            ['usermod', '--password', crypted_passwd, 'ubuntu']
        ]
        for command in commands:
            logging.info(f"command: {command}")
            result = self.container.execute(command)
            logging.info(f"result: {result.exit_code}")
            logging.info(f"stdout: {result.stdout}")
            logging.info(f"stderr: {result.stderr}")

        # Eth info about the container
        addresses = self.container.state().network['eth0']['addresses']
        logging.info(f"Addresses = {addresses}")

    def run_script(self, file):
        # Read the script and copy it into the container in /tmp
        filedata = open(file).read()
        filename = file.split('/')[-1]
        filelocation = '/tmp/'+filename
        logging.info(f'Copy and execute script {filename} in container {self.name}')
        self.container.files.put(filelocation, filedata)

        # Execute the script just copied
        result = self.container.execute(['sh', filelocation])
        logging.info(f"result: {result.exit_code}")
        logging.info(f"stdout: {result.stdout}")
        logging.info(f"stderr: {result.stderr}")

    def share_directory(self, dirsource):
        # If the container is privileged then we can mount the directory
        dirsplit = dirsource.split('/')
        dirname = dirsplit[-1]
        dirdest = '/home/ubuntu/' + dirname
        if(self.privileged):
            if(dirsplit[0]=='.' or len(dirsplit)==1):
                dirsource = os.getcwd() + '/' + dirname
            dirdevice = dirname+'-dev'
            logging.info(f'Container privileged: Mounting host directory {dirsource} at container path {dirdest}')
            self.container.devices.update({dirdevice:{'path':dirdest, 'source': dirsource, 'type': 'disk'}})
            self.container.save(wait=True)
        else:
            logging.info(f'Container unprivileged: Copy directory {dirsource} to {dirdest}')
            self.container.files.recursive_put(dirsource, dirdest, mode='0764', uid=1000, gid=1000)