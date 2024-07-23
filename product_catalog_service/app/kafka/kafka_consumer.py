from aiokafka import AIOKafkaConsumer
from app import ProductSchema, product_pb2
from contextlib import contextmanager
from sqlmodel import Session
from product_catalog_service.app.db.dbconnection import engine

@contextmanager
def get_session():
    session = Session(engine)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

async def consume_messages(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer( 
        topic,
        bootstrap_servers= bootstrap_servers, 
        group_id="my-group"
    )
    
    # Get cluster layout and join group `my-group`
    await consumer.start()
    try:
        # Consume messages
        async for msg in consumer:
            deserialized_product = product_pb2.Product()
            deserialized_product.ParseFromString(msg.value)
            
            new_product = ProductSchema.Product(
                productName=deserialized_product.productName,
                productPrice=deserialized_product.productPrice,
                productDesc=deserialized_product.productDesc,
                inStock=deserialized_product.inStock
            )
            
            # Add the new product to the database
            with get_session() as session:
                session.add(new_product)
                session.commit()
                session.refresh(new_product)
            
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()
# *************** Kafka Consumer Ends