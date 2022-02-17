from mq_client_consumer import consumer
from mq_client_producer import producer
from threading import Thread

if __name__ == "__main__":
    # Ideally these would be your logic
    # on the flow of the data, before and after
    # prediction.

    # Producer Thread
    p = Thread(target=producer)
    p.start()

    # Consumer Thread
    c = Thread(target=consumer)
    c.start()

    p.join()
    c.join()
