FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x run_local.sh
EXPOSE 5000 6000
CMD ["./run_local.sh"]
