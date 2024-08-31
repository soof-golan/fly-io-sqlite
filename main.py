import contextlib

from fastapi import FastAPI, Request, Depends
from aiosqlite import connect
from typing import Annotated


async def setup_db():
    db = await connect("/litefs/db")
    cursor = await db.cursor()
    await cursor.execute("CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT)")
    return db


@contextlib.asynccontextmanager
async def lifespan(_app):
    db = await setup_db()
    try:
        yield {"db": db}
    finally:
        await db.close()


async def cursor(request: Request):
    return await request.state.db.cursor()


app = FastAPI(lifespan=lifespan)


@app.get("/{request_id}")
async def read_root(cursor: Annotated[..., Depends(cursor)], request_id: str = None):
    result = await cursor.execute("SELECT value FROM cache WHERE key = ?", (request_id,))
    result = await result.fetchone()
    if result:
        return {"value": result[0]}
    return {"value": None}


@app.post("/{request_id}")
async def update_root(cursor: Annotated[..., Depends(cursor)], request_id: str, value: str):
    result = await cursor.execute("INSERT OR REPLACE INTO cache (key, value) VALUES (?, ?) RETURNING value",
                                  (request_id, value))
    result = await result.fetchone()
    if result:
        return {"value": result[0]}
    return {"value": None}
