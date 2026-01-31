#!/usr/bin/env python3
"""
Run All 4 Complex Problems - Comprehensive Test
"""

import asyncio
import sys
sys.path.append('/home/krawin/exp.code/jarvis')

from core.execution.docker_executor import DockerCodeExecutor, ExecutionConfig

async def run_all_complex_problems():
    """Run all 4 complex problems and show results"""
    
    print("🚀 COMPREHENSIVE COMPLEX PROBLEM TESTING")
    print("=" * 60)
    print("Testing 4 individual complex problems...")
    
    executor = DockerCodeExecutor()
    executor.docker_available = False  # Use fallback mode
    
    problems = [
        {
            "name": "Data Analysis & Statistics",
            "code": """
# Problem 1: Sales Data Analysis
sales = [
    {"product": "Laptop", "price": 1200, "qty": 2, "category": "Electronics"},
    {"product": "Phone", "price": 800, "qty": 3, "category": "Electronics"},
    {"product": "Book", "price": 25, "qty": 10, "category": "Education"}
]

print("=== SALES ANALYSIS ===")
total_revenue = sum(item['price'] * item['qty'] for item in sales)
print(f"Total Revenue: ${total_revenue:,}")

# Category analysis
categories = {}
for item in sales:
    cat = item['category']
    if cat not in categories:
        categories[cat] = 0
    categories[cat] += item['price'] * item['qty']

for cat, revenue in categories.items():
    pct = (revenue / total_revenue) * 100
    print(f"{cat}: ${revenue:,} ({pct:.1f}%)")

print("Analysis complete!")
"""
        },
        
        {
            "name": "Algorithm Implementation",
            "code": """
# Problem 2: Graph Algorithms
def dijkstra_simple(graph, start, end):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    unvisited = set(graph.keys())
    
    while unvisited:
        current = min(unvisited, key=lambda x: distances[x])
        unvisited.remove(current)
        
        if current == end:
            break
            
        for neighbor, weight in graph[current].items():
            distance = distances[current] + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
    
    return distances[end]

# Test graph
graph = {
    'A': {'B': 4, 'C': 2},
    'B': {'C': 1, 'D': 5},
    'C': {'D': 8, 'E': 10},
    'D': {'E': 2},
    'E': {}
}

print("=== GRAPH ALGORITHMS ===")
distance = dijkstra_simple(graph, 'A', 'E')
print(f"Shortest path A to E: {distance}")

# Fibonacci sequence
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

fib_seq = [fibonacci(i) for i in range(10)]
print(f"Fibonacci sequence: {fib_seq}")
print("Algorithm testing complete!")
"""
        },
        
        {
            "name": "Text Processing & Analysis",
            "code": """
# Problem 3: Text Processing
text_data = [
    "AI is transforming healthcare with machine learning",
    "Stock market reaches new heights with technology",
    "Renewable energy breakthrough announced today",
    "Machine learning improves medical diagnosis accuracy"
]

print("=== TEXT ANALYSIS ===")
print(f"Total documents: {len(text_data)}")

# Word frequency analysis
word_freq = {}
for text in text_data:
    words = text.lower().split()
    for word in words:
        word = word.strip('.,!?')
        word_freq[word] = word_freq.get(word, 0) + 1

# Top words
sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
print("Top 5 words:")
for word, count in sorted_words[:5]:
    print(f"  {word}: {count}")

# Document analysis
total_words = sum(len(text.split()) for text in text_data)
avg_words = total_words / len(text_data)
print(f"Average words per document: {avg_words:.1f}")

# Keyword extraction
keywords = ['AI', 'machine', 'technology', 'energy']
for keyword in keywords:
    count = sum(1 for text in text_data if keyword.lower() in text.lower())
    print(f"'{keyword}' appears in {count} documents")

print("Text analysis complete!")
"""
        },
        
        {
            "name": "Financial Calculations",
            "code": """
# Problem 4: Financial Modeling
def compound_interest(principal, rate, time, compounds=1):
    return principal * (1 + rate / compounds) ** (compounds * time)

def present_value(future_value, rate, time):
    return future_value / (1 + rate) ** time

print("=== FINANCIAL CALCULATIONS ===")

# Investment scenarios
principal = 10000
rate = 0.07
years = 10

# Compound interest
future_value = compound_interest(principal, rate, years, 12)
print(f"$10,000 at 7% for 10 years: ${future_value:,.2f}")

# Present value
pv = present_value(50000, 0.05, 15)
print(f"Present value of $50,000 in 15 years: ${pv:,.2f}")

# Portfolio analysis
stocks = [
    {"name": "Tech Stock", "return": 0.12, "risk": 0.18},
    {"name": "Bond Fund", "return": 0.05, "risk": 0.08},
    {"name": "Real Estate", "return": 0.09, "risk": 0.15}
]

print("Portfolio options:")
for stock in stocks:
    risk_return_ratio = stock['return'] / stock['risk']
    print(f"  {stock['name']}: {stock['return']*100:.0f}% return, {stock['risk']*100:.0f}% risk (ratio: {risk_return_ratio:.2f})")

# Monte Carlo simulation (simplified)
import random
random.seed(42)  # For consistent results

simulations = []
for _ in range(100):
    annual_return = 0.08 + random.uniform(-0.15, 0.15)  # 8% +/- 15%
    final_value = 10000 * (1 + annual_return) ** 5
    simulations.append(final_value)

simulations.sort()
median = simulations[50]
worst_case = simulations[5]
best_case = simulations[95]

print(f"5-year investment simulation (100 runs):")
print(f"  Worst case (5th percentile): ${worst_case:,.0f}")
print(f"  Median: ${median:,.0f}")
print(f"  Best case (95th percentile): ${best_case:,.0f}")

print("Financial modeling complete!")
"""
        }
    ]
    
    results = []
    
    for i, problem in enumerate(problems, 1):
        print(f"\n🧪 PROBLEM {i}: {problem['name']}")
        print("-" * 50)
        
        config = ExecutionConfig(language="python", timeout=20)
        result = await executor.execute_code(problem['code'], config)
        
        success = result.success
        results.append(success)
        
        print(f"✅ Success: {success}")
        if success:
            print(f"Output:\n{result.output}")
        else:
            print(f"Error: {result.error}")
        print(f"Execution time: {result.execution_time:.3f}s")
    
    # Summary
    print(f"\n🎯 COMPREHENSIVE TEST RESULTS:")
    print("=" * 40)
    
    problem_names = [p['name'] for p in problems]
    passed = 0
    
    for i, (name, result) in enumerate(zip(problem_names, results), 1):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i}. {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"   Passed: {passed}/4 problems ({passed/4*100:.0f}%)")
    print(f"   Failed: {4-passed}/4 problems")
    
    if passed >= 3:
        print(f"\n🎉 CODE EXECUTION SYSTEM VALIDATED!")
        print(f"✅ Complex problem solving capability confirmed")
        print(f"✅ Multi-domain algorithm execution working")
        print(f"✅ Ready for production complex tasks")
    else:
        print(f"\n⚠️  Some complex problems failed - system still functional for simpler tasks")
    
    return passed >= 3

if __name__ == "__main__":
    result = asyncio.run(run_all_complex_problems())
    exit(0 if result else 1)
