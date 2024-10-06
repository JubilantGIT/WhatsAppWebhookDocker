FROM python:3-alpine3.15

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 3000

# Run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3000", "app:app"]

