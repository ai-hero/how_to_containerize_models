# 3 ways to containerize your ML models.

A basic container to serve models in 3 ways - REST, message queues, and batch processing.

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

A predict request using the requests module can be made like this:

```
request_obj = {
  "text": "I am feeling great!",
  "candidate_labels": ["sad", "happy"],
}
resp = requests.post(f"{server_url}/predict", json=request_obj)
resp.raise_for_status()

prediction = resp.json()
# 'prediction' will be {'label': 'happy', 'score': 0.9991405010223389}
```

The full example can be found in [http_client.py](examples/http_client.py). You might also want to install the requirements in [requirements.txt](examples/requirements.txt), and check out the [environment variables](examples/.env).

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

The producer makes the predict request using message queue on the requests topic like this:

```
# Connect to redis
redis_url = os.environ.get("REDIS_URL")
redis_connection = redis.Redis.from_url(redis_url)
predict_request_topic = os.environ.get("PREDICT_REQUEST_TOPIC")

# Create id for tracking our response
_id = str(uuid4())

# Send predict request
request_obj = {
    "text": "I am feeling great!",
    "candidate_labels": ["sad", "happy"],
    "id": _id,
}
redis_connection.lpush(predict_request_topic, json.dumps(request_obj))
```

The consumer, meanwhile, is waiting for the response from the service on the response topic:

```
# Connect to redis
redis_url = os.environ.get("REDIS_URL")
redis_connection = redis.Redis.from_url(redis_url)
predict_response_topic = os.environ.get("PREDICT_RESPONSE_TOPIC")

# Get response
_, msg = redis_connection.blpop(predict_response_topic)
prediction = json.loads(msg)

# prediction will be {
#  'label': 'happy',
#  'score': 0.9991405010223389,
#  'id': 'd856fb6b-55e1-4c47-a407-eb2169e6c781'
# }
```

The full example can be found in [mq_client.py](examples/mq_client.py). You might also want to install the requirements in [requirements.txt](examples/requirements.txt), and check out the [environment variables](examples/.env).

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

# Batch processing with a long running task

## Running the batch process example

To run the batch process example, we run:

```
make batch_process
```

## Processing a csv file

For this example, we mount a volume to the container, and our execution command includes the paths in the mounted location to the labels.txt file, the inputs csv file and the expected output file. The process then loads the input csv and labels.txt file provided in the command line arguments and generates the output csv file.

### Batch process using a file.

Since this is not a client-server architecture, we don't need additional code.

The input csv looks like this:

```
text
I'm meeting amy friends tonight!
"Oh no, my team lost :("
I bought a new phone!
```

The output csv looks like this:

```
text,label,score
I'm meeting amy friends tonight!,happy,0.9462801814079285
"Oh no, my team lost :(",sad,0.9981276392936707
I bought a new phone!,happy,0.9799920320510864
```

These files can be found in the `examples/` folder.

## Logs

Since the container is not run detatched, you can check the logs as the make command executes.

# CI/CD

To test, run:

```
make test
```
