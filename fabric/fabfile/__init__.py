# -*- coding: utf-8 -*-
"""Fabric provisioning for bare-minimum setup of server and deploying the xl_auth application."""

from __future__ import absolute_import, division, print_function, unicode_literals

from fabric.contrib.files import upload_template
from fabric.api import env, local, task, sudo, cd, run

from . import docker


@task
def vagrant():
    """Invoke as first task of `fab vagrant do-something` when testing with Vagrant."""
    env.user = 'vagrant'
    env.hosts = ['127.0.0.1:2222']

    # Use Vagrant SSH key (something like './.vagrant/machines/default/virtualbox/private_key').
    result = local('vagrant ssh-config | grep IdentityFile', capture=True)
    env.key_filename = result.split()[1]


@task
def prepare():
    """Prepare server with bare-minimum capabilities."""
    docker.setup()


@task
def setup(inventory_hostname=None, xl_auth_admin_pass=None, xl_auth_import_data=False,
          **env_override_kwargs):
    """Configure and start the xl_auth application and database (possibly importing stuff, etc)."""
    if not inventory_hostname:
        inventory_hostname = _get_eth0_ip_addr()

    env.update({  # Defaults.
        'inventory_hostname': inventory_hostname,
        'server_name': inventory_hostname + ':5000',
        'xl_auth_admin_pass': xl_auth_admin_pass,
        'xl_auth_gelf_address': 'udp://localhost:12201'
    })
    env.update(env_override_kwargs)

    _upload_docker_compose_yml()
    _pull_and_start_containers()
    _run_db_upgrade()

    if xl_auth_admin_pass:
        _set_libris_at_kb_se_admin_pass(xl_auth_admin_pass)

    if xl_auth_import_data:
        _import_data_from_bibdb_and_voyager()


def _get_eth0_ip_addr():
    return run('echo $(ip addr show eth0 | grep "inet\\b" | awk \'{print $2}\' | '
               'cut -d/ -f1)').splitlines()[0]


def _upload_docker_compose_yml():
    sudo('mkdir -p /opt/xl_auth')
    upload_template('docker-compose.yml.j2', '/opt/xl_auth/docker-compose.yml', context=env,
                    use_jinja=True, use_sudo=True)


def _pull_and_start_containers():
    with cd('/opt/xl_auth'):
        sudo('docker-compose pull')
        sudo('docker-compose up --no-start')
        sudo('docker-compose restart && sleep 10')


def _run_db_upgrade():
    sudo('docker exec -it xl_auth /usr/local/bin/flask db upgrade')


def _set_libris_at_kb_se_admin_pass(password):
    sudo('docker exec -it xl_auth /usr/local/bin/flask create_user -e libris@kb.se -p"%s" --force '
         '--is-admin --is-active' % password)


def _import_data_from_bibdb_and_voyager():
    sudo('docker exec -it xl_auth /usr/local/bin/flask import_data --admin-email=libris@kb.se -v '
         '--wipe-permissions')
