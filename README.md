# [api.dantran.fr](https://api.dantran.fr/docs)

Backend of https://dantran.fr

Playing with the following stack:
* Python (FastAPI)
* MongoDB
* MinIO

Provided endpoints:
* `/music`

See the frontend project: [MrDanao/website](https://github.com/MrDanao/website)

## Run locally

The following requirements must be installed on your local host:
* Docker Engine (only tested with v20.10.6)
* Docker Compose (only tested with v1.28.6)

### Development

Make sure the environment is clean:

```
$ docker-compose -f dev.docker-compose.yml down
```

Build and run the environment (same command after changes):

```
$ docker-compose -f dev.docker-compose.yml up -d --build
```

Access to:
* Swagger UI: `http://<localhost|host_ip>:8000/docs`
* ReDoc UI: `http://<localhost|host_ip>:8000/redoc`
* MinIO UI: `http://<localhost|host_ip>:9000/`

See logs:

```
$ docker-compose -f dev.docker-compose.yml logs -f
```

Tear down the environment:

```
$ docker-compose -f dev.docker-compose.yml down
```

### Tests

Make sure the environment is clean:

```
$ docker-compose -f test.docker-compose.yml down
```

Build and run tests, with logs:

```
$ docker-compose -f test.docker-compose.yml up --exit-code-from=test-app --build
```

Tear down the environment:

```
$ docker-compose -f test.docker-compose.yml down
```
