import os
import json
import redis
import logging
import datetime
from fastapi import FastAPI, Request, Response
from fastapi_redis_cache import FastApiRedisCache, cache
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
from starlette.middleware.cors import CORSMiddleware


# engine=create_engine("mysql+pymysql://root:root@127.0.0.1:3306/H-database")
# conn = engine.connect()


LOCAL_REDIS_URL = "redis://127.0.0.1:6379"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials="*",
    allow_methods="*",
    allow_headers="*",
)
Cache = redis.Redis.from_url(LOCAL_REDIS_URL, decode_responses=True)
def history(tableName,operation:str,newData={},oldData={}):
    x = str(datetime.datetime.now())
    records = Cache.get("log-"+tableName)
    if not records:
        records = "[]"
    record = {"operation":operation,"oldData":oldData,"timestamp":x,"newData":newData}
    records = json.loads(records)
    records.append(record)
    Cache.set("log-"+tableName,json.dumps(records))


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
async def updateData(tableName ,id: str,request: Request):
    try:
        row = Cache.get(tableName)
        row = json.loads(row)
        old_row = row.get(id,{})
        operation = "update/add"
        new_row = await request.json()
        history(tableName, operation, new_row, old_row)
        row[id] = new_row
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
        operation = "delete"
        history(tableName, operation, row)
        return {tableName: row}
    except Exception as exp:
        print("Error occured while deletion of data",exp)

@app.get("/createBackup")
def createBackup(tableName):
    try:
        backup = Cache.get(tableName)
        backup = Cache.set("backup-"+tableName,backup)
        operation = "backup"
        history(tableName, operation)
        return {"status": 200}
    except Exception as exp:
        print("Error while taking backup",exp)

@app.post("/applyBackup")
def applyBackup(tableName):
    try:
        backup = Cache.get("backup-"+tableName)
        row = Cache.set(tableName,backup)
        operation = "apply Backup"
        history(tableName, operation)
        return {"status":200}
    except Exception as exp:
        print("Error while applying backup",exp)

@app.get("/log")
def getHistory(tableName):
    try:
        row = Cache.keys("log-"+tableName+"-*")
        records = []
        for key in row:
            records.append(json.loads(Cache.get(key)))
        return records
    except Exception as exp:
        print("Error occured while fetching table",exp)