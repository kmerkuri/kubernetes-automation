FROM python:3.8-slim
WORKDIR /app
COPY main.py requirements.txt /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt
CMD ["python", "main.py"]
