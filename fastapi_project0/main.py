from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select
from fastapi_project0 import settings
from typing import Optional, Annotated
from contextlib import asynccontextmanager

class Todo (SQLModel, table=True) :
    id: Optional[int] = Field(default=None, primary_key=True)
    content:str = Field(index=True)

connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg")

engine = create_engine(connection_string, connect_args={"sslmode":"require"},
                       pool_recycle=300)

def create_db_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    create_db_tables()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Generated API with Neon DB",
    version="0.0.1",
    servers=[
        {
            "url" : "0.0.0.0:8000",
            "description": "Development Server"
        }
    ]
)

def get_session():
    with Session(engine) as session:
        yield session

# Define API endpoints/route_handlers

@app.get("/")
def read_root():
    return {"Hello" : "My first API Endpoint"}

@app.post("/todos/")
def create_todo(todo:Todo, session: Annotated[Session, Depends(get_session)]):
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo
    
@app.get("/todos/")
def read_todo(session: Annotated[Session,Depends(get_session)]):
    todos = session.exec(select(Todo)).all()
    return todos

@app.put("/todos/{todo_id}/")
def update_todo(todo_id:int, todo:Todo, session: Annotated[Session, Depends(get_session)]):
    db_todo = session.get(Todo, todo_id)
    if db_todo:
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return db_todo
    else:
        raise HTTPException(status_code=404, detail="Todo not found")
    
@app.delete("/todos/{todo_id}/")
def delete_todo(todo_id:int, todo:Todo, session: Annotated[Session, Depends(get_session)]):
    db_todo = session.get(todo_id, todo)
    if db_todo:
        session.delete(todo)
        session.commit()
        return db_todo
    else:
        raise HTTPException(status_code=404, detail="Todo not Found")
    