# 3 ways to containerize your ML models.

A basic container to serve models in 3 ways - REST, message queues, cron jobs w/ Celery

# Serving HTTP endpoint using docker compose

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

# CI/CD

To test, run:

```
make test
```
