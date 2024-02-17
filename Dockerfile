FROM python:3.12-slim
WORKDIR /compressor
COPY . .
RUN pip install .
RUN pip install gunicorn==21.2.0
RUN chmod +x /compressor/run

CMD ["bash", "/compressor/run"]
