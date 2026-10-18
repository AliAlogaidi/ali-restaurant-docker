# Small Python runtime; this chatbot needs no pip packages.
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 HOST=0.0.0.0 DATABASE_PATH=/data/simple-ali.db
COPY simple-ali-chatbot.py .
# A separate writable folder keeps the database outside the application code.
RUN mkdir -p /data && chown 10001:10001 /data
USER 10001:10001
EXPOSE 8001
CMD ["python", "simple-ali-chatbot.py"]
