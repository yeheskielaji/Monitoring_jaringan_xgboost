FROM python:3.10-slim
WORKDIR /Monitoring_jaringan_xgboost
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["python", "run.py"]
