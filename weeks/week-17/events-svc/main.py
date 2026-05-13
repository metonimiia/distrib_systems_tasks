import os
import grpc
import uuid
import logging
from concurrent import futures

import events_pb2
import events_pb2_grpc

# Настройка базового логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventsServiceServicer(events_pb2_grpc.EventsServiceServicer):
    """
    Реализация gRPC сервиса для работы с событиями (Events).
    """
    def __init__(self):
        # Временное хранилище событий в памяти
        self.events = []

    def GetEvents(self, request, context):
        # Обработка запроса на получение списка событий
        logger.info("Обработка запроса GetEvents")
        return events_pb2.EventList(events=self.events)

    def CreateEvent(self, request, context):
        # Обработка запроса на создание нового события
        logger.info(f"Обработка запроса CreateEvent: {request.name}")
        event = events_pb2.Event(id=str(uuid.uuid4()),name=request.name,location=request.location)
        self.events.append(event)
        return event

def serve():
    # Получение порта из переменной окружения или использование 8257 по умолчанию
    port = os.environ.get("PORT", "8257")
    # Создание gRPC сервера с пулом потоков
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Регистрация нашего сервиса на сервере
    events_pb2_grpc.add_EventsServiceServicer_to_server(EventsServiceServicer(), server)
    # Добавление порта для приема незащищенных соединений
    server.add_insecure_port(f'[::]:{port}')
    logger.info(f"gRPC сервис событий запускается на порту {port}...")
    server.start()
    # Ожидание завершения работы сервера
    server.wait_for_termination()

if __name__ == '__main__':
    serve()