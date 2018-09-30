# Welcome to the docker-compose demo

**Table Of Contents**

 - [Thoughts](#thoughts)
 - [Requirements](#requirements)
 - [Starting the primes server directly](#starting-the-primes-server-directly)
 - [Building the image for the primes server](#building-the-image-for-the-primes-server)
 - [Running the primes server as Docker container](#running-the-primes-server-as-docker-container)
 - [Using docker-compose for starting the primes server](#using-dockercompose-for-starting-the-primes-server)
 - [Running multiple prime servers with a loadbalancer](#running-multiple-prime-servers-with-a-loadbalancer)
 - [Scaling the primes server](#scaling-the-primes-server)
 - [Health check](#health-check)
 - [Links](#links)

## Thoughts

 - The images can be built locally but the docker-compose also would work if the images are already uploaded
   to a Docker registry; this idea is essential if you want to run such an environment either in Jenkins or
   Travis CI like system as part of a CI/CD (coded pipeline) or via Kubernetes.
 - The good thing is: if it works for those systems it also works locally which is usually not the case
   if you use such tools (Docker and docker-compose) relying on a concrete setup on your machine.
 - The setup and teardown should **always** be **easy** and **fast**.
 - The example server (written in Python) is very short (below 50 lines of code)

## Requirements

 - Please ensure you have at least **Docker 18.06**.
 - You should have at least **docker-compose 1.22.0**.
 - You always should be in the root path of this repository when you execute shown commands.

## Starting the primes server directly

```bash
$ HOSTNAME=demo FLASK_APP=src/primes_server.py flask run
 * Serving Flask app "src/primes_server.py"
 * Environment: production
   WARNING: Do not use the development server in a production environment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

Open another terminal and then:

```bash
$ curl http://127.0.0.1:5000/primes/check/3
{"isPrime": true, "hostname": "demo", "number": 3}
$ curl http://127.0.0.1:5000/primes/check/4
{"isPrime": false, "hostname": "demo", "number": 4}
```

## Building the image for the primes server

It's basically about installing the required Python module **Flask**, adding the python
server to the image and defining the command on how to run the server when the Docker container
for this image is started.

```bash
docker build -t demo/primes-server:latest . -f images/Dockerfile.primes_server
```

## Running the primes server as Docker container

```bash
$ docker run --rm --name=primes-server -p 5000:5000 -d demo/primes-server:latest
$ curl http://localhost:5000/primes/check/3
{"isPrime": true, "hostname": "09d6af743a3f", "number": 3}
$ curl http://localhost:5000/primes/check/4
{"isPrime": false, "hostname": "09d6af743a3f", "number": 4}
```

When stopping the server (`docker stop primes-server`) the container automatically
goes away because of the `--rm` option.

## Using docker-compose for starting the primes server

```bash
$ docker-compose -f compose/docker-compose-server.yml up -d primes-server
$ docker ps
CONTAINER ID        IMAGE                       COMMAND                  CREATED              STATUS              PORTS                    NAMES
29177c0471cf        demo/primes-server:latest   "flask run --host=0.…"   About a minute ago   Up About a minute   0.0.0.0:5000->5000/tcp   docker-compose-demo_primes-server_1
$ curl http://localhost:5000/primes/check/3
{"isPrime": true, "hostname": "09d6af743a3f", "number": 3}
$ curl http://localhost:5000/primes/check/4
{"isPrime": false, "hostname": "09d6af743a3f", "number": 4}
```

The `-d` is that docker compose starts the process into background.
Avoiding that more services are started the service **prime-service** is specified.
You can shutdown with `docker-compose -f compose/docker-compose-server.yml down`.


## Running multiple prime servers with a loadbalancer

```bash
$ docker-compose --compatibility -f compose/docker-compose-loadbalancer.yml up -d
Starting compose_primes-server_1 ... done
Starting compose_primes-server_2 ... done
Starting compose_primes-server_3 ... done
Starting compose_proxy_1         ... done
$ for n in $(seq 1 12); do echo "$(curl -s http://localhost/primes/check/$n)"; done
{"isPrime": false, "hostname": "99a5669c6fa2", "number": 1}
{"isPrime": true, "hostname": "35eeb727e120", "number": 2}
{"isPrime": true, "hostname": "ffda7cf2c91f", "number": 3}
{"isPrime": false, "hostname": "99a5669c6fa2", "number": 4}
{"isPrime": true, "hostname": "35eeb727e120", "number": 5}
{"isPrime": false, "hostname": "ffda7cf2c91f", "number": 6}
{"isPrime": true, "hostname": "99a5669c6fa2", "number": 7}
{"isPrime": false, "hostname": "35eeb727e120", "number": 8}
{"isPrime": false, "hostname": "ffda7cf2c91f", "number": 9}
{"isPrime": false, "hostname": "99a5669c6fa2", "number": 10}
{"isPrime": true, "hostname": "35eeb727e120", "number": 11}
{"isPrime": false, "hostname": "ffda7cf2c91f", "number": 12}
```

- You can see that each response comes from another prime server (hostname).
  Docker usually adjusts the hostname with the id of the container.
- You also can see that the mechanism used here is round robin.
- The `--compatibility` parameter is **required** otherwise the scale feature
  in the yaml configuration (name: deploy) works for Docker swarm only.
- It's also to mention that the concrete Docker image for the haproxy
  seems no longer maintained which does the automatic re-configuration
  depending on current scale. There are other solution with Docker compose
  but I have not yet investigated.
- You shutdown with `docker-compose --compatibility -f compose/docker-compose-loadbalancer.yml down`.

## Scaling the primes server

```bash
docker-compose --compatibility -f compose/docker-compose-loadbalancer.yml up -d --scale=primes-server=10
Starting compose_primes-server_1 ... done
Starting compose_primes-server_2 ... done
Starting compose_primes-server_3 ... done
Creating compose_primes-server_4  ... done
Creating compose_primes-server_5  ... done
Creating compose_primes-server_6  ... done
Creating compose_primes-server_7  ... done
Creating compose_primes-server_8  ... done
Creating compose_primes-server_9  ... done
Creating compose_primes-server_10 ... done
compose_proxy_1 is up-to-date
```

## Health check

The health check can be implemented as REST call of the server.
The server has to tell whether all is fine.

```bash
$ docker ps --format="{{.Names}} {{.Status}}"
compose_proxy_1 Up 43 seconds
compose_primes-server_3 Up 45 seconds (healthy)
compose_primes-server_2 Up 45 seconds (healthy)
compose_primes-server_1 Up 46 seconds (healthy)
```

In the logs of each container you see a record each
10 seconds:

```
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/status"]
  interval: 10s
  timeout: 2s
```

## Links

 - <https://docs.docker.com/compose/install/>
 - <https://docs.docker.com/compose/compose-file/>
 - <https://docs.docker.com/compose/startup-order/>
