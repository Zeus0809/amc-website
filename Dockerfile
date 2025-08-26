FROM python:3.11.13-slim

WORKDIR /amc-website

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
