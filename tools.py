from typing import List, Dict, Any, Optional
from models import warehouse, Slot, Item
import json


def change_slot_assignment(slot_id: str, item_id: str) -> Dict[str, Any]:
    """
    Tool to change the assignment of an item to a specific slot.
    
    Args:
        slot_id: The ID of the slot to assign the item to
        item_id: The ID of the item to assign to the slot
    
    Returns:
        Dict with success status and message
    """
    try:
        # Check if slot exists
        if slot_id not in warehouse.slots:
            return {
                "success": False,
                "message": f"Slot {slot_id} not found",
                "action": "change_assignment"
            }
        
        # Check if item exists
        if item_id not in warehouse.items:
            return {
                "success": False,
                "message": f"Item {item_id} not found",
                "action": "change_assignment"
            }
        
        slot = warehouse.slots[slot_id]
        item = warehouse.items[item_id]
        
        # Check if slot is already occupied
        if slot.status.value == "occupied" and slot.assigned_item_id != item_id:
            current_item = warehouse.items.get(slot.assigned_item_id)
            current_item_name = current_item.name if current_item else "Unknown Item"
            return {
                "success": False,
                "message": f"Slot {slot_id} is already occupied by {current_item_name} ({slot.assigned_item_id})",
                "action": "change_assignment"
            }
        
        # Try to assign item to slot
        success = warehouse.assign_item_to_slot(slot_id, item_id)
        
        if success:
            return {
                "success": True,
                "message": f"Successfully assigned {item.name} ({item_id}) to slot {slot_id}",
                "action": "change_assignment",
                "slot_info": {
                    "slot_id": slot_id,
                    "zone": slot.zone,
                    "aisle": slot.aisle,
                    "level": slot.level,
                    "position": slot.position
                },
                "item_info": {
                    "item_id": item_id,
                    "name": item.name,
                    "category": item.category
                }
            }
        else:
            return {
                "success": False,
                "message": f"Cannot assign {item.name} to slot {slot_id}. Item may not be compatible with slot requirements.",
                "action": "change_assignment"
            }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error changing slot assignment: {str(e)}",
            "action": "change_assignment"
        }


def find_available_slots(item_id: Optional[str] = None, zone: Optional[str] = None, slot_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Tool to find available slots, optionally filtered by item compatibility, zone, or slot type.
    
    Args:
        item_id: Optional item ID to find compatible slots for
        zone: Optional zone filter (A, B, C)
        slot_type: Optional slot type filter (standard, cold_storage, hazmat, oversized)
    
    Returns:
        Dict with available slots information
    """
    try:
        empty_slots = warehouse.get_empty_slots()
        
        # Filter by item compatibility if item_id provided
        if item_id:
            if item_id not in warehouse.items:
                return {
                    "success": False,
                    "message": f"Item {item_id} not found",
                    "action": "find_slots"
                }
            empty_slots = warehouse.find_suitable_slots_for_item(item_id)
        
        # Filter by zone if provided
        if zone:
            empty_slots = [slot for slot in empty_slots if slot.zone.upper() == zone.upper()]
        
        # Filter by slot type if provided
        if slot_type:
            empty_slots = [slot for slot in empty_slots if slot.slot_type.value == slot_type.lower()]
        
        # Format slot information
        slot_info = []
        for slot in empty_slots[:20]:  # Limit to first 20 slots
            slot_info.append({
                "slot_id": slot.slot_id,
                "zone": slot.zone,
                "aisle": slot.aisle,
                "level": slot.level,
                "position": slot.position,
                "slot_type": slot.slot_type.value,
                "max_weight": slot.max_weight,
                "dimensions": slot.dimensions
            })
        
        item_name = ""
        if item_id and item_id in warehouse.items:
            item_name = f" for {warehouse.items[item_id].name}"
        
        return {
            "success": True,
            "message": f"Found {len(empty_slots)} available slots{item_name}",
            "action": "find_slots",
            "total_slots": len(empty_slots),
            "slots": slot_info,
            "filters_applied": {
                "item_id": item_id,
                "zone": zone,
                "slot_type": slot_type
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error finding available slots: {str(e)}",
            "action": "find_slots"
        }


def get_warehouse_status() -> Dict[str, Any]:
    """
    Tool to get overall warehouse status and occupancy information.
    
    Returns:
        Dict with warehouse status information
    """
    try:
        total_slots = len(warehouse.slots)
        occupied_slots = warehouse.get_occupied_slots()
        empty_slots = warehouse.get_empty_slots()
        
        # Count by zone
        zone_stats = {}
        for zone in ["A", "B", "C"]:
            zone_slots = [slot for slot in warehouse.slots.values() if slot.zone == zone]
            zone_occupied = [slot for slot in zone_slots if slot.status.value == "occupied"]
            zone_stats[zone] = {
                "total": len(zone_slots),
                "occupied": len(zone_occupied),
                "empty": len(zone_slots) - len(zone_occupied),
                "occupancy_rate": (len(zone_occupied) / len(zone_slots)) * 100 if zone_slots else 0
            }
        
        # Count by slot type
        type_stats = {}
        for slot_type in ["standard", "cold_storage", "hazmat", "oversized"]:
            type_slots = [slot for slot in warehouse.slots.values() if slot.slot_type.value == slot_type]
            type_occupied = [slot for slot in type_slots if slot.status.value == "occupied"]
            type_stats[slot_type] = {
                "total": len(type_slots),
                "occupied": len(type_occupied),
                "empty": len(type_slots) - len(type_occupied),
                "occupancy_rate": (len(type_occupied) / len(type_slots)) * 100 if type_slots else 0
            }
        
        # Recent assignments (occupied slots with items)
        recent_assignments = []
        for slot in occupied_slots[:10]:  # Show first 10
            if slot.assigned_item_id and slot.assigned_item_id in warehouse.items:
                item = warehouse.items[slot.assigned_item_id]
                recent_assignments.append({
                    "slot_id": slot.slot_id,
                    "item_id": item.item_id,
                    "item_name": item.name,
                    "item_category": item.category
                })
        
        return {
            "success": True,
            "message": "Warehouse status retrieved successfully",
            "action": "warehouse_status",
            "summary": {
                "total_slots": total_slots,
                "occupied_slots": len(occupied_slots),
                "empty_slots": len(empty_slots),
                "overall_occupancy_rate": (len(occupied_slots) / total_slots) * 100
            },
            "zone_breakdown": zone_stats,
            "slot_type_breakdown": type_stats,
            "recent_assignments": recent_assignments
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting warehouse status: {str(e)}",
            "action": "warehouse_status"
        }


# Tool registry for the agent
AVAILABLE_TOOLS = {
    "change_slot_assignment": {
        "function": change_slot_assignment,
        "description": "Assign or reassign an item to a specific warehouse slot",
        "parameters": {
            "slot_id": "string - The ID of the slot (e.g., A-01-01-01)",
            "item_id": "string - The ID of the item (e.g., ITEM_001)"
        }
    },
    "find_available_slots": {
        "function": find_available_slots,
        "description": "Find available warehouse slots, optionally filtered by item compatibility, zone, or slot type",
        "parameters": {
            "item_id": "string (optional) - Item ID to find compatible slots for",
            "zone": "string (optional) - Zone filter (A, B, or C)",
            "slot_type": "string (optional) - Slot type (standard, cold_storage, hazmat, oversized)"
        }
    },
    "get_warehouse_status": {
        "function": get_warehouse_status,
        "description": "Get overall warehouse status, occupancy rates, and statistics",
        "parameters": {}
    }
}


def execute_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """Execute a tool by name with given parameters"""
    if tool_name not in AVAILABLE_TOOLS:
        return {
            "success": False,
            "message": f"Tool '{tool_name}' not found",
            "action": "unknown"
        }
    
    tool_function = AVAILABLE_TOOLS[tool_name]["function"]
    return tool_function(**kwargs) 