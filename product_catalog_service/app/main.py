from fastapi import FastAPI,Depends
from typing import Annotated
from sqlmodel import Session,select
from contextlib import asynccontextmanager
from aiokafka import AIOKafkaProducer

from app import ProductSchema, product_pb2
from app.kafka.kafka_producer import get_kafka_producer
from app.kafka.kafka_consumer import consume_messages
import asyncio

from product_catalog_service.app.db import dbconnection

print("HEYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    dbconnection.create_db_and_tables()
    asyncio.create_task(consume_messages('product_catalog', 'broker:19092')) 
    yield

app = FastAPI(
    lifespan=lifespan, title="Product Service", 
    version="0.0.1",
)

# Micro Service 1
# FastAPI Instance

def get_db_session():
    with Session(dbconnection.engine) as session:
        yield session
        
@app.get("/")
def root():
    return {"message":  "I am Micro Service 1" }

@app.post("/create") 
async def create(data: ProductSchema.Product, producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]): 

    """
        Adding Product to the database
    """ 

    product_protbuf = product_pb2.Product(productName=data.productName, productPrice=data.productPrice , productDesc=data.productDesc, inStock=data.inStock)
    
    print(f"Todo Prot Buff",product_protbuf)  

    # Serizalizing the Message
    serialized_product = product_protbuf.SerializeToString()
    print(f"Serialized data: {serialized_product}") 

    await producer.send_and_wait("product_catalog", serialized_product) 
    return "Successfull" 

@app.get("/products/")
def getProducts(session: Annotated[Session, Depends(get_db_session)]):
    """_summary_

    Args:
        session (Annotated[Session, Depends): Only Runs when there is healty database session

    Returns:
        _type_: Returning all the products
    """
    products = session.exec(select(ProductSchema.Product)).all()
    return products