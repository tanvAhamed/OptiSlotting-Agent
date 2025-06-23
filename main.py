import os
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict, Any
import json

from agent import agent
from models import warehouse
from tools import execute_tool

app = FastAPI(title="Warehouse Management Agent", version="1.0.0")

# Create templates directory if it doesn't exist
if not os.path.exists("templates"):
    os.makedirs("templates")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(user_message: str = Form(...)):
    """Process chat message from user"""
    try:
        if user_message.lower().strip() in ["help", "/help", "?"]:
            response = {
                "response": agent.get_help(),
                "success": True,
                "tool_used": "help",
                "tool_result": None
            }
        else:
            response = agent.process_message(user_message)
        
        return JSONResponse(content=response)
    except Exception as e:
        return JSONResponse(
            content={
                "response": f"Sorry, an error occurred: {str(e)}",
                "success": False,
                "tool_used": None,
                "tool_result": None
            },
            status_code=500
        )

@app.get("/api/warehouse/status")
async def get_warehouse_status():
    """Get warehouse status via API"""
    result = execute_tool("get_warehouse_status")
    return JSONResponse(content=result)

@app.get("/api/warehouse/slots")
async def get_slots():
    """Get all slots information"""
    slots_data = []
    for slot in warehouse.slots.values():
        slot_info = {
            "slot_id": slot.slot_id,
            "zone": slot.zone,
            "aisle": slot.aisle,
            "level": slot.level,
            "position": slot.position,
            "slot_type": slot.slot_type.value,
            "status": slot.status.value,
            "assigned_item_id": slot.assigned_item_id,
            "max_weight": slot.max_weight,
            "dimensions": slot.dimensions
        }
        
        # Add item info if assigned
        if slot.assigned_item_id and slot.assigned_item_id in warehouse.items:
            item = warehouse.items[slot.assigned_item_id]
            slot_info["assigned_item"] = {
                "item_id": item.item_id,
                "name": item.name,
                "category": item.category,
                "weight": item.weight
            }
        
        slots_data.append(slot_info)
    
    return JSONResponse(content={"slots": slots_data})

@app.get("/api/warehouse/items")
async def get_items():
    """Get all items information"""
    items_data = []
    for item in warehouse.items.values():
        # Check if item is assigned to a slot
        assigned_slot = None
        for slot in warehouse.slots.values():
            if slot.assigned_item_id == item.item_id:
                assigned_slot = slot.slot_id
                break
        
        item_info = {
            "item_id": item.item_id,
            "name": item.name,
            "category": item.category,
            "weight": item.weight,
            "dimensions": item.dimensions,
            "temperature_requirement": item.temperature_requirement,
            "is_hazardous": item.is_hazardous,
            "assigned_slot": assigned_slot
        }
        items_data.append(item_info)
    
    return JSONResponse(content={"items": items_data})

@app.post("/api/warehouse/assign")
async def assign_item_to_slot(assignment_data: Dict[str, str]):
    """Assign item to slot via API"""
    slot_id = assignment_data.get("slot_id")
    item_id = assignment_data.get("item_id")
    
    if not slot_id or not item_id:
        return JSONResponse(
            content={"success": False, "message": "Both slot_id and item_id are required"},
            status_code=400
        )
    
    result = execute_tool("change_slot_assignment", slot_id=slot_id, item_id=item_id)
    return JSONResponse(content=result)

@app.get("/api/warehouse/slots/empty")
async def get_empty_slots():
    """Get empty slots via API"""
    result = execute_tool("find_available_slots")
    return JSONResponse(content=result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 