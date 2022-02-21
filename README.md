Simple microservices with python, rabbitmq, FastAPI and pika.

## Steps to run:

<div class="termy">

```console
$ git clone https://github.com/BmeUP/services.git
$ cd services/composes
$ sudo docker-compose -f docker-compose.rabbitmq.yml up
$ sudo docker-compose -f docker-compose.second-service.yml up
$ sudo docker-compose -f docker-compose.first-service.yml up

```
</div>

Folow this http://127.0.0.1:8000/docs in your browser.