import os
import grpc
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Импорт сгенерированных файлов gRPC
import events_pb2
import events_pb2_grpc

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Инициализация REST-шлюза
app = FastAPI(title="Сервис Gateway", description="Шлюз для преобразования REST запросов в gRPC")
# Получение адреса gRPC-сервиса (из Docker окружения или локальный по умолчанию)
EVENTS_SVC_HOST = os.environ.get("EVENTS_SVC_HOST", "events-svc-s12:8257")
# Валидация входящего JSON для создания события
class EventModel(BaseModel):
    name: str
    location: str

@app.get("/api/events")
def get_events():
    """Отдает список всех событий."""
    logger.info("Перенаправление GET /api/events в gRPC сервис")
    try:
        # Открытие канала связи с микросервисом
        with grpc.insecure_channel(EVENTS_SVC_HOST) as channel:
            stub = events_pb2_grpc.EventsServiceStub(channel) # Создание gRPC-клиента
            # Вызов метода на удаленном сервере
            response = stub.GetEvents(events_pb2.Empty())
            # Возврат данных в виде JSON-совместимого списка
            return [{"id": e.id, "name": e.name, "location": e.location} for e in response.events]
    except Exception as e:
        logger.error(f"Ошибка при вызове gRPC сервиса: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.post("/api/events")
def create_event(event: EventModel):
    """Создает новое событие."""
    logger.info(f"Перенаправление POST /api/events в gRPC сервис для события: {event.name}")
    try:
        # Открытие канала связи с микросервисом
        with grpc.insecure_channel(EVENTS_SVC_HOST) as channel:
            stub = events_pb2_grpc.EventsServiceStub(channel) # Создание gRPC-клиента
            # Формирование gRPC-запроса из данных REST-запроса и его отправка
            response = stub.CreateEvent(events_pb2.Event(name=event.name, location=event.location))
            # Возврат созданного объекта клиенту
            return {"id": response.id, "name": response.name, "location": response.location}
    except Exception as e:
        logger.error(f"Ошибка при вызове gRPC сервиса: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")