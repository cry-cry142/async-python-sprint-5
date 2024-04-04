FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY .aws/. /root/.aws/

COPY . .

CMD ["python", "main.py"]
