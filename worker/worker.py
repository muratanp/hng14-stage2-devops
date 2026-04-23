import redis
import time
import os
import signal
import sys

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") or None

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

running = True


def handle_shutdown(signum, frame):
    global running
    print(f"Received signal {signum}. Shutting down gracefully...", flush=True)
    running = False


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)


def process_job(job_id):
    print(f"Processing job {job_id}", flush=True)
    time.sleep(2)  # simulate work
    r.hset(f"job:{job_id}", "status", "completed")
    print(f"Done: {job_id}", flush=True)


print("Worker started. Waiting for jobs...", flush=True)

while running:
    job = r.brpop("jobs", timeout=5)
    if job:
        _, job_id = job
        process_job(job_id.decode())

print("Worker exited cleanly.", flush=True)
sys.exit(0)
