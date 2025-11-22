# image python 3.12
FROM python:3.12-slim

WORKDIR /src

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

COPY . .

CMD ["python","src/app.py"]
