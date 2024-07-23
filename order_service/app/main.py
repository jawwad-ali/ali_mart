from fastapi import FastAPI, Depends
from aiokafka import AIOKafkaProducer
from typing import Annotated
from contextlib import asynccontextmanager
import asyncio

from app.kafka.kafka_producer import get_kafka_producer
from app.schema.ProductType import Product
from app.kafka.kafka_consumer import consume_messages
from app.db import dbconnection
from app import product_pb2
 
print("HEYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    dbconnection.create_db_and_tables()
    asyncio.create_task(consume_messages('order_service', 'broker:19092')) 
    yield

app = FastAPI(
    lifespan=lifespan, title="Purchase/Order Services", 
    version="0.0.1",
)

@app.get("/") 
def root():  
    return {"messages": "Purchase/Order Services"}

@app.post("/purchase")
async def purchase(data: Product, quantity:int, producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    product_protbuf = product_pb2.Product(productName=data.productName, quantity=quantity) 
    
    # Serizalizing the Message 
    serialized_order = product_protbuf.SerializeToString()
    print(f"serialized_order {serialized_order}")
    
    await producer.send_and_wait("order_service", serialized_order) 
    return serialized_order  