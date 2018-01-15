# -*- coding: utf-8 -*-
"""Fabric provisioning for bare-minimum setup of server and deploying the xl_auth application."""

from __future__ import absolute_import, division, print_function, unicode_literals

# noinspection PyCompatibility
from cStringIO import StringIO

from fabric.api import env, local, task

from . import docker


@task
def vagrant():
    """Invoke as first task of `fab vagrant do-something` when testing with Vagrant."""
    # Change from the default user to 'vagrant'.
    env.user = 'vagrant'
    # Connect to the port-forwarded SSH.
    env.hosts = ['127.0.0.1:2222']

    # Use Vagrant SSH key (something like './.vagrant/machines/default/virtualbox/private_key').
    result = local('vagrant ssh-config | grep IdentityFile', capture=True)
    env.key_filename = result.split()[1]


@task
def prepare():
    docker.setup()
