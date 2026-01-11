# Hello World • main.py
from pydantic import BaseModel
from fastapi import FastAPI
app = FastAPI(title="Todo List API")

class TodoItem(BaseModel):
    id: int
    task: str
    time_estimate: int = None  # in minutes

class TodoItemResponse(BaseModel):
    id: int
    task: str
    time_estimate: int = None  # in minutes
    completed: bool = False

@app.get("/todo")
def todo()-> list[TodoItemResponse]:
    my_todo_list = [
    TodoItemResponse(id=1, task="Learn FastAPI", completed=False),
    TodoItemResponse(id=2, task="Build an API", completed=False),
]
    return my_todo_list

@app.post("/todo")
def add_todo(todo: TodoItem) -> TodoItemResponse:
    todo_response = TodoItemResponse(**todo.dict(), completed=False)
    return todo_response   

@app.delete("/todo/{item_id}")
def delete_todo(item_id: int):
    """Delete a todo item by its ID."""
    return {"message": f"Todo item with id {item_id} deleted."}  

@app.put("/todo/{item_id}")
def update_todo(item_id: int, todo: TodoItem) -> TodoItemResponse:
    todo_response = TodoItemResponse(**todo.dict(), completed=False)
    return todo_response

@app.patch("/todo/{item_id}/complete")
def complete_todo(item_id: int) -> TodoItemResponse:
    """Mark a todo item as completed."""
    todo_response = TodoItemResponse(id=item_id, task="Sample Task", completed=True)
    return todo_response
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 

