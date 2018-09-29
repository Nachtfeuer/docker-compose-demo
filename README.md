# Welcome to the docker-compose primer


## Building the image for the primes server

```bash
docker build -t demo/primes-server:latest . -f images/Dockerfile.primes_server
```

## Running the primes server directly

```bash
$ docker run --rm --name=primes-server -p 5000:5000 -d demo/primes-server:latest
$ curl http://localhost:5000/primes/check/3
{"isPrime": true, "number": 3}
$ curl http://localhost:5000/primes/check/4
{"isPrime": false, "number": 4}
```

## Using docker-compose for starting the primes server

```bash
$ docker-compose -f compose/docker-compose-server.yml up -d primes-server
$ docker ps
CONTAINER ID        IMAGE                       COMMAND                  CREATED              STATUS              PORTS                    NAMES
29177c0471cf        demo/primes-server:latest   "flask run --host=0.…"   About a minute ago   Up About a minute   0.0.0.0:5000->5000/tcp   docker-compose-demo_primes-server_1
$ curl http://localhost:5000/primes/check/3
{"isPrime": true, "number": 3}
$ curl http://localhost:5000/primes/check/4
{"isPrime": false, "number": 4}
```

The `-d` is that docker compose starts the process into background.
Avoiding that more services are started the service **prime-service** is specified.
You can shutdown with `docker-compose -f compose/docker-compose-server.yml down`.


## Running multipe prime servers with haproxy

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
