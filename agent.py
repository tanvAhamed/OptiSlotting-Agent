import re
import json
from typing import Dict, Any, List, Optional
from tools import AVAILABLE_TOOLS, execute_tool
from models import warehouse
import openai
import os
from dotenv import load_dotenv
import string

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)


class WarehouseAgent:
    def __init__(self):
        self.tools = AVAILABLE_TOOLS
        self.conversation_history = []
    
    def openai_chat(self, user_message: str) -> str:
        """Call OpenAI Chat API for a response (v1.x syntax)"""
        try:
            messages = [
                {"role": "system", "content": "You are a helpful warehouse management assistant. If the user asks about warehouse slotting, inventory, or assignments, respond with clear, concise, and actionable information. If the user asks for a specific action (like assigning an item to a slot), respond with a short confirmation and the action taken."},
                {"role": "user", "content": user_message}
            ]
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[OpenAI API error: {str(e)}]"

    def process_message(self, user_message: str) -> dict:
        """
        Use OpenAI for all chat. If the message matches a warehouse action, execute it and append the result to the OpenAI response.
        """
        user_message = user_message.strip()
        # First, try to match a warehouse action
        intent_result = self._analyze_intent(user_message.lower())
        tool_result = None
        action_response = ""
        if intent_result["action"]:
            filtered_params = {}
            if intent_result["action"] == "change_slot_assignment":
                if "slot_id" in intent_result["parameters"]:
                    filtered_params["slot_id"] = intent_result["parameters"]["slot_id"]
                if "item_id" in intent_result["parameters"]:
                    filtered_params["item_id"] = intent_result["parameters"]["item_id"]
            else:
                filtered_params = intent_result["parameters"]
            tool_result = execute_tool(intent_result["action"], **filtered_params)
            if tool_result["success"]:
                action_response = self._format_success_response(tool_result)
            else:
                # Only show the error message if the action failed
                return {
                    "response": tool_result["message"],
                    "success": False,
                    "tool_used": intent_result["action"],
                    "tool_result": tool_result
                }
        # Call OpenAI for a natural language response
        openai_response = self.openai_chat(user_message)
        # Combine OpenAI response and action result if any
        if action_response:
            if intent_result["action"] == "get_warehouse_status":
                # Use real occupancy rate for summary
                occupancy = tool_result["summary"]["overall_occupancy_rate"]
                summary = f"The warehouse currently has {occupancy:.1f}% capacity utilization."
                response = f"{summary}\n\n{action_response}"
            elif intent_result["action"] == "find_available_slots":
                response = action_response
            else:
                response = f"{openai_response}\n\n{action_response}"
        else:
            response = openai_response
        return {
            "response": response,
            "success": tool_result["success"] if tool_result else True,
            "tool_used": intent_result["action"],
            "tool_result": tool_result
        }
    
    def _analyze_intent(self, message: str) -> Dict[str, Any]:
        """
        Analyze user message to determine intent and extract parameters
        """
        message = message.lower()
        
        # Intent patterns and their corresponding actions
        patterns = [
            # Assignment patterns
            {
                "patterns": [
                    r"assign\s+(.+?)\s+to\s+slot\s+([a-z]-\d+-\d+-\d+)",
                    r"assign\s+(.+?)\s+to\s+([a-z]-\d+-\d+-\d+)",  # Without "slot"
                    r"put\s+(.+?)\s+in\s+slot\s+([a-z]-\d+-\d+-\d+)",
                    r"put\s+(.+?)\s+in\s+([a-z]-\d+-\d+-\d+)",  # Without "slot"
                    r"move\s+(.+?)\s+to\s+slot\s+([a-z]-\d+-\d+-\d+)",
                    r"move\s+(.+?)\s+to\s+([a-z]-\d+-\d+-\d+)"  # Without "slot"
                ],
                "action": "change_slot_assignment",
                "extractor": self._extract_assignment_params
            },
            # Status patterns
            {
                "patterns": [
                    r"show\s+warehouse\s+status",
                    r"warehouse\s+status",
                    r"get\s+status",
                    r"show\s+occupancy",
                    r"how\s+full\s+is\s+the\s+warehouse"
                ],
                "action": "get_warehouse_status",
                "extractor": lambda m: {}
            },
            # Find slots patterns
            {
                "patterns": [
                    r"find\s+empty\s+slots",
                    r"show\s+available\s+slots",
                    r"list\s+empty\s+slots",
                    r"find\s+slots\s+for\s+(.+)",
                    r"where\s+can\s+i\s+put\s+(.+)",
                    r"find\s+slots\s+in\s+zone\s+([abc])",
                    r"show\s+slots\s+in\s+zone\s+([abc])"
                ],
                "action": "find_available_slots",
                "extractor": self._extract_find_slots_params
            }
        ]
        
        for pattern_group in patterns:
            for pattern in pattern_group["patterns"]:
                match = re.search(pattern, message)
                if match:
                    parameters = pattern_group["extractor"](match)
                    return {
                        "action": pattern_group["action"],
                        "parameters": parameters,
                        "matched_pattern": pattern
                    }
        
        return {"action": None, "parameters": {}, "matched_pattern": None}
    
    def _extract_assignment_params(self, match) -> Dict[str, Any]:
        """Extract parameters for slot assignment"""
        item_description = match.group(1).strip()
        slot_id = match.group(2).upper()
        
        # Try to find item by name or ID
        item_id = self._find_item_by_description(item_description)
        
        return {
            "slot_id": slot_id,
            "item_id": item_id,
            "item_description": item_description
        }
    
    def _extract_find_slots_params(self, match) -> Dict[str, Any]:
        """Extract parameters for finding slots"""
        params = {}

        if match.lastindex and match.lastindex >= 1:
            text = match.group(1).strip()
            # Remove trailing punctuation
            text = text.rstrip(string.punctuation).strip()

            # Check if it's a zone specification
            if len(text) == 1 and text.upper() in ['A', 'B', 'C']:
                params["zone"] = text.upper()
            else:
                # Try to find item
                item_id = self._find_item_by_description(text)
                if item_id:
                    params["item_id"] = item_id

        return params
    
    def _find_item_by_description(self, description: str) -> Optional[str]:
        """Find item ID by description (name or ID), with hardcoded mapping for monitor and laptop."""
        description = description.lower().strip()

        # Hardcoded mapping for common electronics
        electronics_map = {
            'monitor': 'ITEM_006',
            'laptop': 'ITEM_001',
        }
        if description in electronics_map:
            return electronics_map[description]

        # First try exact ID match
        for item_id, item in warehouse.items.items():
            if item_id.lower() == description:
                return item_id
        
        # Then try name matching
        for item_id, item in warehouse.items.items():
            if description in item.name.lower():
                return item_id
        
        # Try partial matches
        for item_id, item in warehouse.items.items():
            item_words = item.name.lower().split()
            description_words = description.split()
            if any(word in item_words for word in description_words):
                return item_id
        
        return None
    
    def _format_response(self, user_message: str, intent_result: Dict, tool_result: Dict) -> Dict[str, Any]:
        """Format the response based on tool result"""
        
        if not tool_result["success"]:
            if intent_result["action"] == "change_slot_assignment" and "item_description" in intent_result["parameters"]:
                # Special handling for item not found
                if not intent_result["parameters"]["item_id"]:
                    available_items = self._list_available_items()
                    response_text = f"I couldn't find an item matching '{intent_result['parameters']['item_description']}'. " + \
                                  f"Available items are:\n{available_items}"
                else:
                    response_text = tool_result["message"]
            else:
                response_text = tool_result["message"]
        else:
            response_text = self._format_success_response(tool_result)
        
        return {
            "response": response_text,
            "success": tool_result["success"],
            "tool_used": intent_result["action"],
            "tool_result": tool_result
        }
    
    def _format_success_response(self, tool_result: Dict) -> str:
        """Format successful tool responses in a user-friendly way"""
        
        if tool_result["action"] == "change_assignment":
            return f"✅ {tool_result['message']}"
        
        elif tool_result["action"] == "find_slots":
            if tool_result["total_slots"] == 0:
                return "❌ No available slots found matching your criteria."
            
            # Get item name if available
            item_name = ""
            if tool_result.get("filters_applied", {}).get("item_id"):
                item_id = tool_result["filters_applied"]["item_id"]
                from models import warehouse
                item = warehouse.items.get(item_id)
                if item:
                    item_name = f" for {item.name}"

            slots_text = f"Found {tool_result['total_slots']} available slots{item_name} in Zone A:\n\n"
            for slot in tool_result["slots"][:10]:  # Show first 10
                slots_text += f"📦 {slot['slot_id']} - Zone {slot['zone']}, {slot['slot_type'].replace('_', ' ').title()}\n"
            
            if tool_result["total_slots"] > 10:
                slots_text += f"\n... and {tool_result['total_slots'] - 10} more slots"
                
            return slots_text
        
        elif tool_result["action"] == "warehouse_status":
            summary = tool_result["summary"]
            response = f"📊 **Warehouse Status**\n\n"
            response += f"🏢 Total Slots: {summary['total_slots']}\n"
            response += f"📦 Occupied: {summary['occupied_slots']} ({summary['overall_occupancy_rate']:.1f}%)\n"
            response += f"🆓 Empty: {summary['empty_slots']}\n\n"
            
            response += "**Zone Breakdown:**\n"
            for zone, stats in tool_result["zone_breakdown"].items():
                response += f"Zone {zone}: {stats['occupied']}/{stats['total']} ({stats['occupancy_rate']:.1f}%)\n"
            
            if tool_result["recent_assignments"]:
                response += "\n**Recent Assignments:**\n"
                for assignment in tool_result["recent_assignments"][:5]:
                    response += f"• {assignment['item_name']} → {assignment['slot_id']}\n"
            
            return response
        
        return tool_result["message"]
    
    def _list_available_items(self) -> str:
        """List all available items"""
        items_text = ""
        for item_id, item in warehouse.items.items():
            items_text += f"• {item.name} ({item_id}) - {item.category}\n"
        return items_text
    
    def get_help(self) -> str:
        """Get help information"""
        help_text = """
🏭 **Warehouse Management Assistant**

I can help you with:

**📦 Slot Assignment:**
• "assign laptop to slot A-01-01-03" or "assign laptop to A-01-01-03"
• "put office chair in slot B-02-01-01" or "put office chair in B-02-01-01"
• "move item ITEM_001 to slot C-01-01-02" or "move item ITEM_001 to C-01-01-02"

**🔍 Find Available Slots:**
• "find empty slots"
• "show available slots in zone A"
• "find slots for laptop"
• "where can I put the printer?"

**📊 Warehouse Status:**
• "show warehouse status"
• "how full is the warehouse?"
• "get occupancy report"

**Available Items:**
""" + self._list_available_items()
        
        return help_text


# Global agent instance
agent = WarehouseAgent() 