#!/usr/bin/env python3
"""
Complex Problem 2: Algorithm Implementation and Optimization
"""

import asyncio
import sys
sys.path.append('/home/krawin/exp.code/jarvis')

from core.execution.docker_executor import DockerCodeExecutor, ExecutionConfig

async def problem_2_algorithms():
    """Problem 2: Complex Algorithm Implementation"""
    print("🔢 PROBLEM 2: Algorithm Implementation & Optimization")
    print("=" * 55)
    print("Task: Implement graph algorithms, pathfinding, and optimization")
    
    code = """
# Complex Algorithm Implementation Problem
import heapq
from collections import defaultdict, deque

class Graph:
    def __init__(self):
        self.vertices = defaultdict(list)
        self.weights = {}
    
    def add_edge(self, u, v, weight=1):
        self.vertices[u].append(v)
        self.vertices[v].append(u)
        self.weights[(u, v)] = weight
        self.weights[(v, u)] = weight
    
    def dijkstra(self, start, end):
        distances = defaultdict(lambda: float('inf'))
        distances[start] = 0
        previous = {}
        pq = [(0, start)]
        visited = set()
        
        while pq:
            current_distance, current = heapq.heappop(pq)
            
            if current in visited:
                continue
                
            visited.add(current)
            
            if current == end:
                break
            
            for neighbor in self.vertices[current]:
                weight = self.weights.get((current, neighbor), 1)
                distance = current_distance + weight
                
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current
                    heapq.heappush(pq, (distance, neighbor))
        
        # Reconstruct path
        path = []
        current = end
        while current in previous:
            path.append(current)
            current = previous[current]
        path.append(start)
        path.reverse()
        
        return distances[end], path
    
    def bfs_shortest_path(self, start, end):
        if start == end:
            return [start]
        
        visited = {start}
        queue = deque([(start, [start])])
        
        while queue:
            current, path = queue.popleft()
            
            for neighbor in self.vertices[current]:
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    if neighbor == end:
                        return new_path
                    visited.add(neighbor)
                    queue.append((neighbor, new_path))
        
        return None

def solve_traveling_salesman_dp(distances, n):
    # Dynamic Programming solution for small TSP
    dp = {}
    
    def tsp(mask, pos):
        if mask == (1 << n) - 1:
            return distances[pos][0]
        
        if (mask, pos) in dp:
            return dp[(mask, pos)]
        
        ans = float('inf')
        for city in range(n):
            if mask & (1 << city) == 0:
                new_ans = distances[pos][city] + tsp(mask | (1 << city), city)
                ans = min(ans, new_ans)
        
        dp[(mask, pos)] = ans
        return ans
    
    return tsp(1, 0)

print("=== GRAPH ALGORITHMS TESTING ===")

# Create a sample graph
g = Graph()
edges = [
    ('A', 'B', 4), ('A', 'C', 2), ('B', 'C', 1), ('B', 'D', 5),
    ('C', 'D', 8), ('C', 'E', 10), ('D', 'E', 2), ('D', 'F', 6),
    ('E', 'F', 3)
]

for u, v, w in edges:
    g.add_edge(u, v, w)

print("Graph created with vertices: A, B, C, D, E, F")

# Test Dijkstra's algorithm
print("\\n1. Dijkstra's Shortest Path (A to F):")
distance, path = g.dijkstra('A', 'F')
print(f"   Distance: {distance}")
print(f"   Path: {' -> '.join(path)}")

# Test BFS
print("\\n2. BFS Shortest Path (A to F):")
bfs_path = g.bfs_shortest_path('A', 'F')
if bfs_path:
    print(f"   Path: {' -> '.join(bfs_path)}")
    print(f"   Steps: {len(bfs_path) - 1}")

# Test TSP for small graph
print("\\n3. Traveling Salesman Problem (4 cities):")
tsp_distances = [
    [0, 10, 15, 20],
    [10, 0, 35, 25],
    [15, 35, 0, 30],
    [20, 25, 30, 0]
]
tsp_result = solve_traveling_salesman_dp(tsp_distances, 4)
print(f"   Minimum tour cost: {tsp_result}")

# Performance test with larger data
print("\\n4. Performance Test - Large Graph:")
large_graph = Graph()
for i in range(20):
    for j in range(i+1, 20):
        weight = (i + j) % 10 + 1
        large_graph.add_edge(f"N{i}", f"N{j}", weight)

large_distance, large_path = large_graph.dijkstra("N0", "N19")
print(f"   Path from N0 to N19: {large_distance} (via {len(large_path)} nodes)")

print("\\n=== ALGORITHM TESTING COMPLETE ===")
"""
    
    executor = DockerCodeExecutor()
    executor.docker_available = False
    
    config = ExecutionConfig(language="python", timeout=20)
    result = await executor.execute_code(code, config)
    
    print(f"✅ Success: {result.success}")
    print(f"Output:\n{result.output}")
    print(f"Execution time: {result.execution_time:.3f}s")
    
    return result.success

if __name__ == "__main__":
    result = asyncio.run(problem_2_algorithms())
    print(f"\n🎯 Problem 2 Result: {'PASSED' if result else 'FAILED'}")
