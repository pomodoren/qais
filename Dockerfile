FROM python:3.7.9-slim-stretch
COPY . /service
WORKDIR /service/api
RUN pip install -r ./requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]

