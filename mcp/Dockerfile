FROM python:3.12-slim
RUN pip install --no-cache-dir "mcp>=1.10,<2"
WORKDIR /app
COPY server.py .
CMD ["python", "server.py"]
