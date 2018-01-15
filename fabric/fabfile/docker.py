# -*- coding: utf-8 -*-
"""Fabric tasks for setting up Docker CE."""

from __future__ import absolute_import, division, print_function, unicode_literals

from fabric.api import put, sudo, task

from six.moves import StringIO as _StringIO


class StringIO(_StringIO, object):
    """Fake 'StringIO', for prettier Fabric output."""

    name = None

    def __init__(self, text, name=''):
        """Add file name to stream object."""
        super(StringIO, self).__init__(text)
        self.name = name


@task
def setup():
    """Install and configure Docker CE."""
    _add_docker_repo()
    _install_docker()
    _configure_docker()
    _restart_docker()
    _add_epel_repo()
    _setup_docker_compose()


@task
def _add_docker_repo():
    put(use_sudo=True, remote_path='/etc/yum.repos.d/docker-ce-stable.repo',
        local_path=StringIO("""[docker-ce-stable]
baseurl = https://download.docker.com/linux/centos/7/$basearch/stable
gpgkey = https://download.docker.com/linux/centos/gpg
name = Docker CE Stable - $basearch
""", name='docker-ce-stable.repo'))


@task
def _install_docker():
    sudo('yum -q install -y docker-ce-17.09.1.ce')


@task
def _configure_docker():
    sudo('mkdir -p /etc/docker')
    put(use_sudo=True, remote_path='/etc/docker/daemon.json',
        local_path=StringIO('{ "iptables": true, "log-driver": "syslog" }', name='daemon.json'))
    sudo('systemctl enable docker')


@task
def _restart_docker():
    sudo('systemctl restart docker')


@task
def _add_epel_repo():
    put(use_sudo=True, remote_path='/etc/yum.repos.d/epel.repo',
        local_path=StringIO("""[epel]
baseurl = http://download.fedoraproject.org/pub/epel/$releasever/$basearch/
gpgkey = http://download.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-$releasever
name: EPEL YUM repo
""", name='epel.repo'))
    sudo('yum -q install -y epel-release')


@task
def _setup_docker_compose():
    sudo('yum -q install -y python-pip')
    sudo('pip -q install pip==9.0.1')
    sudo('pip -q install docker-compose==1.18')
