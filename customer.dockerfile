FROM python:3

RUN mkdir -p /opt/src/application
WORKDIR /opt/src/application

COPY application/admin.py ./admin.py
COPY application/adminDecorator.py ./adminDecorator.py
COPY application/configuration.py ./configuration.py
COPY application/customer.py ./customer.py
COPY application/daemon.py ./daemon.py
COPY application/manage.py ./manage.py
COPY application/models.py ./models.py
COPY application/requirements.txt ./requirements.txt
COPY application/storekeeper.py ./storekeeper.py

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./customer.py"]