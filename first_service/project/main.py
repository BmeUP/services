from fastapi import FastAPI
from pydantic import BaseModel, condecimal

from queue_service.q_service import RpcClient


class Record(BaseModel):
    product_name: str
    price: condecimal(max_digits=4)


app = FastAPI()
rpc_c = RpcClient()


@app.get("/{data}")
async def root(data=0):
    response = rpc_c.call({'r_id': data})
    return {"response": f"{response}"}


@app.post("/create/")
async def create_record(record: Record):
    response = rpc_c.insert(record)
    return {"response": f"{response}"}
