#/usr/bin/env python
from datetime import datetime
from dotenv import load_dotenv
import os
import sys
import uuid



from fabric.api import env, task, put, sudo, local, cd, lcd, run, prompt
from fabric.colors import red, green, blue, yellow
from fabric.api import shell_env
from fabric.context_managers import cd, prefix, settings, hide





# GROCCAD HOST (GCP instance)
################################################################################
env.hosts = ['35.203.84.59']
env.user = 'ivan'
env.DOCKER_HOST = "ssh://ivan@35.203.84.59"

# env.credentials_dotenv_path = 'credentials/??'




@task
def reset_n_load():
    local('./manage.py reset_db')
    local('./manage.py migrate')



# PROVISION DOCKER ON REMOTE HOST
################################################################################

@task
def install_docker():
    """
    Install docker on remote host following the instructions from the docs:
    https://docs.docker.com/engine/install/debian/#install-using-the-repository
    """
    with settings(warn_only=True), hide('stdout', 'stderr', 'warnings'):
        sudo('apt-get -qy remove docker docker-engine docker.io containerd runc')
    with hide('stdout'):
        sudo('apt-get update -qq')
        sudo('apt-get -qy install apt-transport-https ca-certificates curl gnupg-agent software-properties-common')
    sudo('curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -')
    sudo('add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"')
    with hide('stdout'):
        sudo('apt-get update -qq')
        sudo('apt-get -qy install docker-ce docker-ce-cli containerd.io')
    sudo('usermod -aG docker {}'.format(env.user))  # add user to `docker` group
    sudo("sed -i 's/^#MaxSessions 10/MaxSessions 30/' /etc/ssh/sshd_config")
    # docker-compose opens >10 SSH sessions, hence the need to up default value
    # via https://github.com/docker/compose/issues/6463#issuecomment-458607840
    # TODO sysctl -w vm.max_map_count=262144
    sudo('service sshd restart')
    print(green('Docker installed on ' + env.host))


@task
def uninstall_docker(deep=False):
    """
    Uninstall docker using instructions from the official Docker docs:
    https://docs.docker.com/engine/install/debian/#uninstall-docker-engine
    """
    deep = (deep and deep.lower() == 'true')  # defaults to False
    with hide('stdout'):
        sudo('apt-get -qy purge docker-ce docker-ce-cli containerd.io')
        if deep:
            sudo('rm -rf /var/lib/docker')
            sudo('rm -rf /var/lib/containerd')
    print(green('Docker uninstalled from ' + env.host))



# FWD DOCKER COMMANDS TO REMOTE HOST
################################################################################

@task
def dlocal(command):
    """
    Execute the `command` (srt) on the remote docker host `env.DOCKER_HOST`.
    If `env.DOCKER_HOST` is not defined, execute `command` on the local docker.
    Docker remote execution via SSH requires remote host to run docker v18+.
    """
    if 'DOCKER_HOST' in env:
        with shell_env(DOCKER_HOST=env.DOCKER_HOST):
            local(command)  # this will run the command on remote docker host
    else:
        local(command)      # this will use local docker (if installed)



# DOCKER COMMANDS
################################################################################

@task
def dlogs(container, options=''):
    cmd = 'docker logs '
    cmd += options
    cmd += ' {}'.format(container)
    dlocal(cmd)

@task
def dps(options=''):
    cmd = 'docker ps '
    cmd += options
    dlocal(cmd)

@task
def dshell(container):
    cmd = 'docker exec -ti {} /bin/bash'.format(container)
    dlocal(cmd)

@task
def dexec(container, command, options='-ti'):
    cmd = 'docker exec '
    cmd += options
    cmd += ' {} bash -c \'{}\''.format(container, command)
    dlocal(cmd)

@task
def dsysprune(options=''):
    cmd = 'docker system prune -f '
    cmd += options
    dlocal(cmd)



# DOCKER COMPOSE COMMANDS
################################################################################

@task
def dclogs(options=''):
    cmd = 'docker-compose logs '
    cmd += options
    dlocal(cmd)

@task
def dcbuild(service='', options=''):
    cmd = 'docker-compose build '
    cmd += options
    cmd += '  ' + service
    dlocal(cmd)

@task
def dcup(options='-d'):
    cmd = 'docker-compose up '
    cmd += options
    dlocal(cmd)

@task
def dcdown(options=''):
    cmd = 'docker-compose down '
    cmd += options
    dlocal(cmd)

