# Отчет по Docker

- Image size: `week10-app-s12:latest` = `140MB`.
- Layer count (`docker history -q week10-app-s12 | wc -l`): `15`.
- Слои (layers): отдельные слои создают команды `COPY requirements.txt`, `RUN pip install ...`, `COPY --from=builder /install /usr/local`, `COPY main.py`, `EXPOSE`, `CMD`.
- Команда сборки: `docker build -t week10-app-s12 .`
- Команда запуска: `docker run --rm -p 8273:8273 week10-app-s12`
