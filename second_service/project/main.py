import logging
import sqlite3
import json

import pika

from db import con


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def query_to_db(data: dict, connection: sqlite3.Connection) -> dict:
    connection.row_factory = dict_factory
    cur = connection.cursor()
    cur.execute("""SELECT rowid, product_name, price FROM catalog WHERE rowid=:id """, {'id': data.get('r_id')})
    res = cur.fetchall()
    try:
        return res[0]
    except IndexError:
        return {'message': f'There is no record with id: {data.get("r_id")}'}


def insert_to_db(data: dict, connection: sqlite3.Connection) -> dict:
    cur = connection.cursor()
    cur.execute("""INSERT INTO catalog VALUES(?, ?)""", (data.get('product_name'), data.get('price')))
    con.commit()
    return {'message': 'ok'}


class Connection:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.URLParameters('amqp://myuser:mypassword123@rabbitmq:5672/'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='rpc_exchange', exchange_type='topic')
        self.channel.basic_qos(prefetch_count=0)

    def on_request(self, ch, method, props, body):
        funcs = {
            'rpc_request.select': query_to_db,
            'rpc_request.insert': insert_to_db
        }
        res = funcs.get(method.routing_key)(json.loads(body.decode('utf-8')), con)
        self.channel.basic_publish(
            exchange='rpc_exchange',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=json.dumps(res)
        )

    def consume_for_request(self):
        self.channel.queue_declare('rpc_request', durable=True)
        self.channel.queue_declare('rpc_response', durable=True)
        self.channel.queue_bind(queue='rpc_request', exchange='rpc_exchange', routing_key='rpc_request.select')
        self.channel.queue_bind(queue='rpc_request', exchange='rpc_exchange', routing_key='rpc_request.insert')
        self.channel.basic_consume(queue='rpc_request', on_message_callback=self.on_request, auto_ack=True)
        self.channel.start_consuming()


cn = Connection()
cn.consume_for_request()
