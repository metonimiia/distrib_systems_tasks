import argparse
import threading
import time

import grpc
import requests
import uvicorn
from fastapi import FastAPI

import service_pb2
import service_pb2_grpc
from service import create_server


REST_HOST = "127.0.0.1"
REST_PORT = 18080
GRPC_HOST = "127.0.0.1"
GRPC_PORT = 50080


app = FastAPI()
rest_data = {"id": 0}


@app.post("/api/notifications")
def create_notification(payload: dict):
    # Простейший REST-обработчик: сохраняем данные в памяти и возвращаем их.
    rest_data["id"] += 1
    return {
        "id": rest_data["id"],
        "text": payload.get("text", ""),
        "channel": payload.get("channel", "general"),
    }


def wait_for_rest():
    # Ждём, пока REST-сервис поднимется и начнёт отвечать.
    url = f"http://{REST_HOST}:{REST_PORT}/api/notifications"
    for _ in range(100):
        try:
            requests.post(url, json={"text": "warmup", "channel": "bench"}, timeout=0.5)
            return
        except requests.RequestException:
            time.sleep(0.05)
    raise RuntimeError("REST server did not start")


def wait_for_grpc():
    # Ждём готовности gRPC-канала.
    target = f"{GRPC_HOST}:{GRPC_PORT}"
    for _ in range(100):
        try:
            with grpc.insecure_channel(target) as channel:
                grpc.channel_ready_future(channel).result(timeout=0.5)
                return
        except Exception:
            time.sleep(0.05)
    raise RuntimeError("gRPC server did not start")


def benchmark_rest(iterations: int):
    # Замеряем время для N REST-запросов.
    url = f"http://{REST_HOST}:{REST_PORT}/api/notifications"
    start = time.perf_counter()
    for i in range(iterations):
        response = requests.post(
            url,
            json={"text": f"n-{i}", "channel": "bench"},
            timeout=2,
        )
        response.raise_for_status()
    elapsed = time.perf_counter() - start
    return elapsed, iterations / elapsed


def benchmark_grpc(iterations: int):
    # Замеряем время для N gRPC unary-запросов.
    target = f"{GRPC_HOST}:{GRPC_PORT}"
    with grpc.insecure_channel(target) as channel:
        stub = service_pb2_grpc.NotificationsServiceStub(channel)
        start = time.perf_counter()
        for i in range(iterations):
            stub.Create(service_pb2.Request(text=f"n-{i}", channel="bench"))
        elapsed = time.perf_counter() - start
    return elapsed, iterations / elapsed


def check_streaming():
    # Проверяем, что streaming-метод реально отдаёт несколько сообщений.
    target = f"{GRPC_HOST}:{GRPC_PORT}"
    with grpc.insecure_channel(target) as channel:
        stub = service_pb2_grpc.NotificationsServiceStub(channel)
        updates = list(stub.Subscribe(service_pb2.SubscribeRequest(channel="bench", limit=5)))
    return len(updates)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=1000)
    args = parser.parse_args()

    # Поднимаем REST в отдельном потоке, чтобы бенч выполнялся в одном процессе.
    rest_server = uvicorn.Server(uvicorn.Config(app, host=REST_HOST, port=REST_PORT, log_level="error"))
    rest_thread = threading.Thread(target=rest_server.run, daemon=True)
    rest_thread.start()

    # Поднимаем gRPC-сервер.
    grpc_server = create_server(f"{GRPC_HOST}:{GRPC_PORT}")
    grpc_server.start()

    try:
        wait_for_rest()
        wait_for_grpc()

        print("Запуск бенчмарка...")
        rest_time, rest_rps = benchmark_rest(args.iterations)
        grpc_time, grpc_rps = benchmark_grpc(args.iterations)
        stream_count = check_streaming()

        print(f"REST: {rest_time:.4f} сек, {rest_rps:.2f} req/s")
        print(f"gRPC: {grpc_time:.4f} сек, {grpc_rps:.2f} req/s")
        print(f"Проверка стриминга: получено {stream_count} сообщений")
    finally:
        grpc_server.stop(grace=0)
        rest_server.should_exit = True
        rest_thread.join(timeout=2)


if __name__ == "__main__":
    main()
