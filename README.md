# 🏭 OptiSlotting Agent - Warehouse Inventory Management System

A FastAPI-based warehouse management agent with a modern web chat UI and natural language interface for slot assignment and inventory management.

---

## 🖥️ Frontend
- **Modern Chat UI**: Real-time chat with the agent using plain English
- **Quick Actions**: One-click buttons for common tasks (status, find slots, help)
- **Live Stats Sidebar**: See total, occupied, and empty slots, with zone/type breakdowns
- **Example Commands**: Clickable suggestions for new users
- **Red Error Bubble**: Irrelevant questions trigger a red message bubble with a clear guardrail message

**Frontend Preview:**
![image](https://github.com/user-attachments/assets/4ffca837-86cf-49b7-a555-bcf9d9021a82)


---

## ⚙️ Backend
- **FastAPI** serves both the web UI and RESTful API endpoints
- **Endpoints:**
  - `/` – Main chat interface (serves the frontend)
  - `/chat` – Processes chat messages (POST)
  - `/api/warehouse/status` – Warehouse statistics (GET)
  - `/api/warehouse/slots` – All slots info (GET)
  - `/api/warehouse/items` – All items info (GET)
  - `/api/warehouse/assign` – Assign item to slot (POST)
  - `/api/warehouse/slots/empty` – Get empty slots (GET)

---

## 🧠 Agent Tools
- **change_slot_assignment**: Assign or reassign an item to a specific slot
- **find_available_slots**: Find available slots, optionally filtered by item, zone, or slot type
- **get_warehouse_status**: Get overall warehouse status, occupancy, and statistics

---

## 🏗️ Demo Flows

**Assigning an Item**
```
User: assign laptop to slot A-01-01-05
Agent: ✅ Successfully assigned Laptop Computer (ITEM_001) to slot A-01-01-05
```

**Finding Slots**
```
User: find slots for monitor
Agent: Found 57 available slots for Monitor 27inch in Zone A: ...
```

**Guardrail Example**
```
User: write a poem about strawberries
Agent: (Red bubble) Sorry, I can only answer questions related to Slotting Inventory Management
```

**Warehouse Status**
```
User: show warehouse status
Agent: The warehouse currently has 2.8% capacity utilization. ...
```

---

## 🚀 Setup Guide

1. **Clone the repository**
   ```bash
   git clone https://github.com/tanvAhamed/OptiSlotting-Agent.git
   cd OptiSlotting-Agent
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up environment variables**
   - Create a `.env` file with your OpenAI API key:
     ```
     OPENAI_API_KEY=your-key-here
     ```
4. **Run the application**
   ```bash
   python main.py
   ```
   - The app will be available at [http://localhost:8000](http://localhost:8000)

---

## 📝 Customization & Extensibility
- Add new items in `models.py`
- Add new tools in `tools.py` and register in `AVAILABLE_TOOLS`
- Extend agent patterns in `agent.py` for new intents

---

## 🛡️ Guardrails & Safety
- The agent only answers questions related to warehouse slotting and management
- Irrelevant or unsafe questions trigger a red chat bubble with:
  > Sorry, I can only answer questions related to Slotting Inventory Management

---

## 📄 License
This project is part of the OptiSlot Agent capstone project.

## 🚀 Features

- **Natural Language Interface**: Chat with the agent using plain English
- **3 Core Tools**:
  1. **Slot Assignment**: Assign items to warehouse slots with compatibility checking
  2. **Slot Discovery**: Find available slots based on item requirements or filters
  3. **Warehouse Status**: Get comprehensive warehouse occupancy and statistics
- **Smart Slot Management**: Automatic compatibility checking (weight, dimensions, hazmat, temperature)
- **Real-time Web Interface**: Modern chat UI with live warehouse statistics
- **RESTful API**: Complete API endpoints for programmatic access
- **Guardrails & Visual Feedback**: Irrelevant or unsafe questions trigger a red chat bubble and a clear message

## 📊 Warehouse Structure

- **3 Zones**: A (Standard), B (Cold Storage), C (Hazmat/Oversized)
- **180 Total Slots**: Organized by Zone-Aisle-Level-Position (e.g., A-01-01-01)
- **4 Slot Types**: Standard, Cold Storage, Hazmat, Oversized
- **6 Sample Items**: Electronics, furniture, chemicals, food, office supplies

## 🛠️ Installation

1. **Clone/Create the project directory**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

4. **Open your browser** to `http://localhost:8000`

## 💬 Usage Examples

### Chat Commands
- `"assign laptop to slot A-01-01-05"`
- `"put office chair in slot B-02-01-01"`
- `"find empty slots in zone A"`
- `"where can I put the monitor?"`
- `"show warehouse status"`
- `"find slots for chemical solvent"`
- `"write poem on strawberry"` ⟶ _Triggers guardrail: red bubble, message: Sorry, I can only answer questions related to slotting management._

### API Endpoints
- `GET /` - Web interface
- `POST /chat` - Chat with agent
- `GET /api/warehouse/status` - Warehouse statistics
- `GET /api/warehouse/slots` - All slots info
- `GET /api/warehouse/items` - All items info
- `POST /api/warehouse/assign` - Direct slot assignment

## 🏗️ Architecture

### Core Components

1. **`models.py`** - Data models and warehouse initialization
   - Slot, Item, Assignment classes
   - Warehouse data management
   - Compatibility checking logic

2. **`tools.py`** - Agent tools implementation
   - `change_slot_assignment()` - Assign items to slots
   - `find_available_slots()` - Search for empty slots
   - `get_warehouse_status()` - Warehouse statistics

3. **`agent.py`** - Natural language processing agent
   - Intent recognition with regex patterns
   - Parameter extraction
   - Response formatting

4. **`main.py`** - FastAPI web application
   - Chat interface endpoints
   - RESTful API
   - Static file serving

5. **`templates/index.html`** - Modern web interface
   - Real-time chat
   - Warehouse statistics sidebar
   - Quick actions and examples

### Data Structure

```python
# Sample Slot
{
  "slot_id": "A-01-01-01",
  "zone": "A",
  "slot_type": "standard",
  "status": "occupied",
  "assigned_item_id": "ITEM_001",
  "max_weight": 25.0,
  "dimensions": {"length": 80, "width": 60, "height": 100}
}

# Sample Item
{
  "item_id": "ITEM_001",
  "name": "Laptop Computer",
  "category": "Electronics",
  "weight": 2.5,
  "dimensions": {"length": 35, "width": 25, "height": 3},
  "is_hazardous": False
}
```

## 🔧 Customization

### Adding New Items
```python
# In models.py, add to dummy_items list
Item(
    item_id="ITEM_007",
    name="New Product",
    category="Category",
    weight=10.0,
    dimensions={"length": 50, "width": 40, "height": 30},
    is_hazardous=False
)
```

### Adding New Tools
```python
# In tools.py
def new_tool_function(param1: str) -> Dict[str, Any]:
    # Tool implementation
    return {"success": True, "message": "Tool executed"}

# Add to AVAILABLE_TOOLS registry
AVAILABLE_TOOLS["new_tool"] = {
    "function": new_tool_function,
    "description": "Description of the tool",
    "parameters": {"param1": "Parameter description"}
}
```

### Extending Agent Patterns
```python
# In agent.py, add to patterns list
{
    "patterns": [r"new pattern regex"],
    "action": "tool_name",
    "extractor": extraction_function
}
```

## 📈 Warehouse Statistics

The system tracks:
- **Overall occupancy rate**
- **Zone-wise breakdown** (A, B, C)
- **Slot type utilization** (Standard, Cold Storage, Hazmat, Oversized)
- **Recent assignments**
- **Empty slot counts**

## 🔐 Compatibility Rules

- **Weight**: Item weight ≤ Slot max weight
- **Dimensions**: Item fits within slot dimensions
- **Hazardous**: Hazardous items only in Hazmat slots
- **Temperature**: Frozen items only in Cold Storage slots

## 🎯 Example Interactions

```
User: "assign laptop to slot A-01-01-05"
Agent: ✅ Successfully assigned Laptop Computer (ITEM_001) to slot A-01-01-05

User: "find slots for chemical solvent"  
Agent: Found 38 available slots for Chemical Solvent:
       📦 C-01-01-02 - Zone C, Hazmat
       📦 C-01-02-01 - Zone C, Hazmat
       ...

User: "show warehouse status"
Agent: 📊 Warehouse Status
       🏢 Total Slots: 180
       📦 Occupied: 6 (3.3%)
       🆓 Empty: 174
       ...
```

## 🚀 Future Enhancements

- Add item movement history tracking
- Implement advanced search filters
- Add bulk operations support
- Create mobile-responsive design
- Add user authentication
- Implement real-time notifications
- Add barcode scanning support

## 📝 License

This project is part of the OptiSlot Agent capstone project.

## 🛡️ Guardrails & Safety

- The agent only answers questions related to warehouse slotting and management.
- If a user asks an irrelevant or potentially unsafe (jailbreak) question, the agent responds with:

  > Sorry, I can only answer questions related to slotting management.

- The chat bubble for this response turns red for clear visual feedback.
- This helps prevent misuse and keeps the agent focused on its intended domain.

![image](https://github.com/user-attachments/assets/d4a3ea07-25ae-4432-b8b4-67193e199f79)

