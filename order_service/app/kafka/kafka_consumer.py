from aiokafka import AIOKafkaConsumer
from app.schema import ProductType
from contextlib import contextmanager
from sqlmodel import Session,select
from app.db.dbconnection import engine
from app import product_pb2
from app.schema.ProductType import Product 
 
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
        
# Reteriving the product from DB.
def select_product(purchased_product,quantity):
    """
        Method to get the product from Kafka Consumer and reterive product it from the DB
    """
    with Session(engine) as session:
        statement = select(Product).where(Product.productName == purchased_product)
        results = session.exec(statement)
        for product in results:
            print("Product from db",product.inStock)
               
            if product.inStock >= quantity:
                product.inStock = product.inStock - quantity
                print("Your order has been placed...")
            else:
                print("Out of Stock")


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
            # print(f"Received message: {msg.value} on topic {msg.topic}")
        
            deserialized_product = product_pb2.Product()
            deserialized_product.ParseFromString(msg.value)
            print("** Deserialized_product **" , deserialized_product)
            
            new_product = ProductType.Product( 
                productName=deserialized_product.productName,
            ) 

            # Method to get the product from Kafka Consumer and reterive product it from the DB
            # if  deserialized_product.quantity < ProductType.Product.inStock:
            select_product(new_product.productName, deserialized_product.quantity)   
            
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()