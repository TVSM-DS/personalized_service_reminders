# FROM python:3.8-slim-buster
# FROM python:3.10.10
# COPY . /app
# WORKDIR /app
# RUN pip install -r requirements.txt --use-deprecated=legacy-resolver
# EXPOSE 8501
# ENTRYPOINT ["streamlit","run"]
# CMD ["app.py"]


FROM python:3.10.10
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]