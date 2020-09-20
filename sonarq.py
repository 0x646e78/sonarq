#!/usr/bin/env python3

import docker
import argparse
import json
import os
import time
from datetime import datetime
from datetime import timezone
from sonarqube import SonarQubeClient

scanner_image='sonarsource/sonar-scanner-cli'
server_image='sonarqube:lts'
server_name='sonar-server'
server_user='admin'
server_pass='admin' #Please don't bug me about this yet :P
docker_network='sonarq'

#TODO: logger
#TODO: __main__

class Infra():
    def __init__(self):
        self.client = docker.from_env()

    def check_network(self):
        try:
            self.client.networks.get(docker_network)
        except docker.errors.NotFound:
            print(f'Creating docker network {docker_network} for sonarqube')
            self.client.networks.create(docker_network)

    def run_server(self):
        try:
            print('Launching a new sonarqube server')
            container = self.client.containers.run(server_image,
                            name=server_name,
                            network=docker_network,
                            ports={'9000/tcp': (host_ip, host_port)},
                            detach=True)
        except Exception as e:
            print(e)
            exit(1)
        return container

    def run_scan(self, code_path, project_name, token):
        try:
            print(f'Starting a sonarqube scan of {project_name}. This could take a while depending on project size')
            container = self.client.containers.run(scanner_image,
                            f'-Dsonar.projectKey={project_name} -Dsonar.login={token} -Dsonar.working.directory=/tmp',
                            environment={'SONAR_HOST_URL': f'http://{server_name}:{host_port}'},
                            name='sonar-scanner',
                            network=docker_network, 
                            volumes={code_path: {'bind': '/usr/src', 'mode': 'ro'}},
                            remove=True)
        except Exception as e:
            #TODO clean up container 
            print(e)
            exit(1)

    def server_status(self):
        try:
            return self.client.containers.get(server_name).status
        except docker.errors.NotFound:
            return False

    def start_server(self):
        print('Starting sonar server')
        return self.client.containers.get(server_name).start()

    def stop(self):
        print('Stopping sonar server')
        return self.client.containers.get(server_name).stop()

    def kill(self):
        print('Removing sonar server')
        return self.client.containers.get(server_name).remove(force=True)

#argparse TODO:
# scan even if not a git repo
# password for server
parser = argparse.ArgumentParser(description='Local sonarqube scanning.')
parser.add_argument('-n', '--project-name', 
                    help='Project name to use in SonarQube, defaults to code folder name')
parser.add_argument('--ip', default='127.0.0.1',
                    help='Local host IP to bind to, defaults to 127.0.0.1.')
parser.add_argument('--port', default='9000',
                    help='Local host port to bind to, defaults to 9000.')
parser.add_argument('--stop-server', action='store_true',
                    help="Stop the server")
parser.add_argument('--kill-server', action='store_true',
                    help="Destroy the server")
parser.add_argument('path', nargs='?')
args = parser.parse_args()

infra = Infra()
if args.kill_server:
    infra.kill()
    exit(0)
if args.stop_server:
    infra.stop()
    exit(0)

if not args.path:
    parser.error('Must specify a code path')
code_path = os.path.abspath(args.path)

if args.project_name:
    project_name = args.project_name
else:
    project_name = os.path.basename(os.path.normpath(code_path))
host_ip = args.ip
host_port = args.port

#TODO check code path exists and is a git repo

print(f'Beginning sonarq tasks for {code_path}')

#check docker network, create if non existent
infra.check_network()

#check server status, run or start if needed if not found
start_time = int(datetime.now(tz=timezone.utc).timestamp())
state = infra.server_status()
if state != 'running':
    if not state:
        container = infra.run_server()
        time.sleep(20)
    elif state == 'exited':
        infra.start_server()
        time.sleep(15)
        container = infra.client.containers.get(server_name)
    while True:
        if infra.server_status() == 'running':
            logs = str(container.logs(since=start_time))
            if 'SonarQube is up' in logs:
                break
        else:
            time.sleep(3)
   
#auth to server
s = SonarQubeClient(sonarqube_url=f'http://{host_ip}:{host_port}', username=server_user, password=server_pass)
print(f'Sonarqube server is available at http://{host_ip}:{host_port}')

#Create a token
sonar_tokens = s.user_tokens.search_user_tokens(user_login=server_user)
for i in sonar_tokens:
    if i['name'] == project_name:
        s.user_tokens.revoke_user_token(project_name, user_login=server_user)
sonar_token = s.user_tokens.generate_user_token(project_name, user_login=server_user).json()['token']

#check if project exists in sonar, create if not
project = list(s.projects.search_projects(projects=project_name))
if len(project) < 1:
    print(f'Creating a new Sonarqube project named {project_name}')
    project = s.projects.create_project(project=project_name, name=project_name, visibility='private')
else:
    print(f'Using existing Sonarqube project for {project_name}')
    project = project[0]

#run the scan
infra.run_scan(code_path, project_name, sonar_token)

#output the link to the project
print('Scan complete. Results are available at the following url (user/pass = admin/admin)')
print(f'\nhttp://{host_ip}:{host_port}/dashboard?id={project_name}\n')

#TODO: output the main stats
