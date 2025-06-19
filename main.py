import json
import uuid
import random
import time
from importlib.metadata import metadata
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
import logging
import threading

KAFKA_BROKERS = "localhost:29092,localhost:39092,localhost:49092"
NUM_PARTITIONS = 5
REPLICATION_FACTOR = 3
TOPIC_NAME = "FINANCIAL_TRANSACTIONS"
topic_name = 'financial_transactions'
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

producer_conf = {
    'bootstrap.servers': KAFKA_BROKERS,
    'queue.buffering.max.messages': 10000,
    'queue.buffering.max.kbytes': 512000,
    'batch.num.messages': 1000,
    'linger.ms': 10,
    'acks': 1,
    'compression.type': 'gzip'
}

producer = Producer(producer_conf)

def create_topic(topic_name):
    admin_client = AdminClient({"bootstrap.servers": KAFKA_BROKERS})
    
    try:
        topic_metadata = admin_client.list_topics(timeout=10)
        if topic_name not in topic_metadata.topics:
            topic = NewTopic(topic_name, num_partitions=NUM_PARTITIONS, replication_factor=REPLICATION_FACTOR)
            fs = admin_client.create_topics([topic])
            for topic, future in fs.items():
                try:
                    future.result()  # Check for any errors
                    logger.info(f"Topic '{topic_name}' created successfully.")
                except Exception as e:
                    logger.error(f"Failed to create topic '{topic_name}': {e}")                   
        else:
            logger.info(f"Topic '{topic_name}' already exists.")
    
    except Exception as e:
        logger.error(f"An error occurred while creating the topic: {e}")
        
        
def generate_transaction(): 
    return dict(
        transaction_id=str(uuid.uuid4()),
        user_id = f'user_{random.randint(1, 1000)}',
        amount=random.uniform(10.0, 1000.0),
        transaction_time = int(time.time()),
        merchant_id = random.choice(['merchant_a', 'merchant_b', 'merchant_c']),
        transaction_type = random.choice(['purchase', 'refund', 'transfer']),
        location = f'location_{random.randint(1, 5)}',
        payment_method = random.choice(['credit_card', 'debit_card', 'paypal', 'bank_transfer']),
        is_international = random.choice([True, False]),
        currency = random.choice(['USD', 'EUR', 'GBP', 'JPY'])
    )
    
def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Message delivery failed for record: {msg.key()}")
    else:
        logger.info(f"Message {msg.key()} delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
            
def produce_transaction(thread_id):
    while True:
        transaction = generate_transaction()
        
        try:
            producer.produce(
                topic = TOPIC_NAME,
                key=transaction['user_id'],
                value=json.dumps(transaction).encode('utf-8'),
                on_delivery=delivery_report
            )
            print(f"Thread {thread_id} produced transaction: {transaction}")
            producer.flush()
        except Exception as e:
            print(f"Failed to produce message: {e}")

def produce_data_in_parallel(num_thread):
    threads = []
    try:
        for i in range(num_thread):
            thread = threading.Thread(target=produce_transaction, args=(i, ))
            thread.daemon = True
            thread.start()
            threads.append(thread)
            
        for thread in threads:
            thread.join()
            
    except KeyboardInterrupt:
        print("Stopping due to Ctrl+C")
    
    except Exception as e:
        print(f"Error starting thread {i}: {e}")


if __name__ == "__main__":
    create_topic(TOPIC_NAME)
    produce_data_in_parallel(3)

    