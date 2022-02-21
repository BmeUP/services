import json
import uuid

import pika


class Connection:
    def __init__(self):
        self.creds = pika.PlainCredentials('myuser', 'mypassword123')
        self.params = pika.ConnectionParameters(
            host='rabbitmq',
            port=5672,
            credentials=self.creds)
        self.connection = pika.BlockingConnection(self.params)
        self.channel = self.connection.channel()
        self.channel.queue_bind(queue='rpc_response', exchange='rpc_exchange', routing_key='rpc_response.select')
        self.channel.queue_bind(queue='rpc_response', exchange='rpc_exchange', routing_key='rpc_response.insert')
        self.channel.basic_consume(queue='rpc_response', on_message_callback=self.on_response, auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body.decode('utf-8'))


class RpcClient(Connection):
    def call(self, data):
        x = 1
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='rpc_exchange',
            routing_key='rpc_request.select',
            properties=pika.BasicProperties(
                reply_to='rpc_response.select',
                correlation_id=self.corr_id
            ),
            body=json.dumps(data)
        )
        while self.response is None and x < 1000:
            self.connection.process_data_events()
            x += 1
        return self.response

    def insert(self, data):
        x = 1
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='rpc_exchange',
            routing_key='rpc_request.insert',
            properties=pika.BasicProperties(
                reply_to='rpc_response.insert',
                correlation_id=self.corr_id
            ),
            body=data.json()
        )

        while self.response is None and x < 1000:
            self.connection.process_data_events()
            x += 1
        return self.response
