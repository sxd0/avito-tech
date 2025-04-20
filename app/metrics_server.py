from prometheus_client import start_http_server, Counter, Histogram
from time import time
from threading import Thread

REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests",
    ["method", "endpoint"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "Duration of HTTP requests in seconds",
    ["endpoint"]
)

PVZ_CREATED = Counter("business_pvz_created_total", "Number of created PVZ")
RECEPTIONS_CREATED = Counter("business_receptions_created_total", "Number of created receptions")
PRODUCTS_CREATED = Counter("business_products_created_total", "Number of created products")

def run_metrics_server():
    print("🚀 Prometheus metrics available on port 9000")
    start_http_server(9000)

def observe_request(endpoint: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            REQUEST_COUNT.labels(method="POST", endpoint=endpoint).inc()
            start = time()
            result = func(*args, **kwargs)
            REQUEST_LATENCY.labels(endpoint=endpoint).observe(time() - start)
            return result
        return wrapper
    return decorator

Thread(target=run_metrics_server, daemon=True).start()
