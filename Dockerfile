FROM python:3.7.2

COPY requirements.txt /app/
COPY t_exporter.py /app/

WORKDIR /app/

RUN pip install -r requirements.txt

CMD ["python", "t_exporter.py"]