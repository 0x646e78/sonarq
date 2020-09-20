sonarq - a local soonarqube scanning solution
---

`sonarq.py` provides a local sonarqube scanner & server solution, driven from the cli.

It uses ephemeral scanners and creates/starts a sonarqube server with local web access.

## Use

```
./sonarq.py <code_path>
```

Further options cam be viewed with `--help`

A link to the completed scan will be printed to stdout. By default the server will be avaiable on [http://localhost:9000](http://localhost:9000)

To stop or remove the server is currently via docker:

```
docker stop sonar-server
```

## Install

### Pre-requsites:

- docker
- python3

### Set up & source a python virtual env

```
python3 -m venv venv
. venv/bin/activate
```

### Install libraries

```
pip3 install -r requirements.txt
```


## Example

```
./sonarq.py ./
Beginning sonarq tasks for /Users/dnx/dev/pub/sonarq
Creating docker network sonarq for project sonarq
Starting a new sonarqube server
Sonarqube server is available at http://127.0.0.1:9000
Creating a new Sonarqube project named sonarq
Starting a sonarqube scan of sonarq. This could take a while.
Scan complete. Results are available at the following url (user/pass = admin/admin)

http://127.0.0.1:9000/dashboard?id=sonarq
```
