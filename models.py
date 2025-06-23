from pydantic import BaseModel
from typing import Optional, List, Dict
from enum import Enum
import json


class SlotStatus(str, Enum):
    EMPTY = "empty"
    OCCUPIED = "occupied"
    RESERVED = "reserved"


class SlotType(str, Enum):
    STANDARD = "standard"
    COLD_STORAGE = "cold_storage"
    HAZMAT = "hazmat"
    OVERSIZED = "oversized"


class Item(BaseModel):
    item_id: str
    name: str
    category: str
    weight: float  # in kg
    dimensions: Dict[str, float]  # length, width, height in cm
    temperature_requirement: Optional[str] = None
    is_hazardous: bool = False


class Slot(BaseModel):
    slot_id: str
    zone: str
    aisle: str
    level: int
    position: int
    slot_type: SlotType
    max_weight: float  # in kg
    dimensions: Dict[str, float]  # length, width, height in cm
    status: SlotStatus
    assigned_item_id: Optional[str] = None


class Assignment(BaseModel):
    slot_id: str
    item_id: str
    assigned_date: str
    quantity: int = 1


class WarehouseData:
    def __init__(self):
        self.slots: Dict[str, Slot] = {}
        self.items: Dict[str, Item] = {}
        self.assignments: Dict[str, Assignment] = {}
        self._initialize_dummy_data()
    
    def _initialize_dummy_data(self):
        """Initialize warehouse with dummy data"""
        
        # Create dummy items
        dummy_items = [
            Item(
                item_id="ITEM_001",
                name="Laptop Computer",
                category="Electronics",
                weight=2.5,
                dimensions={"length": 35, "width": 25, "height": 3},
                is_hazardous=False
            ),
            Item(
                item_id="ITEM_002",
                name="Office Chair",
                category="Furniture",
                weight=15.0,
                dimensions={"length": 60, "width": 60, "height": 110},
                is_hazardous=False
            ),
            Item(
                item_id="ITEM_003",
                name="Chemical Solvent",
                category="Chemicals",
                weight=5.0,
                dimensions={"length": 20, "width": 20, "height": 30},
                is_hazardous=True
            ),
            Item(
                item_id="ITEM_004",
                name="Frozen Food Box",
                category="Food",
                weight=8.0,
                dimensions={"length": 40, "width": 30, "height": 20},
                temperature_requirement="frozen"
            ),
            Item(
                item_id="ITEM_005",
                name="Printer Paper (Box)",
                category="Office Supplies",
                weight=12.0,
                dimensions={"length": 50, "width": 35, "height": 25},
                is_hazardous=False
            ),
            Item(
                item_id="ITEM_006",
                name="Monitor 27inch",
                category="Electronics",
                weight=6.0,
                dimensions={"length": 65, "width": 45, "height": 20},
                is_hazardous=False
            )
        ]
        
        for item in dummy_items:
            self.items[item.item_id] = item
        
        # Create dummy slots
        zones = ["A", "B", "C"]
        aisles = ["01", "02", "03", "04"]
        levels = [1, 2, 3]
        positions = [1, 2, 3, 4, 5]
        
        slot_counter = 1
        for zone in zones:
            for aisle in aisles:
                for level in levels:
                    for position in positions:
                        slot_id = f"{zone}-{aisle}-{level:02d}-{position:02d}"
                        
                        # Determine slot type based on zone
                        if zone == "A":
                            slot_type = SlotType.STANDARD
                            max_weight = 25.0
                        elif zone == "B":
                            slot_type = SlotType.COLD_STORAGE
                            max_weight = 20.0
                        else:  # zone == "C"
                            slot_type = SlotType.HAZMAT if position <= 2 else SlotType.OVERSIZED
                            max_weight = 50.0 if slot_type == SlotType.OVERSIZED else 30.0
                        
                        slot = Slot(
                            slot_id=slot_id,
                            zone=zone,
                            aisle=aisle,
                            level=level,
                            position=position,
                            slot_type=slot_type,
                            max_weight=max_weight,
                            dimensions={"length": 80, "width": 60, "height": 100},
                            status=SlotStatus.EMPTY
                        )
                        
                        self.slots[slot_id] = slot
                        slot_counter += 1
        
        # Create some initial assignments
        initial_assignments = [
            ("A-01-01-01", "ITEM_001"),  # Laptop in standard slot
            ("A-01-01-02", "ITEM_002"),  # Chair in standard slot
            ("C-01-01-01", "ITEM_003"),  # Chemical in hazmat slot
            ("B-01-01-01", "ITEM_004"),  # Frozen food in cold storage
            ("A-02-01-01", "ITEM_005"),  # Paper in standard slot
            ("A-01-02-01", "ITEM_006"),  # Monitor in standard slot
        ]
        
        for slot_id, item_id in initial_assignments:
            if slot_id in self.slots and item_id in self.items:
                self.assign_item_to_slot(slot_id, item_id)
    
    def assign_item_to_slot(self, slot_id: str, item_id: str) -> bool:
        """Assign an item to a slot"""
        if slot_id not in self.slots:
            return False
        if item_id not in self.items:
            return False
        
        slot = self.slots[slot_id]
        item = self.items[item_id]
        
        # Check if slot is compatible with item
        if not self._is_compatible(slot, item):
            return False
        
        # Remove item from current slot if assigned
        current_assignment = self._find_item_assignment(item_id)
        if current_assignment:
            self.unassign_item(item_id)
        
        # Assign item to new slot
        slot.status = SlotStatus.OCCUPIED
        slot.assigned_item_id = item_id
        
        assignment = Assignment(
            slot_id=slot_id,
            item_id=item_id,
            assigned_date="2024-01-01"  # Dummy date
        )
        self.assignments[f"{slot_id}_{item_id}"] = assignment
        
        return True
    
    def unassign_item(self, item_id: str) -> bool:
        """Remove item assignment"""
        assignment = self._find_item_assignment(item_id)
        if not assignment:
            return False
        
        slot = self.slots[assignment.slot_id]
        slot.status = SlotStatus.EMPTY
        slot.assigned_item_id = None
        
        del self.assignments[f"{assignment.slot_id}_{item_id}"]
        return True
    
    def _find_item_assignment(self, item_id: str) -> Optional[Assignment]:
        """Find current assignment for an item"""
        for assignment in self.assignments.values():
            if assignment.item_id == item_id:
                return assignment
        return None
    
    def _is_compatible(self, slot: Slot, item: Item) -> bool:
        """Check if an item is compatible with a slot"""
        # Weight check
        if item.weight > slot.max_weight:
            return False
        
        # Dimension check
        if (item.dimensions["length"] > slot.dimensions["length"] or
            item.dimensions["width"] > slot.dimensions["width"] or
            item.dimensions["height"] > slot.dimensions["height"]):
            return False
        
        # Hazmat check
        if item.is_hazardous and slot.slot_type != SlotType.HAZMAT:
            return False
        
        # Temperature check
        if item.temperature_requirement == "frozen" and slot.slot_type != SlotType.COLD_STORAGE:
            return False
        
        return True
    
    def get_empty_slots(self) -> List[Slot]:
        """Get all empty slots"""
        return [slot for slot in self.slots.values() if slot.status == SlotStatus.EMPTY]
    
    def get_occupied_slots(self) -> List[Slot]:
        """Get all occupied slots"""
        return [slot for slot in self.slots.values() if slot.status == SlotStatus.OCCUPIED]
    
    def find_suitable_slots_for_item(self, item_id: str) -> List[Slot]:
        """Find all suitable empty slots for an item"""
        if item_id not in self.items:
            return []
        
        item = self.items[item_id]
        suitable_slots = []
        
        for slot in self.get_empty_slots():
            if self._is_compatible(slot, item):
                suitable_slots.append(slot)
        
        return suitable_slots


# Global warehouse instance
warehouse = WarehouseData() 