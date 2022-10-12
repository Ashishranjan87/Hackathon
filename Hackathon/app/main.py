import os

import redis
from fastapi import FastAPI, Request, Response
from fastapi_redis_cache import FastApiRedisCache, cache
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

# engine=create_engine("mysql+pymysql://root:root@127.0.0.1:3306/H-database")
# conn = engine.connect()
LOCAL_REDIS_URL = "redis://127.0.0.1:6379"

app = FastAPI()

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

    # WILL NOT be cached
    @app.get("/data")
    def getTables(tableName):
        try:
            row = Cache.hget(tableName)
            return {tableName :row }
        except Exception as exp:
            print("Error occured while fetching table")

    @app.post("/updateTable")
