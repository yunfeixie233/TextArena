# This implementation is strongly based on the code here: https://github.com/diplomacy/diplomacy
# good explanation of the game: https://www.youtube.com/watch?v=l53oL0ptt7k



# DEFAULT_GAME_RULES = ('SOLITAIRE', 'NO_PRESS', 'IGNORE_ERRORS', 'POWER_CHOICE')
# class OrderSettings:
#     """ Constants to define flags for attribute Power.order_is_set. """
#     #pylint:disable=too-few-public-methods
#     ORDER_NOT_SET = 0
#     ORDER_SET_EMPTY = 1
#     ORDER_SET = 2
#     ALL_SETTINGS = {ORDER_NOT_SET, ORDER_SET_EMPTY, ORDER_SET}

import random
from typing import List, Optional

from enum import Enum

class Season(Enum):
    SPRING = "Spring"
    FALL = "Fall"
    WINTER = "Winter"

class PhaseType(Enum):
    MOVEMENT = "Movement"
    RETREATS = "Retreats"
    ADJUSTMENTS = "Adjustments"

class UnitType(Enum):
    ARMY = "A"
    FLEET = "F"

class TerrainType(Enum):
    LAND = "land"
    SEA = "sea"
    COAST = "coast"

class OrderType(Enum):
    HOLD = "H"
    MOVE = "-"
    SUPPORT = "S"
    CONVOY = "C"
    RETREAT = "R"
    BUILD = "B"
    DISBAND = "D"
    WAIVE = "WAIVE"



class Region:
    """ Represents a region on the Diplomacy map """
    def __init__(self, name: str, terrain_type: TerrainType, is_supply_center: bool = False):
        self.name = name 
        self.terrain_type = terrain_type
        self.is_supply_center = is_supply_center
        self.owner = None 
        self.unit = None 
        self.disloged_unit = None 
        self.adjacent_regions = {"A": set(), "F": set()}
        self.home_for = None

    def add_adjacency(self, other_region: str, unit_types: List[str]):
        """ Add adjacency to another region for specific unit types """
        for unit_type in unit_types:
            self.adjacent_regions[unit_type].add(other_region)

    def is_adjacent(self, unit_type: UnitType, other_region: str) -> bool:
        """ Check if this region is adjacent to another for a given unit type """
        return other_region in self.adjacent_regions[unit_type.value]

    def place_unit(self, unit) -> bool:
        """ Place a unit in this region """
        if self.unit is not None:
            return False 
        self.unit = unit 
        return True 

    def remove_unit(self) -> Optional['Unit']:
        """ Remove and return the unit from this region """
        unit = self.unit 
        self.unit = None 
        return unit 

    def dislodge_unit(self) -> Optional['Unit']:
        """ Remove any disloged unit """
        unit = self.dislodged_unit
        self.dislodged_unit = None 
        return unit 

    def set_owner(self, power) -> None:
        """ Set the owner of this supply center """
        if not self.is_supply_center:
            return 
        self.owner = power

    def __str__(self) -> str:
        return self.name 



class Unit:
    """ Represents a military unit on the map """
    def __init__(self, unit_type: UnitType, power: str):
        self.type = unit_type 
        self.power = power 
        self.region = None # will be set when placed on map
        self.dislodged = False 
        self.retreat_options = [] 

    def place_in_region(self, region: Region) -> bool:
        """ Place this unit in a region """
        if region.place_unit(self):
            self.region = region 
            return True 
        return False 

    def move_to_region(self, region: Region) -> bool:
        """ Move this unit to a new region """
        if not self.region:
            return False 
        
        old_region = self.region 
        if region.place_unit(self):
            old_region.remove_unit()
            self.region = region 
            return True 
        return False 

    def dislodge(self) -> None:
        """ Mark this unit as dislodged """
        self.dislodge = True 
        if self.region:
            self.region.unit = None 

    def retreat(self, region: Region) -> bool:
        """ Retreat this unit to a new region """
        if not self.dislodged or region.name not in self.retreat_options:
            return False 

        if region.place_unit(self):
            self.dislodged = False 
            self.region = region 
            self.retreat_options = []
            return True 
        return False

    def __str__(self) -> str:
        prefix = "*" if self.dislodged else ""
        location = self.region.name if self.region else "NOWHERE"
        return f"{prefix}{self.type.value} {location}"



class Order:
    """ Represents an order in the game """
    def __init__(self, power: str, unit_type: UnitType, location: str, 
                 order_type: OrderType, target: str = None, secondary_target: str = None):
        self.power = power
        self.unit_type = unit_type 
        self.location = location 
        self.order_type = order_type 
        self.target = target 
        self.secondary_target = secondary_target
        self.result = None # For storing resolution results
        self.strength = 1 # Base strength of the order 

    def __str__(self) -> str:
        if self.order_type == OrderType.HOLD:
            return f"{self.unit_type.value} {self.location} {self.order_type.value}"
        elif self.order_type == OrderType.MOVE:
            return f"{self.unit_type.value} {self.location} {self.order_type.value} {self.target}"
        elif self.order_type == OrderType.SUPPORT:
            if self.secondary_target:
                # Support move
                return f"{self.unit_type.value} {self.location} {self.order_type.value} {self.target} {OrderType.MOVE.value} {self.secondary_target}"
            else:
                # Support hold
                return f"{self.unit_type.value} {self.location} {self.order_type.value} {self.target}"
        elif self.order_type == OrderType.CONVOY:
            return f"{self.unit_type.value} {self.location} {self.order_type.value} {self.target} {OrderType.MOVE.value} {self.secondary_target}"
        elif self.order_type == OrderType.RETREAT:
            return f"{self.unit_type.value} {self.location} R {self.target}"
        elif self.order_type == OrderType.BUILD:
            return f"{self.unit_type.value} {self.location} B"
        elif self.order_type == OrderType.DISBAND:
            return f"{self.unit_type.value} {self.location} D"
        elif self.order_type == OrderType.WAIVE:
            return "WAIVE"
        return "Invalid Order"

    @classmethod
    def parse(cls, order_str: str, power: str) -> 'Order':
        """Parse an order string into an Order object"""
        if order_str.strip().upper() == "WAIVE":
            return cls(power, None, None, OrderType.WAIVE)
            
        parts = order_str.strip().split()
        if len(parts) < 3:
            raise ValueError(f"Invalid order format: {order_str}")
            
        unit_type = UnitType.ARMY if parts[0] == 'A' else UnitType.FLEET
        location = parts[1]
        
        if parts[2] == 'H':
            return cls(power, unit_type, location, OrderType.HOLD)
        elif parts[2] == '-':
            if len(parts) < 4:
                raise ValueError(f"Move order missing destination: {order_str}")
            return cls(power, unit_type, location, OrderType.MOVE, parts[3])
        elif parts[2] == 'S':
            if len(parts) < 4:
                raise ValueError(f"Support order invalid: {order_str}")
            supported_unit_type = UnitType.ARMY if parts[3] == 'A' else UnitType.FLEET
            supported_location = parts[4]
            
            if len(parts) >= 7 and parts[5] == '-':
                # Support move
                return cls(power, unit_type, location, OrderType.SUPPORT, 
                          f"{supported_unit_type.value} {supported_location}", parts[6])
            else:
                # Support hold
                return cls(power, unit_type, location, OrderType.SUPPORT, 
                          f"{supported_unit_type.value} {supported_location}")
        elif parts[2] == 'C':
            if len(parts) < 7 or parts[5] != '-':
                raise ValueError(f"Convoy order invalid: {order_str}")
            convoyed_unit_type = UnitType.ARMY if parts[3] == 'A' else UnitType.FLEET
            convoyed_location = parts[4]
            return cls(power, unit_type, location, OrderType.CONVOY, 
                      f"{convoyed_unit_type.value} {convoyed_location}", parts[6])
        elif parts[2] == 'R':
            if len(parts) < 4:
                raise ValueError(f"Retreat order missing destination: {order_str}")
            return cls(power, unit_type, location, OrderType.RETREAT, parts[3])
        elif parts[2] == 'B':
            return cls(power, unit_type, location, OrderType.BUILD)
        elif parts[2] == 'D':
            return cls(power, unit_type, location, OrderType.DISBAND)
            
        raise ValueError(f"Unknown order type: {order_str}")



class Power:
    """ Represents a power in the game """
    def __init__(self, name: str):
        self.name = name 
        self.units = [] 
        self.orders = []
        self.home_centers = [] # List of home supply center names
        self.controlled_centers = [] # List of currently controlled supply centers
        self.is_waiting = True 
        self.is_defeated = False 

    def add_unit(self, unit: Unit) -> None:
        """ Add a unit to this power """
        unit.power = self.name 
        self.units.append(unit)

    def remove_unit(self, unit: Unit) -> None:
        """ Remove a unit from this power """
        if unit in self.units:
            self.units.remove(unit)

    def add_center(self, center: str) -> None:
        """ Add a supply center to this power """
        if center not in self.controlled_centers:
            self.controlled_centers.append(center)
    
    def remove_center(self, center: str) -> None:
        """ Remove a supply center from this power """
        if center in self.controlled_centers:
            self.controlled_centers.remove(center)

    def clear_orders(self) -> None:
        """ Clear all orders """
        self.orders = [] 

    def set_orders(self, orders: List[Order]) -> None:
        """ Set orders for this power """
        self.orders = orders 
        self.is_waiting = False 

    def check_elimination(self) -> bool:
        """ Check if this power is eliminated """
        if not self.units and not self.controlled_centers:
            self.is_defeated = True 
        return self.is_defeated

    def get_buildable_locations(self, game_map: 'Map') -> List[str]:
        """ Get locations where this power can build new units """
        buildable = []
        for center_name in self.home_centers:
            if (center_name in self.controlled_centers and 
                game_map.regions[center_name].unit is None and 
                game_map.regions[center_name].dislodged_unit is None):
                buildable.append(center_name)
        return buildable

    def count_needed_builds(self) -> int:
        """ Calculate needed builds (positive) or needed disbands (negative) """
        return len(self.controlled_centers) - len(self.units)


class Map:
    """ Represents the Diplomacy map """
    def __init__(self):
        self.regions = {} # Dict mapping region names to Region objects

    def add_region(self, name: str, terrain_type: TerrainType, is_supply_center: bool = False, home_for: str = None) -> None:
        """ Add a region to the map """
        region = Region(name, terrain_type, is_supply_center)
        region.home_for = home_for 
        self.regions[name] = region 

    def add_adjacency(self, region1: str, region2: str, unit_types: List[str]) -> None:
        """ Add bidirectional adjacency between regions """
        if region1 in self.regions and region2 in self.regions:
            self.regions[region1].add_adjacency(region2, unit_types)
            self.regions[region2].add_adjacency(region1, unit_types)

    def get_region(self, name: str) -> Optional[Region]:
        """ Get a region by name """
        return self.regions.get(name)

    def get_all_regions(self) -> List[Region]:
        """ Get all regions on the map """
        return list(self.regions.values())

    def get_supply_centers(self) -> List[str]:
        """ Get all dupply center names """
        return [name for name, region in self.regions.items() if region.is_supply_center]

    def get_home_centers(self, power: str) -> List[str]:
        """ Get home supply centers for a power """
        return [name for name, region in self.regions.items()
                    if region.is_supply_center and region.home_for == power]

    @classmethod
    def create_standard_map(cls) -> 'Map':
        """ Create the standard Diplomacy map """
        game_map = cls()

        # Define regions  (TODO double-check and extend)
        regions_data = [
            # Format: (name, terrain_type, is_supply_center, home_power)
            ('BRE', TerrainType.COAST, True, 'FRANCE'),
            ('PAR', TerrainType.LAND, True, 'FRANCE'),
            ('MAR', TerrainType.COAST, True, 'FRANCE'),
            ('LON', TerrainType.COAST, True, 'ENGLAND'),
            ('EDI', TerrainType.COAST, True, 'ENGLAND'),
            ('LVP', TerrainType.COAST, True, 'ENGLAND'),
            ('BER', TerrainType.COAST, True, 'GERMANY'),
            ('MUN', TerrainType.LAND, True, 'GERMANY'),
            ('KIE', TerrainType.COAST, True, 'GERMANY'),
            ('VEN', TerrainType.COAST, True, 'ITALY'),
            ('ROM', TerrainType.COAST, True, 'ITALY'),
            ('NAP', TerrainType.COAST, True, 'ITALY'),
            ('VIE', TerrainType.LAND, True, 'AUSTRIA'),
            ('TRI', TerrainType.COAST, True, 'AUSTRIA'),
            ('BUD', TerrainType.LAND, True, 'AUSTRIA'),
            ('CON', TerrainType.COAST, True, 'TURKEY'),
            ('ANK', TerrainType.COAST, True, 'TURKEY'),
            ('SMY', TerrainType.COAST, True, 'TURKEY'),
            ('WAR', TerrainType.LAND, True, 'RUSSIA'),
            ('MOS', TerrainType.LAND, True, 'RUSSIA'),
            ('SEV', TerrainType.COAST, True, 'RUSSIA'),
            ('STP', TerrainType.COAST, True, 'RUSSIA'),
            # Non-supply centers
            ('PIC', TerrainType.COAST, False, None),
            ('BUR', TerrainType.LAND, False, None),
            ('GAS', TerrainType.COAST, False, None),
            ('YOR', TerrainType.COAST, False, None),
            ('WAL', TerrainType.COAST, False, None),
            ('CLY', TerrainType.COAST, False, None),
            ('RUH', TerrainType.LAND, False, None),
            ('PIE', TerrainType.COAST, False, None),
            ('TUS', TerrainType.COAST, False, None),
            ('APU', TerrainType.COAST, False, None),
            ('TYR', TerrainType.LAND, False, None),
            ('BOH', TerrainType.LAND, False, None),
            ('GAL', TerrainType.LAND, False, None),
            ('UKR', TerrainType.LAND, False, None),
            ('ARM', TerrainType.LAND, False, None),
            ('SYR', TerrainType.COAST, False, None),
            # Seas
            ('MAO', TerrainType.SEA, False, None),
            ('NAO', TerrainType.SEA, False, None),
            ('IRI', TerrainType.SEA, False, None),
            ('ENG', TerrainType.SEA, False, None),
            ('NTH', TerrainType.SEA, False, None),
            ('SKA', TerrainType.SEA, False, None),
            ('HEL', TerrainType.SEA, False, None),
            ('BAL', TerrainType.SEA, False, None),
            ('BOT', TerrainType.SEA, False, None),
            ('BAR', TerrainType.SEA, False, None),
            ('NWG', TerrainType.SEA, False, None),
            ('WES', TerrainType.SEA, False, None),
            ('LYO', TerrainType.SEA, False, None),
            ('TYS', TerrainType.SEA, False, None),
            ('ADR', TerrainType.SEA, False, None),
            ('ION', TerrainType.SEA, False, None),
            ('AEG', TerrainType.SEA, False, None),
            ('EAS', TerrainType.SEA, False, None),
            ('BLA', TerrainType.SEA, False, None),
        ]

        # Add regions to the map 
        for name, terrain, is_sc, home_for in regions_data:
            game_map.add_region(name, terrain, is_sc, home_for)

        # Add adjacencies (TODO incomplete, add the rest as well)
        adjacencies = [
            # Format: (region1, region2, [unit_types])
            ('BRE', 'ENG', ['F']),
            ('BRE', 'MAO', ['F']),
            ('BRE', 'PAR', ['A']),
            ('BRE', 'PIC', ['A', 'F']),
            ('BRE', 'GAS', ['A']),
            ('PAR', 'BRE', ['A']),
            ('PAR', 'PIC', ['A']),
            ('PAR', 'BUR', ['A']),
            ('PAR', 'GAS', ['A']),
            ('MAR', 'BUR', ['A']),
            ('MAR', 'GAS', ['A']),
            ('MAR', 'SPA', ['A', 'F']),
            ('MAR', 'PIE', ['A']),
            ('MAR', 'LYO', ['F']),
            # ...
        ]
        for r1, r2, types in adjacencies:
            game_map.add_adjacency(r1, r2, types)

        return game_map

    def visualize(self) -> str:
        """
        Return a text-based (ASCII-style) visualization of the map's current state.
        
        Each region is printed with:
        - Name and Terrain
        - Whether it's a supply center (and if so, its owner)
        - Any unit present (A or F + power name, '*' if dislodged)
        - Adjacencies for Army and Fleet
        """
        # Sort regions by name so the order is consistent
        region_names = sorted(self.regions.keys())
        
        lines = []
        title_line = "DIPLOMACY MAP OVERVIEW"
        lines.append(title_line)
        lines.append("=" * len(title_line))
        for name in region_names:
            region = self.regions[name]
            # Basic region info
            line_header = f"{name} ({region.terrain_type.value})"
            if region.is_supply_center:
                line_header += " [SC]"
            lines.append(line_header)

            # Supply center owner (if any)
            if region.is_supply_center:
                owner_str = region.owner if region.owner else "None"
                lines.append(f"  Owner: {owner_str}")

            # Any unit present in this region
            if region.unit:
                # __str__ of Unit already prints something like: "A PAR" or "*A PAR" if dislodged
                lines.append(f"  Unit:  {region.unit}")
            else:
                lines.append("  Unit:  None")
            
            # Army adjacencies
            adj_army = sorted(region.adjacent_regions["A"]) if "A" in region.adjacent_regions else []
            lines.append(f"  Adj(A): {', '.join(adj_army) if adj_army else '(none)'}")

            # Fleet adjacencies
            adj_fleet = sorted(region.adjacent_regions["F"]) if "F" in region.adjacent_regions else []
            lines.append(f"  Adj(F): {', '.join(adj_fleet) if adj_fleet else '(none)'}")

            lines.append("")  # blank line for spacing

        return "\n".join(lines)
        
if __name__ == "__main__":
    m = Map.create_standard_map()
    print(m.visualize())


class DiplomacyGameEngine:
    """ The core game engine for Diplomacy """
    
    def __init__(self, rules=None):
        self.map = Map.create_standard_map()
        self.powers = {} # Dict mapping power names to Power objects
        self.year = 1901
        self.season = Season.SPRING
        self.phase = PhaseType.MOVEMENT 
        # TODO check if it is better to track here or in the main env class
        # self.turn_number = 1 
        # self.max_turns = 100
        self.game_over = False 
        self.rules = rules or [] 
        

        # Initialize powers
        self._initialize_powers()

    def _initialize_powers(self):
        """ Initialize powers with starting units and centers """
        # Define standard powers
        standard_powers = {
            'FRANCE': [
                (UnitType.ARMY, 'PAR'),
                (UnitType.ARMY, 'MAR'),
                (UnitType.FLEET, 'BRE')
            ],
            'ENGLAND': [
                (UnitType.FLEET, 'LON'),
                (UnitType.FLEET, 'EDI'),
                (UnitType.ARMY, 'LVP')
            ],
            'GERMANY': [
                (UnitType.ARMY, 'BER'),
                (UnitType.ARMY, 'MUN'),
                (UnitType.FLEET, 'KIE')
            ],
            'ITALY': [
                (UnitType.ARMY, 'ROM'),
                (UnitType.ARMY, 'VEN'),
                (UnitType.FLEET, 'NAP')
            ],
            'AUSTRIA': [
                (UnitType.ARMY, 'VIE'),
                (UnitType.ARMY, 'BUD'),
                (UnitType.FLEET, 'TRI')
            ],
            'RUSSIA': [
                (UnitType.ARMY, 'MOS'),
                (UnitType.ARMY, 'WAR'),
                (UnitType.FLEET, 'SEV'),
                (UnitType.FLEET, 'STP')
            ],
            'TURKEY': [
                (UnitType.ARMY, 'CON'),
                (UnitType.ARMY, 'SMY'),
                (UnitType.FLEET, 'ANK')
            ]
        }

        # Create powers with their units
        for power_name, starting_units in standard_powers.items():
            power = Power(power_name)
            self.powers[power_name] = power 

            # Set home centers
            power.home_centers = self.map.get_home_centers(power_name)

            # Add initial units
            for unit_type, location in starting_units:
                unit = Unit(unit_type, power_name)
                region = self.map.get_region(location)
                if region and unit.place_in_region(region):
                    power.add_unit(unit)

            # Set initial controlled centers
            for center in power.home_centers:
                power.add_center(center)
                region = self.map.get_region(center)
                if region:
                    region.set_owner(power_name)

    def setup_game(self, num_players):
        """ Set up the game with the specified number of players """
        # assert correct player number once more
        if num_players < 3 or num_players > 7:
            raise ValueError(f"Number of players must be between 3 and 7, got {num_players}")
            

        # Select powers for the game 
        all_powers = list(self.powers.keys())
        active_powers = random.sample(all_powers, num_players)

        # Remove unused powers
        for power_name in all_powers:
            if power_name not in active_powers:
                self.powers.pop(power_name)

        return {i: power for i, power in enumerate(active_powers)}

    def get_state(self):
        """ Get the current game state """
        units = {}
        centers = {}

        for power_name, power in self.powers.items():
            units[power_name] = [str(unit) for unit in power.units]
            centers[power_name] = power.controlled_centers.copy()

        return {
            'year': self.year,
            'season': self.season.value,
            'phase': self.phase.value,
            # 'turn': self.turn_number,
            'units': units,
            'centers': centers,
            'game_over': self.game_over,
        } 

    def get_orderable_locations(self, power_name):
        """ Get locations where orders can be issued for a power """
        if power_name not in self.powers:
            return []

        power = self.powers[power_name]
        ordereable_locations = []

        if self.phase == PhaseType.MOVEMENT:
            # IN movement phase, all units can be ordered
            for unit in power.units:
                if not unit.dislodged:
                    orderable_locations.append(unit.region.name)

        elif self.phase == PhaseType.RETREATS:
            # In retreat phase, only dislodged units can be ordered
            for unit in power.units:
                orderable_locations.append(unit.region.name)

        elif self.phase == PhaseType.ADJUSTMENTS:
            # Calculate build/disband count 
            build_count = power.count_needed_builds()

            if build_count > 0:
                # Can build in unoccupied home centers
                orderable_locations = power.get_buildable_locations(self.map)
            elif build_count < 0:
                # Must move units
                for unit in power.units:
                    if not unit.dislodged:
                        orderable_locations.append(unit.region.name)
        
        return orderable_locations


    def validate_order(self, order: Order) -> bool:
        """ Validate if an order is legal """
        if order.order_type == OrderType.WAIVE:
            # WAIVE is only valid in adjustment phase when building 
            return (self.phase == PhaseType.ADJUSTMENTS and self.powers[order.power].count_needed_builds() > 0)

        # Get the unit that would execute this order
        unit = self._find_unit(order.power, order.unit_type, order.location)
        if not unit:
            return False 

        # Validate based on order type 
        elif order.order_type == OrderType.HOLD:
            # Hold is always valid for a unit
            return True 

        elif order.order_type == OrderType.MOVE:
            # Check if destination exists
            dest_region = self.map.get_region(order.target)
            if not dest_region:
                return False 

            # Check if the move id adjacent (or can be conveyed for armies)
            if unit.region.is_adjacent(unit.type, order.target):
                return True 

            # Check if army can be convoyed
            if unit.type == UnitType.ARMY and self._has_possible_convoy_path(unit.region.name, order.target):
                return True 

            return False 

        elif order.order_type == OrderType.SUPPORT:
            # Check if the supported unit exists
            supported_type = UnitType.ARMY if order.target.startswith("A ") else UnitType.FLEET
            supported_loc = order.target.split()[1]
            supported_unit = self._find_unit(None, supported_type, supported_loc)

            if not supported_unit:
                return False 

            # Check if the supported location is adjacent
            if not unit.region.is_adjacent(unit.type, supported_loc):
                return False 

            if order.secondary_target:
                # Support move - check if the destination is adjacent to the support unit
                if not supported_unit.region.is_adjacent(supported_unit.type, order.secondary_target):
                    # Check if it could be a convoyed move
                    if (supported_unit.type == UnitType.ARMY and self._has_possible_convoy_path(supported_loc, order.secondary_target)):
                        return True
                    return False 

                # Check if the destination is adjacent to the supporting unit
                if not unit.region.is_adjacent(unit.type, order.secondary_target):
                    return False 

            return True

        elif order.order_type == OrderType.CONVOY:
            # Only fleets in water regions can convoy
            if unit.type != UnitType.FLEET or unit.region.terrain_type != TerrainType.SEA:
                return False 

            # Check if the convoyed unit exists and is an army
            convoyed_type = UnitType.ARMY if order.target.startswith("A ") else UnitType.FLEET
            convoyed_loc = order.target.split()[1]
            convoyed_unit = self._find_unit(None, convoyed_type, convoyed_loc)

            if not convoyed_Unit or convoyed_unit.type != UnitType.ARMY:
                return False 

            # Check if the convoyed unit is adacent to this fleet
            if not unit.region.is_adjacent(unit.type, convoyed_loc):
                return False 

            # Check if the destination is a coastal region
            dest_region = self.map.get_region(order.secondary_target)
            if not dest_region or dest_region.terrain_type != TerrainType.COAST:
                return False 
            
            return True 

        elif order.order_type == OrderType.RETREAT:
            # Unit must be dislodged
            if not unit.dislodged:
                return False 

            # Check if retreat location is valid
            if order.target not in unit.retreat_options:
                return False 
            
            return True 

        elif order.order_type == OrderType.BUILD:
            # Must be adjustment phase 
            if self.phase != PhaseType.ADJUSTMENTS:
                return False 

            power = self.powers[order.power]

            # Must have builds available
            if power.count_needed_builds() <= 0:
                return False 

            # Location must be buildable home center
            buildable_locs = power.get_buildable_locations(self.map)
            if order.location not in buildable_locs:
                return False 

            # Unit type must be valid for the terrain
            region = self.map.get_region(order.location)
            if order.unit_type == UnitType.FLEET and region.terrain_type != TerrainType.COAST:
                return False 

        elif order.order_type == OrderType.DISBAND:
            # Must be adjustment phase OR retreat phase 
            if self.phase not in [PhaseType.ADJUSTMENTS, PhaseType.RETREATS]:
                return False 

            power = self.powers[order.power]

            if self.phase == PhaseType.ADJUSTMENTS:
                # Must need to remove units
                if power.count_needed_builds() >= 0:
                    return False 
            else: # RETREATS phase
                # Unit must be dislodged
                if not unit.dislodged:
                    return False 
            
            return True 

        return False 

    def _find_unit(self, power_name, unit_type, unit_location, location):
        """ Find a unit by type and location, optionally filtering by power """
        region = self.map.get_region(location)
        if not region:
            return None

        unit = region.unit 
        if not unit:
            # Check if there's a dislodged unit
            unit = region.dislodged_unit

        if not unit:
            return None 
        
        if unit.type != unit_type:
            return None

        if power_name and unit.power != power_name:
            return None 
        
        return unit

    def _has_possible_convoy_path(self, start, end):
        """ Check if there's a possible convoy path between locations """
        # Simple BFS to find a path of fleets
        visited = set()
        queue = [(start, [])] # (location, path_so_far)

        while queue:
            current, path = queue.pop(0)

            if current == end:
                return True 

            if current in visited:
                continue 

            visited.add(current)
            current_region = self.map.get_region(current)


            # For each adjacent sea region with a fleet 
            for adj in current_region.adjacent_regions["F"]:
                adj_region = self.map.get_region(adj)
                if adj_region and adj_region.terrain_type == TerrainType.SEA:
                    # Check if there's a fleet here 
                    if adj_region.unit and adj_region.unit.type == UnitType.FLEET:
                        queue.append((ajd, path + [adj]))
        
        return False 

    # TODO maybe keep track of completed and failed orders to add as observations?
    def resolve_orders(self, orders_by_power):
        """ Process and resolve orders for all powers """
        # Reset waiting status
        for power in self.powers.values():
            power.is_waiting = True


        # Process submitted orders
        valid_orders = {}
        for power_name, orders_list in orders_by_power.items():
            if power_name not in self.powers:
                continue 

            power = self.powers[power_name]
            parsed_orders = []

            for order_str in orders_list:
                try:
                    order = Order.parse(order_str, power_name)
                    if self.validate_order(order):
                        parsed_orders.append(order)
                except ValueError:
                    continue 

            power.set_orders(parsed_orders)
            valid_orders[power_name] = parsed_orders 

        # Check if all powers have submitted orders
        # all_submitted = True
        # for power in self.powers.values():
        #     if not power.is_defeated and power.is_waiting:
        #         all_submitted = False
        #         break
        # TODO - not necessary 

        # if all_submitted:
        if self.phase == PhaseType.MOVEMENT:
            self._resolve_movement(valid_orders)
        elif self.phase == PhaseType.RETREATS:
            self._resolve_retreats(valid_orders)
        elif self.phase == PhaseType.ADJUSTMENTS:
            self._resolve_adjustments(valid_orders)

        # Advance phase 
        self._advance_phase()

        # Check for game end conditinos
        self._check_victory()

        return True, self.get_state()


    def _resolve_movement(self, valid_orders):
        """ Resolve the movement orders """
        # Maps a region to all orders targeting it
        # Maps a region to all orders targeting it
        attack_strength = {}  # {region_name: {strength: [(unit, [supporting_units])]}}
        move_targets = {}     # {region_name: [units moving there]}
        supports = {}         # {unit: [units supporting it]}
        convoys = {}          # {(start, end): [convoying fleets]}
        move_orders = {}      # {unit: target_region}
        support_orders = {}   # {unit: (target_unit, destination)}
        convoy_orders = {}    # {unit: (convoyed_unit, destination)}

        # Step 1: Identify all moves, supports, and convoys
        for power_name, orders in valid_orders.items():
            for order in orders:
                unit = self._find_unit(power_name, order.unit_type, order.location)
                if not unit:
                    continue

                if order.order_type == OrderType.MOVE:
                    move_orders[unit] = order.target 
                    move_targets.setdefault(order.target, []).append(unit)

                elif order.order_type == OrderType.SUPPORT:
                    supported_type = UnitType.ARMY if order.target.startswith("A ") else UnitType.FLEET
                    supported_loc = order.target.split()[1]
                    supported_unit = self._find_unit(None, supported_type, supported_loc)

                    if supported_unit:
                        if order.secondary_target: # Support move
                            suport_orders[unit] = (supported_unit, order.secondary_target)
                            supports.setdefaults(supported_unit, []).append(unit)
                        else: # Support hold
                            support_orders[unit] = (supported_unit, None)
                            supports.setdefaults(supported_unit, []).append(unit)

                elif order.order_type == OrderType.CONVOY:
                    convoyed_type = UnitType.ARMY if order.target.startswith("A ") else UnitType.FLEET
                    convoyed_loc = order.target.split()[1]
                    convoyed_unit = self._find_unit(None, convoyed_type, convoyed_loc)

                    if convoyed_unit and convoyed_unit.type == UnitType.ARMY:
                        convoy_key = (convoy_loc, order.secondary_target)
                        convoys.set_default(convoy_key, []).append(unit)
                        conovy_orders[unit] = (convoy_unit, order.secondary_target)

        # Setp 2: Calculate attack strengths for all potential conflicts
        for target, attacking_units in move_targets.items():
            attack_strength[target] = {}

            # Add defending unit's strength
            defending_region = self.map.get_region(target)
            if defending_region and defending_region.unit:
                defending_unit = defending_region.unit 
                # If defender is not moving 
                if defending_unit not in move_orders:
                    defender_supports = supports.get(defending_unit, [])
                    strength = 1 + len(defender_supports)
                    attack_strength[target][strength] = [(defending_unit, defender_supports)]
            
            # Add each attacket's strength
            for attacker in attacking_units:
                attacker_supports = supports.get(attacker, [])
                # Filter out invalid supports
                valid_supports = []
                for support in attacker_supports:
                    # Support is valid if:
                    # 1. The supporting unit isn't dislodged
                    # 2. The supporting unit isn't being attacked from the unit it's supporting against
                    if not support.dislodged and self._is_valid_support(support, attacker, target):
                        valid_supports.append(support)

                strength = 1 + len(valid_supports)
                attack_strength[target].setdefault(strength, []).append((attacker, valid_supports))

        
        # Step 3: Resolve convoy disruptions
        disrupted_convoys = self._resolve_convoy_disruptions(convoys, attack_strength, move_orders)

        # Step 4: Resolve movements 
        self._resolve_movements(attack_strength, move_orders, disrupted_convoys)

        # Step 5: Update supply center ownership
        self._update_supply_centers()

        # Step 6: Prepare retreat options for dislodged units
        self._prepare_retreats()

    def _is_valid_support(self, supporting_unit, supporting_unit, target):
        """ Check if a support is valid (not cut) """
        # Check if the supporting unit is being attacked
        supporting_region = supporting_unit.region 

        for power_name, orders in valid_orders.items():
            for order in orders:
                if (order.order_type == OrderType.MOVE and 
                order.target == supporting_region.name and 
                power_name != supporting_unit.power):
                    # Support is cut unless the attack comes from the unit being supported
                    attacking_unit = self._find_unit(power_name, order.unit_type, order.location)
                    if attacking_unit and attacking != supported_unit:
                        return False 

        return True 

    def _resolve_convoy_disruptions(self, convoys, attacking_strength, move_orders):
        """ Determine which convoys are disrupted """
        disrupted_convoys = set()

        # Check each convoying fleet to see if it's dislodged
        for (start, end), fleet_list in conoys.items():
            for fleed in fleet_list:
                fleet_region = fleet.region 

                # if there's an attack on this flee'ts location
                if fleet_region.name in attack_strength:
                    strengths = sorted(attack_strength[fleet_region.name].keys(), reverse=True)
                    if not strengths:
                        continue 

                    highest_strength = strengths[0]
                    strongest_attackers = attack_strength[fleet_region.name][highest_strength]


                    # if the fleet is not among the strongest units at its location
                    fleet_strength = 1 
                    if fleet in supports:
                        fleet_strength += len(supports[fleet])

                    if fleet_strength < highest_strength:
                        # The convoy is disrupted 
                        disrupted_convoys.add((start, end))
                        break 
        return disrupted_convoys

    def _resolve_movements(self, attack_strength, move_orders, disrupted_convoys):
        """ Resolve all movements based on attack strengths """
        # Track successful moves and dislodge units
        successful_moves = {}
        dislodged_units = {}

        # Process each location with conflicts
        for location, strength_dict in attack_strength.items():
            if not strength_dict:
                continue 

            strengths = sorted(strength_dict.keys(), reverse=True)
            highest_strength = strengths[0]
            strongest_units = strength_dict[highest_strength]

            # If there's only one strongest unit or attacker
            if len(strongest_units) == 1:
                unit, supporters = strongest_units[0]
                defending_region = self.map.get_region(location)

                # If this is an attack (not a hold)
                if unit in move_orders and move_orders[unit] == location:
                    # Check if the convoy is disrupted
                    unit_start = unit.region.name 
                    if (unit_start, location) in disrupted_convoys:
                        continue 

                    # Move succeeds 
                    successful_moves[unit] = location 

                    # if there's a defender, it's dislodged
                    if defending_region and defending_region.unit:
                        defender = defending_region.unit
                        # Only if defender isn't also moving
                        if defender not in move_orders:
                            dislodge_units[defender] = unit.region.name 

            # If there are multiple strongest units, everyone bounces
            else:
                # No movement occurs
                pass 

        # Execute successful moves
        for unit, destination in successful_moves.items():
            source_region = unit.region 
            dest_region = self.map.get_region(destination)

            # Remove from source
            source_region.remove_unit()

            # Place in destination
            unit.region = dest_region 
            dest_region.unit = unit 

        # Process dislodgements
        for unit, attacker_loc in dislodge_units.items():
            unit.dislodge()
            unit.region.dislodged_unit = unit 

    def _update_supply_centers(self):
        """ Update supply center ownership after Fall movement """
        if self.season != Season.FALL:
            return 

        # Only update in Fall
        for region_name in self.map.get_supply_centers():
            region = self.map.get_region(region_name)
            occupying_unit = region.unit 

            if occupying_unit:
                old_owner = region.owner 
                new_onwer = occupying_unit.power

                # Transfer ownership if changed
                if old_owner != new_owner:
                    if old_owner:
                        self.powers[old_owner].remove_center(region_name)

                    self.powers[new_owner].add_center(region_name)
                    region.set_owner(new_owner)

    def _prepare_retreats(self):
        """ Determine valid retreat locations for all dislodged units """
        # For each dislodged unit, find valid retreat locations
        for power_name, power in self.powers.items():
            for unit in power.units:
                if unit.dislodged:
                    retreat_options = [] 

                    # Check all adjacent locations
                    for adjacent in unit.region.adjacent_regions[unit.type.value]:
                        adjacent_region = self.map.get_region(adjacent)

                        # Location must be empty and not be a bounce location
                        if (adjacent_region and 
                            not adjacent_region.unit and
                            not adjacent_region.dislodged_unit):
                            retreat_options.append(adjacent)

                    unit.retreat_options = retreat_options


