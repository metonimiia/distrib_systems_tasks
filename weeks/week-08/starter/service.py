from concurrent import futures
import time

import grpc

import service_pb2
import service_pb2_grpc


class NotificationsService(service_pb2_grpc.NotificationsServiceServicer):
    def __init__(self):
        # Простой счётчик ID в памяти (для учебного примера этого достаточно).
        self.next_id = 1

    def new_id(self) -> str:
        value = str(self.next_id)
        self.next_id += 1
        return value

    def Create(self, request, context):
        # Unary RPC: один запрос -> один ответ.
        notification_id = self.new_id()
        return service_pb2.Response(
            id=notification_id,
            message=f"Saved '{request.text}' in channel '{request.channel}'",
        )

    def Subscribe(self, request, context):
        # Server Streaming: один запрос -> поток ответов.
        channel = request.channel or "general"
        limit = request.limit if request.limit > 0 else 5

        for i in range(limit):
            yield service_pb2.Update(
                id=self.new_id(),
                text=f"update {i + 1}",
                channel=channel,
            )
            time.sleep(0.05)


def create_server(bind_addr: str = "127.0.0.1:50080"):
    # Создаём gRPC-сервер и регистрируем реализацию сервиса.
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_NotificationsServiceServicer_to_server(
        NotificationsService(),
        server,
    )
    port = server.add_insecure_port(bind_addr)
    if port == 0:
        raise RuntimeError(f"Cannot bind gRPC server to {bind_addr}")
    return server


def serve(bind_addr: str = "127.0.0.1:50080"):
    server = create_server(bind_addr)
    server.start()
    print(f"gRPC сервер запущен на {bind_addr}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
