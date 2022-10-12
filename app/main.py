import os
import json
import redis
from fastapi import FastAPI, Request, Response
from fastapi_redis_cache import FastApiRedisCache, cache
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
from starlette.middleware.sessions import SessionMiddleware

# engine=create_engine("mysql+pymysql://root:root@127.0.0.1:3306/H-database")
# conn = engine.connect()


LOCAL_REDIS_URL = "redis://127.0.0.1:6379"

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="SECRET_KEY")
Cache = redis.Redis.from_url(LOCAL_REDIS_URL, decode_responses=True)
@app.on_event("startup")
def startup():
    redis_cache = FastApiRedisCache()
    redis_cache.init(
        host_url=os.environ.get("REDIS_URL", LOCAL_REDIS_URL),
        prefix="myapi-cache",
        response_header="X-MyAPI-Cache",
        ignore_arg_types=[Request, Response, Session]
    )

@app.get("/data")
def getTables(tableName):
    try:
        row = Cache.get(tableName)
        row = json.loads(row)
        return {tableName :row }
    except Exception as exp:
        print("Error occured while fetching table",exp)

@app.post("/updateRecord")
async def updateData(tableName ,id: int,request: Request):
    try:
        row = Cache.get(tableName)
        row = json.loads(row)
        row[id] = await request.json()
        Cache.set(tableName,json.dumps(row))
        row = Cache.get(tableName)
        row = json.loads(row)
        return {tableName: row}
    except Exception as exp:
        print("Error while updating",tableName, exp)

@app.delete("/deleteRecord")
def deleteRecord(tableName,id: str):
    try:
        row = Cache.get(tableName)
        row = json.loads(row)
        del row[id]
        Cache.set(tableName,json.dumps(row))
        return {tableName: row}
    except Exception as exp:
        print("Error occured while deletion of data",exp)