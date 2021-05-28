import os
import redis
from rq import Worker, Queue, Connection
from config import CONFIG

# rq-server
listen = ["default", "model-tasks"]
conn = redis.from_url(CONFIG.REDIS_URL)

if __name__ == "__main__":
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()