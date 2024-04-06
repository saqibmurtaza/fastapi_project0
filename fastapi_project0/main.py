# from contextlib import asynccontextmanager
# from typing import Annotated, Optional, List
# from fastapi import Depends, FastAPI, HTTPException
# from fastapi_project0 import settings
# from sqlmodel import Field, SQLModel, Session, create_engine, select

# class Todo(SQLModel, table=True):
#     id:Optional[int] = Field(default=None, primary_key=True)
#     content: str = Field(index=True)

# connection_string = (str(settings.DATABASE_URL).replace(
#     "postgresql" , "postgresql+psycopg"))


# engine = create_engine(connection_string, connect_args={"sslmode":"require"}, 
#                        pool_recycle=300)

# def create_db_tables():
#     SQLModel.metadata.create_all(engine)
    
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("Tables are creating.....")
#     create_db_tables()
#     yield

# app = FastAPI(lifespan=lifespan, title="Generate Todo Endpoints",
#               version="0.0.1",
#               servers= [{
#                   "url" : "DATABASE_URL",
#                   "description" : "Development Server"
#               }],
#               )

# def get_session():
#     with Session(engine) as session:
#         yield session

# @app.get("/")
# def read_root():
#     return {"Hello": "My First Fastapi Endpoint"}

# @app.post("/todos/", response_model=Todo)
# def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)]):
#         session.add(todo)
#         session.commit()
#         session.refresh(todo)
#         return todo


# @app.get("/todos/", response_model=list[Todo])
# def read_todo(todo:Todo, session:Annotated[Session, Depends(get_session)]):
#     try:
#         todos = session.exec(select(Todo).all())
#         return todos
#     except Exception as e:
#         print(f"Error occurred while fetching todo list: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")

# @app.put("/todos/{todo_id}", response_model=Todo)
# def update_todo(id:str, todo:Todo, session:Annotated[Session, Depends(get_session)]):
#     db_todo = session.get(id, todo)
#     if db_todo:
#         db_todo.content = todo.content
#         session.add(db_todo)
#         session.commit()
#         session.refresh(db_todo)
#         return db_todo
#     else:
#         raise HTTPException(status_code=404, detail="Todo not found")
    
# @app.delete("/todos/{todo_id}", response_model=Todo)
# def delete_todo(id:str, todo:Todo, session:Annotated[Session, Depends(get_session)]):
#     db_todo = session.get(id, todo)
#     if db_todo:
#         session.delete(db_todo)
#         session.commit()
#         return db_todo
#     else:
#         raise HTTPException(status_code=404, detail="Todo not found")
    

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