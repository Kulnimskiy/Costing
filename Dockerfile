FROM python:3.11-alpine
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENV FLASK_APP=./project/app.py
CMD ["flask", "run", "--host=0.0.0.0"]