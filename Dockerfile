FROM python:3.11.13-slim

WORKDIR /amc-website

ENV FLASK_ENV=production
ENV DATABASE_URL=sqlite:////amc-website/instance/amc_website.db

COPY requirements.txt . 

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
