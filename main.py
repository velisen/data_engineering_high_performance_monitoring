from importlib.metadata import metadata
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
import logging

KAFKA_BROKERS = "localhost:29092,localhost:39092,localhost:49092"
NUM_PARTITIONS = 5
REPLICATION_FACTOR = 3
TOPIC_NAME = "FINANCIAL_TRANSACTIONS"
topic_name = 'financial_transactions'
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

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
        transaction_time = int(time.time())
    )
            
if __name__ == "__main__":
    create_topic(TOPIC_NAME)

    while True:
        transaction = generate_transaction()