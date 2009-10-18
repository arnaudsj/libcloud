#!/usr/bin/env python
"This is simple demo of libcloud use to create a node, monitor its progress, then execute a command remotely on the node created, and then finally destroy it"

# Uncomment 2 lines below if libcloud is installed already 
import sys, time
sys.path.append('libcloud')

from libcloud.drivers.rackspace import RackspaceNodeDriver as Rackspace
from libcloud.drivers.rackspace import RackspaceSize, RackspaceImage

import paramiko # necessary for automation via SSH

def create_and_build(node_name, node_image, node_size):
    RackSpaceNode =  rackspace.create_node(node_name, rackspace.get_image(node_image), rackspace.get_size(node_size))

    # Monitor node building
    state, progress = None, None
    while (progress!=100 or state!='ACTIVE'):
    	mynode = rackspace.get_node_details(RackSpaceNode)
    	progress = int(mynode.progress)
    	state = mynode.state
    	print "Node State/Progress: %s/%s %%" % (state, progress)
    	time.sleep(5)

    return RackSpaceNode

def run_on_node(host, user, passwd, cmd):
    ssh    = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=passwd, look_for_keys=False)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print stdout.readlines()
    ssh.close()

if __name__ == "__main__":
    # Set your username/API key
    rackspace = Rackspace("username","api_key")
    
    # Create and wait for the node to build
    testnode = create_and_build("testnode", RackspaceImage.Arch_2009_02, RackspaceSize.RAM_256MB)

    # Node is Active but wait 10s (arbitrary) for SSH to start answering
    time.sleep(10) 
    
    # Now let's execute a simple command on the node we just created
    run_on_node(testnode.public_ip[0], user="root", passwd=testnode.password, cmd="uname -a")

    # We're done with our test, let's destroy the node!
    rackspace.destroy_node(testnode)
