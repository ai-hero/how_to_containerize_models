# 3 ways to containerize your ML models.

A basic container to serve models in 3 ways - REST, message queues, async jobs

# Serving the model using an HTTP endpoint

## Running the Server

To run the server in detached mode, we run:

```
make serve
```

To run the server not without detaching, we run:

```
make run
```

## Hitting the predict endpoint

Docker compose exposes the container at `http://localhost:8080`.

### Using cURL

To get a prediction we run a cURL request:

```
curl -X POST http://localhost:8080/predict  \
    -H 'Content-Type: application/json'  \
    -d '{"text":"I am feeling great!","candidate_labels":["sad", "happy"]}'
```

You will see the JSON response like:

```
{
  "label": "happy",
  "score": 0.9991405010223389
}
```

### Using Python Requests Module

A full example for using the Python requests module can be found in [http_client.py](examples/http_client.py). You might also want to install the requirements in [requirements.txt](examples/requirements.txt), and check out the [environment variables](examples/.env).

## Logs

You can check the logs of the container using:

```
docker logs -f zero_shot
```

## Shutdown

You can shut down the server using

```
make stop
```

# Serving the Model with a Message Queue

## Running the Service

To run the application in detached mode, we run:

```
make serve_mq
```

## Hitting the predict endpoint

Docker compose exposes the container at `http://localhost:8080`.

### Using Redis Client Producer and Consumer

A full example for using the redis client can be found in [mq_client.py](examples/mq_client.py). You might also want to install the requirements in [requirements.txt](examples/requirements.txt), and check out the [environment variables](examples/.env).

## Logs

You can check the logs of the container using:

```
docker logs -f zero_shot_mq
```

## Shutdown

You can shut down the service using

```
make stop
```

# CI/CD

To test, run:

```
make test
```
