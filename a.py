"""
Diplomacy Map Generation Algorithm using Hexagonal Grid Tiles
Each region can occupy one or more hexagons while maintaining correct borders
"""

import math
import random
from collections import defaultdict, deque
from enum import Enum

class RegionType(Enum):
    LAND = "land"
    COAST = "coast"
    SEA = "sea"

class Region:
    def __init__(self, name, region_type, is_supply_center=False, home_for=None):
        self.name = name
        self.type = region_type
        self.is_supply_center = is_supply_center
        self.home_for = home_for
        self.adjacent_regions = set()
        self.hexes = set()  # Coordinates of hexagons this region occupies
        self.size_requirement = 1  # Default size (will be adjusted based on connections)
    
    def add_adjacency(self, other_region):
        """Add adjacent region"""
        self.adjacent_regions.add(other_region)
    
    def __repr__(self):
        return f"{self.name} ({self.type.value})"

class HexCoord:
    """Cube coordinate system for hexagonal grid"""
    def __init__(self, q, r, s=None):
        self.q = q
        self.r = r
        # In cube coordinates, q + r + s = 0
        self.s = -q - r if s is None else s
        assert q + r + s == 0, "Invalid cube coordinates"
    
    def neighbors(self):
        """Get all 6 neighboring hex coordinates"""
        directions = [
            HexCoord(1, -1, 0), HexCoord(1, 0, -1), HexCoord(0, 1, -1),
            HexCoord(-1, 1, 0), HexCoord(-1, 0, 1), HexCoord(0, -1, 1)
        ]
        return [HexCoord(self.q + d.q, self.r + d.r, self.s + d.s) for d in directions]
    
    def distance(self, other):
        """Calculate distance between two hex coordinates"""
        return max(abs(self.q - other.q), abs(self.r - other.r), abs(self.s - other.s))
    
    def __eq__(self, other):
        if not isinstance(other, HexCoord):
            return False
        return self.q == other.q and self.r == other.r and self.s == other.s
    
    def __hash__(self):
        return hash((self.q, self.r, self.s))
    
    def __repr__(self):
        return f"HexCoord({self.q}, {self.r}, {self.s})"

class DiplomacyMap:
    def __init__(self):
        self.regions = {}  # name -> Region
        self.grid = {}     # HexCoord -> Region name
        self.region_sizes = {}  # name -> required size in hexes
    
    def add_region(self, name, region_type, is_supply_center=False, home_for=None):
        """Add a region to the map"""
        region = Region(name, region_type, is_supply_center, home_for)
        self.regions[name] = region
        return region
    
    def add_adjacency(self, region1_name, region2_name):
        """Add bidirectional adjacency between regions"""
        if region1_name in self.regions and region2_name in self.regions:
            self.regions[region1_name].add_adjacency(region2_name)
            self.regions[region2_name].add_adjacency(region1_name)
    
    def calculate_region_sizes(self):
        """Calculate how many hexes each region needs based on connections"""
        for name, region in self.regions.items():
            connections = len(region.adjacent_regions)
            
            # Base size calculation
            if region.type == RegionType.SEA:
                # Sea regions are most flexible and can be larger
                base_size = max(1, connections // 3)
            elif region.type == RegionType.COAST:
                # Coastal regions need moderate space
                base_size = max(1, connections // 4) 
            else:
                # Land regions are most compact
                base_size = max(1, connections // 5)
                
            # Add bonus for important regions
            if region.is_supply_center:
                base_size += 1
                
            # Special cases for multi-coast territories
            if name in ["SPA", "BUL", "STP"]:
                base_size += 1
                
            self.region_sizes[name] = base_size
            region.size_requirement = base_size
    
    def generate_map(self):
        """Generate the map layout using hexagonal grid"""
        # 1. Calculate how many hexes each region needs
        self.calculate_region_sizes()
        
        # 2. Sort regions by connectivity (most connected first)
        sorted_regions = sorted(
            self.regions.values(),
            key=lambda r: (len(r.adjacent_regions), r.is_supply_center),
            reverse=True
        )
        
        # 3. Place sea regions first (they're most flexible)
        sea_regions = [r for r in sorted_regions if r.type == RegionType.SEA]
        coastal_regions = [r for r in sorted_regions if r.type == RegionType.COAST]
        land_regions = [r for r in sorted_regions if r.type == RegionType.LAND]
        
        # Start with the most connected sea region at center
        center = HexCoord(0, 0, 0)
        self._place_region(sea_regions[0], center, growth_pattern="spiral")
        
        # 4. Place remaining sea regions
        for region in sea_regions[1:]:
            self._place_connected_region(region, growth_pattern="blob")
            
        # 5. Place coastal regions
        for region in coastal_regions:
            self._place_connected_region(region, growth_pattern="compact")
            
        # 6. Place land regions
        for region in land_regions:
            self._place_connected_region(region, growth_pattern="compact")
            
        # 7. Verify and fix adjacencies
        self._verify_and_fix_adjacencies()
        
        return self.grid
    
    def _place_region(self, region, start_hex, growth_pattern="compact"):
        """Place a region on the grid starting at given hex with specified growth pattern"""
        size_needed = region.size_requirement
        region.hexes.add(start_hex)
        self.grid[start_hex] = region.name
        
        if size_needed <= 1:
            return
        
        # Different growth patterns for different region types
        if growth_pattern == "spiral":
            # Spiral outward pattern (good for seas)
            self._grow_region_spiral(region, start_hex, size_needed - 1)
        elif growth_pattern == "blob":
            # Blob-like growth (irregular, good for seas)
            self._grow_region_blob(region, start_hex, size_needed - 1)
        else:  # "compact"
            # Compact growth (good for land)
            self._grow_region_compact(region, start_hex, size_needed - 1)
    
    def _find_best_starting_position(self, region):
        """Find best position to start placing a region based on adjacencies"""
        # For regions with adjacencies, find a position next to an already placed adjacent region
        adjacent_to_placed = [adj for adj in region.adjacent_regions if any(
            self.regions[adj].hexes
        )]
        
        if not adjacent_to_placed:
            # If no adjacencies placed yet, find a position near the center
            center = HexCoord(0, 0, 0)
            for hex_pos, region_name in self.grid.items():
                if not region_name:  # Empty hex
                    return hex_pos
            # If grid is empty, start at center
            return center
        
        # Find an empty hex adjacent to one of our adjacent regions
        for adj_name in adjacent_to_placed:
            adj_region = self.regions[adj_name]
            for adj_hex in adj_region.hexes:
                for neighbor in adj_hex.neighbors():
                    if neighbor not in self.grid:
                        return neighbor
        
        # If no direct empty neighbors, find closest empty hex
        placed_hexes = set()
        for adj_name in adjacent_to_placed:
            placed_hexes.update(self.regions[adj_name].hexes)
        
        closest_empty = None
        min_distance = float('inf')
        
        # Search in expanding rings from placed hexes
        for placed_hex in placed_hexes:
            for distance in range(1, 10):  # Limit search radius
                for candidate in self._ring_hexes(placed_hex, distance):
                    if candidate not in self.grid:
                        return candidate
        
        # If still no position found, find any empty hex
        for q in range(-20, 21):
            for r in range(-20, 21):
                s = -q - r
                hex_pos = HexCoord(q, r, s)
                if hex_pos not in self.grid:
                    return hex_pos
    
    def _ring_hexes(self, center, radius):
        """Get all hexes in a ring of given radius around center"""
        results = []
        # Start at corner and walk around the ring
        hex_pos = HexCoord(
            center.q + radius,
            center.r - radius,
            center.s
        )
        
        # 6 directions to walk
        directions = [
            HexCoord(0, 1, -1), HexCoord(-1, 1, 0),
            HexCoord(-1, 0, 1), HexCoord(0, -1, 1),
            HexCoord(1, -1, 0), HexCoord(1, 0, -1)
        ]
        
        for direction in directions:
            for _ in range(radius):
                results.append(hex_pos)
                hex_pos = HexCoord(
                    hex_pos.q + direction.q,
                    hex_pos.r + direction.r,
                    hex_pos.s + direction.s
                )
        
        return results
    
    def _place_connected_region(self, region, growth_pattern="compact"):
        """Place a region connected to its already-placed adjacencies"""
        # Find starting position based on adjacencies
        start_hex = self._find_best_starting_position(region)
        if not start_hex:
            # If no good position found, place randomly
            q = random.randint(-10, 10)
            r = random.randint(-10, 10)
            s = -q - r
            start_hex = HexCoord(q, r, s)
        
        self._place_region(region, start_hex, growth_pattern)
    
    def _grow_region_spiral(self, region, start_hex, hexes_to_add):
        """Grow region in spiral pattern from start hex"""
        current_radius = 1
        hexes_added = 0
        
        while hexes_added < hexes_to_add:
            ring_hexes = self._ring_hexes(start_hex, current_radius)
            for hex_pos in ring_hexes:
                if hex_pos not in self.grid and hexes_added < hexes_to_add:
                    region.hexes.add(hex_pos)
                    self.grid[hex_pos] = region.name
                    hexes_added += 1
            current_radius += 1
    
    def _grow_region_blob(self, region, start_hex, hexes_to_add):
        """Grow region in blob-like pattern from start hex"""
        frontier = deque([h for h in start_hex.neighbors() if h not in self.grid])
        hexes_added = 0
        
        while frontier and hexes_added < hexes_to_add:
            # Randomly pick from frontier with preference for hexes with more neighbors
            candidates = list(frontier)
            weights = []
            
            for hex_pos in candidates:
                # Count how many neighbors are already part of this region
                connected_neighbors = sum(1 for n in hex_pos.neighbors() 
                                         if n in region.hexes)
                weights.append(1 + connected_neighbors)  # Base weight + connectivity
            
            # Select weighted random hex from frontier
            if not weights:
                break
                
            # Normalize weights for selection
            total = sum(weights)
            probabilities = [w/total for w in weights]
            
            idx = random.choices(range(len(candidates)), probabilities)[0]
            chosen_hex = candidates[idx]
            
            # Add the chosen hex to the region
            if chosen_hex not in self.grid:
                region.hexes.add(chosen_hex)
                self.grid[chosen_hex] = region.name
                hexes_added += 1
                
                # Add new neighbors to frontier
                for neighbor in chosen_hex.neighbors():
                    if neighbor not in self.grid and neighbor not in frontier:
                        frontier.append(neighbor)
            
            # Remove chosen hex from frontier
            frontier.remove(chosen_hex)
    
    def _grow_region_compact(self, region, start_hex, hexes_to_add):
        """Grow region in compact pattern (prioritize filling concave areas)"""
        hexes_added = 0
        shell = set(start_hex.neighbors())
        
        while shell and hexes_added < hexes_to_add:
            # Score each candidate by how many occupied neighbors it has
            candidates = {}
            for hex_pos in shell:
                if hex_pos in self.grid:
                    continue
                    
                # Score based on number of occupied neighbors
                occupied_neighbors = sum(1 for n in hex_pos.neighbors() 
                                       if n in self.grid)
                candidates[hex_pos] = occupied_neighbors
            
            if not candidates:
                # If no candidates in shell, expand shell by one ring
                new_shell = set()
                for hex_pos in shell:
                    new_shell.update(n for n in hex_pos.neighbors() 
                                   if n not in self.grid and n not in region.hexes)
                shell = new_shell
                continue
            
            # Choose hex with highest score (most occupied neighbors)
            best_hex = max(candidates.items(), key=lambda x: x[1])[0]
            
            # Add to region
            region.hexes.add(best_hex)
            self.grid[best_hex] = region.name
            hexes_added += 1
            
            # Update shell
            shell.remove(best_hex)
            shell.update(n for n in best_hex.neighbors() 
                        if n not in self.grid and n not in region.hexes and n not in shell)
    
    def _verify_and_fix_adjacencies(self):
        """Ensure all specified adjacencies are physically represented in grid"""
        # Check each region pair that should be adjacent
        for region_name, region in self.regions.items():
            for adj_name in region.adjacent_regions:
                adj_region = self.regions[adj_name]
                
                # Check if they're physically adjacent in the grid
                is_adjacent = False
                for hex_pos in region.hexes:
                    for neighbor in hex_pos.neighbors():
                        if neighbor in self.grid and self.grid[neighbor] == adj_name:
                            is_adjacent = True
                            break
                    if is_adjacent:
                        break
                
                # If not adjacent, fix by expanding one region toward the other
                if not is_adjacent:
                    self._create_adjacency_bridge(region_name, adj_name)
    
    def _create_adjacency_bridge(self, region1_name, region2_name):
        """Create a path of hexes to connect two regions that should be adjacent"""
        region1 = self.regions[region1_name]
        region2 = self.regions[region2_name]
        
        # Find closest hexes between regions
        closest_pair = None
        min_distance = float('inf')
        
        for hex1 in region1.hexes:
            for hex2 in region2.hexes:
                dist = hex1.distance(hex2)
                if dist < min_distance:
                    min_distance = dist
                    closest_pair = (hex1, hex2)
        
        if not closest_pair:
            return
        
        # If distance is 1, they're already adjacent - no fix needed
        if min_distance <= 1:
            return
            
        # Determine which region to expand
        # Prefer expanding sea regions, then coastal, then land
        if region1.type == RegionType.SEA and region2.type != RegionType.SEA:
            expanding_region = region1
            target_hex = closest_pair[1]
        elif region2.type == RegionType.SEA and region1.type != RegionType.SEA:
            expanding_region = region2
            target_hex = closest_pair[0]
        elif region1.type == RegionType.COAST and region2.type == RegionType.LAND:
            expanding_region = region1
            target_hex = closest_pair[1]
        elif region2.type == RegionType.COAST and region1.type == RegionType.LAND:
            expanding_region = region2
            target_hex = closest_pair[0]
        else:
            # If same type, expand the one with fewer hexes
            if len(region1.hexes) <= len(region2.hexes):
                expanding_region = region1
                target_hex = closest_pair[1]
            else:
                expanding_region = region2
                target_hex = closest_pair[0]
        
        # Find path using A* to create bridge
        expanding_name = expanding_region.name
        start_hex = closest_pair[0] if expanding_region == region1 else closest_pair[1]
        
        # Create bridge using A*
        path = self._find_path(start_hex, target_hex)
        if not path:
            return
            
        # Add path hexes to expanding region (skip first hex, it's already in region)
        for hex_pos in path[1:]:
            # Stop if we've reached the target region
            if hex_pos in self.grid and self.grid[hex_pos] != expanding_name:
                break
                
            # Only add if hex is empty
            if hex_pos not in self.grid:
                expanding_region.hexes.add(hex_pos)
                self.grid[hex_pos] = expanding_name
    
    def _find_path(self, start, goal):
        """Find path between hexes using A* algorithm"""
        # Using A* to find optimal path
        open_set = {start}
        closed_set = set()
        
        # For node n, came_from[n] is the node immediately preceding it on the path
        came_from = {}
        
        # g_score[n] is the cost of the cheapest path from start to n
        g_score = defaultdict(lambda: float('inf'))
        g_score[start] = 0
        
        # f_score[n] = g_score[n] + heuristic(n)
        f_score = defaultdict(lambda: float('inf'))
        f_score[start] = start.distance(goal)
        
        while open_set:
            # Get node with lowest f_score
            current = min(open_set, key=lambda h: f_score[h])
            
            if current == goal:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path
            
            open_set.remove(current)
            closed_set.add(current)
            
            for neighbor in current.neighbors():
                if neighbor in closed_set:
                    continue
                
                # Calculate tentative g_score
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in open_set:
                    open_set.add(neighbor)
                elif tentative_g_score >= g_score[neighbor]:
                    continue
                
                # This path is better, record it
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + neighbor.distance(goal)
        
        return None  # No path found
    
    def visualize_map(self):
        """Generate ASCII visualization of the map"""
        # Find bounds
        min_q = min_r = float('inf')
        max_q = max_r = float('-inf')
        
        for hex_pos in self.grid.keys():
            min_q = min(min_q, hex_pos.q)
            max_q = max(max_q, hex_pos.q)
            min_r = min(min_r, hex_pos.r)
            max_r = max(max_r, hex_pos.r)
        
        # Add padding
        min_q -= 1
        max_q += 1
        min_r -= 1
        max_r += 1
        
        # Generate ASCII grid
        result = []
        for r in range(min_r, max_r + 1):
            # Offset each row
            offset = " " * (r - min_r)
            row = offset
            
            for q in range(min_q, max_q + 1):
                s = -q - r
                hex_pos = HexCoord(q, r, s)
                if hex_pos in self.grid:
                    region_name = self.grid[hex_pos]
                    row += region_name[:3].ljust(3) + " "
                else:
                    row += "... "
            
            result.append(row)
        
        return "\n".join(result)
    
    def get_region_adjacency_counts(self):
        """Return actual adjacency count for each region in the grid"""
        result = {}
        
        for region_name, region in self.regions.items():
            if not region.hexes:
                result[region_name] = 0
                continue
                
            adjacent_regions = set()
            for hex_pos in region.hexes:
                for neighbor in hex_pos.neighbors():
                    if (neighbor in self.grid and 
                        self.grid[neighbor] != region_name):
                        adjacent_regions.add(self.grid[neighbor])
            
            result[region_name] = len(adjacent_regions)
        
        return result

def create_diplomacy_map():
    """Create and return the Diplomacy map with all regions and adjacencies"""
    game_map = DiplomacyMap()
    
    # Define regions by type (land, coast, sea)
    # Format: (name, type, is_supply_center, home_power)
    regions_data = [
        # Sea regions
        ('ADR', RegionType.SEA, False, None),  # Adriatic Sea
        ('AEG', RegionType.SEA, False, None),  # Aegean Sea
        ('BAL', RegionType.SEA, False, None),  # Baltic Sea
        ('BAR', RegionType.SEA, False, None),  # Barents Sea
        ('BLA', RegionType.SEA, False, None),  # Black Sea
        ('BOT', RegionType.SEA, False, None),  # Gulf of Bothnia
        ('EAS', RegionType.SEA, False, None),  # Eastern Mediterranean
        ('ENG', RegionType.SEA, False, None),  # English Channel
        ('HEL', RegionType.SEA, False, None),  # Helgoland Bight
        ('ION', RegionType.SEA, False, None),  # Ionian Sea
        ('IRI', RegionType.SEA, False, None),  # Irish Sea
        ('LYO', RegionType.SEA, False, None),  # Gulf of Lyon
        ('MAO', RegionType.SEA, False, None),  # Mid-Atlantic Ocean
        ('NAO', RegionType.SEA, False, None),  # North Atlantic Ocean
        ('NTH', RegionType.SEA, False, None),  # North Sea
        ('NWG', RegionType.SEA, False, None),  # Norwegian Sea
        ('SKA', RegionType.SEA, False, None),  # Skagerrak
        ('TYS', RegionType.SEA, False, None),  # Tyrrhenian Sea
        ('WES', RegionType.SEA, False, None),  # Western Mediterranean
        
        # Coastal regions (supply centers)
        ('ANK', RegionType.COAST, True, 'TURKEY'),    # Ankara
        ('BEL', RegionType.COAST, True, None),        # Belgium
        ('BER', RegionType.COAST, True, 'GERMANY'),   # Berlin
        ('BRE', RegionType.COAST, True, 'FRANCE'),    # Brest
        ('BUL', RegionType.COAST, True, None),        # Bulgaria
        ('CON', RegionType.COAST, True, 'TURKEY'),    # Constantinople
        ('DEN', RegionType.COAST, True, None),        # Denmark
        ('EDI', RegionType.COAST, True, 'ENGLAND'),   # Edinburgh
        ('GRE', RegionType.COAST, True, None),        # Greece
        ('HOL', RegionType.COAST, True, None),        # Holland
        ('KIE', RegionType.COAST, True, 'GERMANY'),   # Kiel
        ('LON', RegionType.COAST, True, 'ENGLAND'),   # London
        ('LVP', RegionType.COAST, True, 'ENGLAND'),   # Liverpool
        ('MAR', RegionType.COAST, True, 'FRANCE'),    # Marseilles
        ('NAP', RegionType.COAST, True, 'ITALY'),     # Naples
        ('NWY', RegionType.COAST, True, None),        # Norway
        ('POR', RegionType.COAST, True, None),        # Portugal
        ('ROM', RegionType.COAST, True, 'ITALY'),     # Rome
        ('RUM', RegionType.COAST, True, None),        # Rumania
        ('SEV', RegionType.COAST, True, 'RUSSIA'),    # Sevastopol
        ('SMY', RegionType.COAST, True, 'TURKEY'),    # Smyrna
        ('SPA', RegionType.COAST, True, None),        # Spain
        ('STP', RegionType.COAST, True, 'RUSSIA'),    # St Petersburg
        ('SWE', RegionType.COAST, True, None),        # Sweden
        ('TRI', RegionType.COAST, True, 'AUSTRIA'),   # Trieste
        ('TUN', RegionType.COAST, True, None),        # Tunis
        ('VEN', RegionType.COAST, True, 'ITALY'),     # Venice
        
        # Coastal regions (non-supply centers)
        ('ALB', RegionType.COAST, False, None),       # Albania
        ('APU', RegionType.COAST, False, None),       # Apulia
        ('ARM', RegionType.COAST, False, None),       # Armenia
        ('CLY', RegionType.COAST, False, None),       # Clyde
        ('FIN', RegionType.COAST, False, None),       # Finland
        ('GAS', RegionType.COAST, False, None),       # Gascony
        ('LVN', RegionType.COAST, False, None),       # Livonia
        ('NAF', RegionType.COAST, False, None),       # North Africa
        ('PIC', RegionType.COAST, False, None),       # Picardy
        ('PIE', RegionType.COAST, False, None),       # Piedmont
        ('PRU', RegionType.COAST, False, None),       # Prussia
        ('SYR', RegionType.COAST, False, None),       # Syria
        ('TUS', RegionType.COAST, False, None),       # Tuscany
        ('WAL', RegionType.COAST, False, None),       # Wales
        ('YOR', RegionType.COAST, False, None),       # Yorkshire
        
        # Land regions (supply centers)
        ('BUD', RegionType.LAND, True, 'AUSTRIA'),    # Budapest
        ('MOS', RegionType.LAND, True, 'RUSSIA'),     # Moscow
        ('MUN', RegionType.LAND, True, 'GERMANY'),    # Munich
        ('PAR', RegionType.LAND, True, 'FRANCE'),     # Paris
        ('SER', RegionType.LAND, True, None),         # Serbia
        ('VIE', RegionType.LAND, True, 'AUSTRIA'),    # Vienna
        ('WAR', RegionType.LAND, True, 'RUSSIA'),     # Warsaw
        
        # Land regions (non-supply centers)
        ('BOH', RegionType.LAND, False, None),        # Bohemia
        ('BUR', RegionType.LAND, False, None),        # Burgundy
        ('GAL', RegionType.LAND, False, None),        # Galicia
        ('RUH', RegionType.LAND, False, None),        # Ruhr
        ('SIL', RegionType.LAND, False, None),        # Silesia
        ('TYR', RegionType.LAND, False, None),        # Tyrolia
        ('UKR', RegionType.LAND, False, None),        # Ukraine
    ]
    
    # Add all regions to the map
    for name, region_type, is_sc, home_for in regions_data:
        game_map.add_region(name, region_type, is_sc, home_for)
    
    # Define adjacencies (from the standard Diplomacy map)
    adjacencies = [
        # Western Europe
        ('BRE', 'ENG'), ('BRE', 'MAO'), ('BRE', 'PAR'), ('BRE', 'PIC'), ('BRE', 'GAS'),
        ('PAR', 'PIC'), ('PAR', 'BUR'), ('PAR', 'GAS'),
        ('MAR', 'PIE'), ('MAR', 'BUR'), ('MAR', 'GAS'), ('MAR', 'LYO'), ('MAR', 'SPA'),
        ('GAS', 'SPA'), ('GAS', 'BUR'), ('GAS', 'MAO'),
        ('PIC', 'BUR'), ('PIC', 'BEL'), ('PIC', 'ENG'),
        ('BUR', 'RUH'), ('BUR', 'BEL'), ('BUR', 'MUN'),
        
        # British Isles
        ('EDI', 'CLY'), ('EDI', 'YOR'), ('EDI', 'NTH'), ('EDI', 'NWG'),
        ('CLY', 'NAO'), ('CLY', 'NWG'), ('CLY', 'LVP'),
        ('LVP', 'YOR'), ('LVP', 'WAL'), ('LVP', 'IRI'), ('LVP', 'NAO'),
        ('YOR', 'WAL'), ('YOR', 'LON'), ('YOR', 'NTH'),
        ('WAL', 'LON'), ('WAL', 'ENG'), ('WAL', 'IRI'),
        ('LON', 'NTH'), ('LON', 'ENG'),
        
        # Seas around Britain
        ('IRI', 'NAO'), ('IRI', 'MAO'), ('IRI', 'ENG'),
        ('NAO', 'NWG'), ('NAO', 'MAO'),
        ('ENG', 'NTH'), ('ENG', 'MAO'), ('ENG', 'BEL'),
        ('NTH', 'NWG'), ('NTH', 'SKA'), ('NTH', 'DEN'), ('NTH', 'HEL'), 
        ('NTH', 'HOL'), ('NTH', 'BEL'), ('NTH', 'NWY'),
        ('NWG', 'BAR'), ('NWG', 'NWY'),
        ('BAR', 'STP'), ('BAR', 'NWY'),
        
        # Central Europe
        ('HOL', 'BEL'), ('HOL', 'KIE'), ('HOL', 'RUH'), ('HOL', 'HEL'),
        ('BEL', 'RUH'),
        ('RUH', 'KIE'), ('RUH', 'MUN'),
        ('KIE', 'BER'), ('KIE', 'MUN'), ('KIE', 'DEN'), ('KIE', 'HEL'), ('KIE', 'BAL'),
        ('BER', 'PRU'), ('BER', 'SIL'), ('BER', 'MUN'), ('BER', 'BAL'),
        ('MUN', 'BOH'), ('MUN', 'TYR'), ('MUN', 'SIL'),
        
        # Scandinavia
        ('DEN', 'SKA'), ('DEN', 'BAL'), ('DEN', 'SWE'), ('DEN', 'HEL'),
        ('NWY', 'SWE'), ('NWY', 'FIN'), ('NWY', 'STP'), ('NWY', 'SKA'),
        ('SWE', 'FIN'), ('SWE', 'STP'), ('SWE', 'SKA'), ('SWE', 'BAL'), ('SWE', 'BOT'),
        ('FIN', 'STP'), ('FIN', 'BOT'),
        ('SKA', 'BAL'),
        
        # Baltic Region
        ('BAL', 'PRU'), ('BAL', 'LVN'), ('BAL', 'BOT'),
        ('BOT', 'STP'), ('BOT', 'LVN'),
        ('PRU', 'SIL'), ('PRU', 'WAR'), ('PRU', 'LVN'),
        ('SIL', 'BOH'), ('SIL', 'GAL'), ('SIL', 'WAR'),
        
        # Eastern Europe
        ('STP', 'MOS'), ('STP', 'LVN'),
        ('LVN', 'MOS'), ('LVN', 'WAR'),
        ('MOS', 'UKR'), ('MOS', 'SEV'), ('MOS', 'WAR'),
        ('WAR', 'UKR'), ('WAR', 'GAL'),
        ('UKR', 'SEV'), ('UKR', 'RUM'), ('UKR', 'GAL'),
        ('SEV', 'RUM'), ('SEV', 'ARM'), ('SEV', 'BLA'),
        
        # Italy and Adriatic
        ('PIE', 'TYR'), ('PIE', 'VEN'), ('PIE', 'TUS'), ('PIE', 'LYO'),
        ('VEN', 'TYR'), ('VEN', 'TRI'), ('VEN', 'APU'), ('VEN', 'ROM'), 
        ('VEN', 'TUS'), ('VEN', 'ADR'),
        ('TYR', 'BOH'), ('TYR', 'VIE'), ('TYR', 'TRI'), ('TYR', 'MUN'),
        ('TUS', 'ROM'), ('TUS', 'LYO'), ('TUS', 'TYS'),
        ('ROM', 'NAP'), ('ROM', 'APU'), ('ROM', 'TYS'),
        ('NAP', 'APU'), ('NAP', 'ION'), ('NAP', 'TYS'),
        ('APU', 'ADR'), ('APU', 'ION'),
        
        # Mediterranean Seas
        ('LYO', 'TYS'), ('LYO', 'WES'), ('LYO', 'SPA'),
        ('WES', 'TYS'), ('WES', 'TUN'), ('WES', 'NAF'), ('WES', 'SPA'),
        ('TYS', 'ION'), ('TYS', 'TUN'),
        ('ION', 'ADR'), ('ION', 'ALB'), ('ION', 'GRE'), ('ION', 'TUN'), 
        ('ION', 'EAS'), ('ION', 'AEG'),
        ('ADR', 'TRI'), ('ADR', 'ALB'),
        ('AEG', 'EAS'), ('AEG', 'GRE'), ('AEG', 'BUL'), ('AEG', 'CON'), ('AEG', 'SMY'),
        ('EAS', 'SMY'), ('EAS', 'SYR'),
        
        # Iberian Peninsula
        ('SPA', 'POR'), ('SPA', 'GAS'), ('SPA', 'MAO'), ('SPA', 'MAR'),
        ('POR', 'MAO'),
        ('MAO', 'NAF'),
        
        # North Africa
        ('NAF', 'TUN'), ('TUN', 'NAF'),
        
        # Balkans
        ('BOH', 'VIE'), ('BOH', 'GAL'),
        ('VIE', 'GAL'), ('VIE', 'BUD'), ('VIE', 'TRI'),
        ('GAL', 'BUD'), ('GAL', 'RUM'),
        ('BUD', 'TRI'), ('BUD', 'SER'), ('BUD', 'RUM'),
        ('TRI', 'ALB'), ('TRI', 'SER'),
        ('SER', 'ALB'), ('SER', 'GRE'), ('SER', 'BUL'), ('SER', 'RUM'),
        ('RUM', 'BUL'), ('RUM', 'BLA'),
        ('BUL', 'GRE'), ('BUL', 'CON'), ('BUL', 'BLA'), ('BUL', 'AEG'),
        ('GRE', 'ALB'), ('ALB', 'ADR'), ('ALB', 'ION'),
        
        # Black Sea and Turkey
        ('BLA', 'ANK'), ('BLA', 'ARM'), ('BLA', 'CON'),
        ('CON', 'ANK'), ('CON', 'SMY'),
        ('ANK', 'ARM'), ('ANK', 'SMY'),
        ('ARM', 'SYR'), ('ARM', 'SMY'),
        ('SMY', 'SYR'), ('SMY', 'EAS')
    ]
    
    # Add all adjacencies to the map
    for region1, region2 in adjacencies:
        game_map.add_adjacency(region1, region2)
    
    return game_map

def main():
    """Create and visualize a Diplomacy map"""
    # Create the map with all regions and adjacencies
    print("Creating Diplomacy map...")
    game_map = create_diplomacy_map()
    
    # Generate the hex grid layout
    print("Generating hex grid layout...")
    game_map.generate_map()
    
    # Verify adjacencies are correct
    print("\nVerifying adjacencies...")
    expected_adjacencies = {}
    for region_name, region in game_map.regions.items():
        expected_adjacencies[region_name] = len(region.adjacent_regions)
    
    actual_adjacencies = game_map.get_region_adjacency_counts()
    
    adjacency_issues = []
    for region_name, expected_count in expected_adjacencies.items():
        actual_count = actual_adjacencies.get(region_name, 0)
        if actual_count != expected_count:
            adjacency_issues.append(
                f"{region_name}: Expected {expected_count}, got {actual_count}"
            )
    
    if adjacency_issues:
        print("Adjacency issues found:")
        for issue in adjacency_issues:
            print(f"  {issue}")
    else:
        print("All adjacencies verified correctly!")
    
    # Print region sizes
    print("\nRegion sizes (hexes):")
    for region_name, size in sorted(game_map.region_sizes.items()):
        actual_size = len(game_map.regions[region_name].hexes)
        print(f"{region_name}: {actual_size} hexes (target: {size})")
    
    # Visualize the map
    print("\nMap visualization:")
    visualization = game_map.visualize_map()
    print(visualization)
    
    # Statistics
    total_hexes = sum(len(region.hexes) for region in game_map.regions.values())
    print(f"\nTotal hexagons used: {total_hexes}")
    print(f"Average hexes per region: {total_hexes / len(game_map.regions):.2f}")
    
    # Most efficiently placed regions (actual vs target size)
    efficiency = []
    for name, region in game_map.regions.items():
        target = game_map.region_sizes[name]
        actual = len(region.hexes)
        if target > 0:
            efficiency.append((name, actual/target, actual, target))
    
    print("\nMost efficient region placements:")
    for name, ratio, actual, target in sorted(efficiency, key=lambda x: x[1])[:5]:
        print(f"{name}: {actual}/{target} hexes ({ratio:.2f}x)")
    
    print("\nLeast efficient region placements:")
    for name, ratio, actual, target in sorted(efficiency, key=lambda x: x[1], reverse=True)[:5]:
        print(f"{name}: {actual}/{target} hexes ({ratio:.2f}x)")

if __name__ == "__main__":
    main()