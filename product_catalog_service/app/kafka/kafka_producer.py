from aiokafka import AIOKafkaProducer

async def get_kafka_producer():
    """
        Kafka Producer Function 
    """
    producer = AIOKafkaProducer(bootstrap_servers="broker:19092")
    await producer.start()
    try:
        yield producer
    finally: 
        await producer.stop() 