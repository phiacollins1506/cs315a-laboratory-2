from fastapi import FastAPI, Query, Path

app = FastAPI()

tasks_db: list[str] = ["Setup environment", "Write unit tests", "Deploy application"]

@app.get("/tasks")
async def get_tasks():
    return {"tasks": tasks_db, "count": len(tasks_db)}

@app.post("/tasks")
async def create_task(
      task_name: str = Query(..., min_length=3, max_length=50)
  ):
      tasks_db.append(task_name)
      return tasks_db

@app.delete("/tasks/{task_index}")
async def delete_task(
      task_index: int = Path(..., ge=0)
  ):
      if task_index < len(tasks_db):
          task_name = tasks_db.pop(task_index)
          return {"message": "Task removed", "deleted": task_name}
      return {"error": "Index out of range"}


inventory_db: dict[int, str] = {
      501: "Mechanical Keyboard",
      502: "Ergonomic Mouse",
      503: "USB-C Hub"
  }

@app.get("/inventory")
async def get_inventory():
      return inventory_db

@app.get("/inventory/{item_id}")
async def get_inventory_item(
      item_id: int = Path(..., gt=0)
  ):
      if item_id in inventory_db:
          return {"item_id": item_id, "item_name": inventory_db[item_id]}
      return {"error": "Item not found"}

@app.post("/inventory/{item_id}")
async def create_inventory_item(
      item_id: int = Path(..., gt=0),
      item_name: str = Query(..., min_length=2, max_length=30)
  ):
      inventory_db[item_id] = item_name
      return {"message": "Item added successfully", "inventory": inventory_db}

@app.delete("/inventory/{item_id}")
async def delete_inventory_item(
      item_id: int = Path(..., gt=0)
  ):
      if item_id in inventory_db:
          del inventory_db[item_id]
          return {"message": "Item removed successfully"}
      return {"error": "Item not found"}