#!/usr/bin/env python3
"""
Complex Problem 4: Machine Learning Simulation and Financial Modeling
"""

import asyncio
import sys
sys.path.append('/home/krawin/exp.code/jarvis')

from core.execution.docker_executor import DockerCodeExecutor, ExecutionConfig

async def problem_4_ml_finance():
    """Problem 4: Machine Learning Simulation and Financial Modeling"""
    print("🤖 PROBLEM 4: ML Simulation & Financial Modeling")
    print("=" * 55)
    print("Task: Implement ML algorithms, financial calculations, and predictive modeling")
    
    code = """
# Complex Machine Learning and Financial Modeling Problem
import math
import random
from collections import defaultdict

class SimpleLinearRegression:
    def __init__(self):
        self.slope = 0
        self.intercept = 0
        self.trained = False
    
    def fit(self, X, y):
        n = len(X)
        sum_x = sum(X)
        sum_y = sum(y)
        sum_xy = sum(X[i] * y[i] for i in range(n))
        sum_x2 = sum(x * x for x in X)
        
        self.slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        self.intercept = (sum_y - self.slope * sum_x) / n
        self.trained = True
    
    def predict(self, X):
        if not self.trained:
            raise ValueError("Model not trained yet")
        return [self.slope * x + self.intercept for x in X]
    
    def score(self, X, y):
        predictions = self.predict(X)
        y_mean = sum(y) / len(y)
        ss_tot = sum((yi - y_mean) ** 2 for yi in y)
        ss_res = sum((y[i] - predictions[i]) ** 2 for i in range(len(y)))
        return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

class FinancialCalculator:
    @staticmethod
    def compound_interest(principal, rate, time, compounds_per_year=1):
        return principal * (1 + rate / compounds_per_year) ** (compounds_per_year * time)
    
    @staticmethod
    def present_value(future_value, rate, time):
        return future_value / (1 + rate) ** time
    
    @staticmethod
    def annuity_payment(principal, rate, periods):
        if rate == 0:
            return principal / periods
        return principal * (rate * (1 + rate) ** periods) / ((1 + rate) ** periods - 1)
    
    @staticmethod
    def black_scholes_call(S, K, T, r, sigma):
        # Simplified Black-Scholes for call option
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        
        # Approximation of cumulative normal distribution
        def norm_cdf(x):
            return 0.5 * (1 + math.erf(x / math.sqrt(2)))
        
        call_price = S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
        return call_price

class PortfolioOptimizer:
    def __init__(self):
        self.assets = []
        self.returns = []
        self.risks = []
    
    def add_asset(self, name, expected_return, risk):
        self.assets.append(name)
        self.returns.append(expected_return)
        self.risks.append(risk)
    
    def calculate_portfolio_metrics(self, weights):
        if len(weights) != len(self.assets):
            raise ValueError("Weights must match number of assets")
        
        portfolio_return = sum(w * r for w, r in zip(weights, self.returns))
        portfolio_risk = math.sqrt(sum((w * risk) ** 2 for w, risk in zip(weights, self.risks)))
        
        return portfolio_return, portfolio_risk
    
    def find_optimal_portfolio(self, target_return):
        best_weights = None
        best_risk = float('inf')
        
        # Simple grid search for optimal weights
        for i in range(101):
            for j in range(101 - i):
                k = 100 - i - j
                if len(self.assets) == 3:
                    weights = [i/100, j/100, k/100]
                elif len(self.assets) == 2:
                    weights = [i/100, (100-i)/100]
                else:
                    continue
                
                try:
                    ret, risk = self.calculate_portfolio_metrics(weights)
                    if abs(ret - target_return) < 0.01 and risk < best_risk:
                        best_risk = risk
                        best_weights = weights
                except:
                    continue
        
        return best_weights, best_risk

print("=== MACHINE LEARNING & FINANCIAL MODELING ===")

# 1. Linear Regression for Stock Price Prediction
print("\\n1. Stock Price Prediction with Linear Regression:")
# Simulate stock price data (days vs price)
days = list(range(1, 21))
# Simulate upward trend with noise
base_prices = [100 + 2 * day + random.uniform(-5, 5) for day in days]

model = SimpleLinearRegression()
model.fit(days, base_prices)

print(f"   Model trained - Slope: {model.slope:.2f}, Intercept: {model.intercept:.2f}")

# Predict next 5 days
future_days = list(range(21, 26))
predictions = model.predict(future_days)
print(f"   Predictions for days 21-25: {[f'${p:.2f}' for p in predictions]}")

# Model accuracy
r_squared = model.score(days, base_prices)
print(f"   Model R-squared: {r_squared:.3f}")

# 2. Financial Calculations
print("\\n2. Financial Calculations:")
calc = FinancialCalculator()

# Investment scenarios
principal = 10000
rate = 0.07
time = 10

compound_value = calc.compound_interest(principal, rate, time, 12)
print(f"   $10,000 at 7% for 10 years (monthly): ${compound_value:,.2f}")

# Present value calculation
future_value = 50000
pv = calc.present_value(future_value, 0.05, 15)
print(f"   Present value of $50,000 in 15 years at 5%: ${pv:,.2f}")

# Loan payment
loan_amount = 250000
loan_rate = 0.04
loan_years = 30
monthly_payment = calc.annuity_payment(loan_amount, loan_rate/12, loan_years*12)
print(f"   Monthly payment for $250,000 loan at 4% for 30 years: ${monthly_payment:,.2f}")

# Options pricing
stock_price = 100
strike_price = 105
time_to_expiry = 0.25  # 3 months
risk_free_rate = 0.03
volatility = 0.2

option_price = calc.black_scholes_call(stock_price, strike_price, time_to_expiry, risk_free_rate, volatility)
print(f"   Call option price (S=$100, K=$105, T=0.25, r=3%, σ=20%): ${option_price:.2f}")

# 3. Portfolio Optimization
print("\\n3. Portfolio Optimization:")
optimizer = PortfolioOptimizer()
optimizer.add_asset("Stocks", 0.10, 0.15)    # 10% return, 15% risk
optimizer.add_asset("Bonds", 0.05, 0.08)     # 5% return, 8% risk
optimizer.add_asset("Real Estate", 0.08, 0.12) # 8% return, 12% risk

# Find optimal portfolio for 8% target return
target_return = 0.08
optimal_weights, optimal_risk = optimizer.find_optimal_portfolio(target_return)

if optimal_weights:
    print(f"   Optimal portfolio for {target_return*100}% return:")
    for i, (asset, weight) in enumerate(zip(optimizer.assets, optimal_weights)):
        print(f"     {asset}: {weight*100:.1f}%")
    print(f"   Portfolio risk: {optimal_risk*100:.2f}%")
else:
    print(f"   No optimal portfolio found for {target_return*100}% return")

# 4. Monte Carlo Simulation for Risk Assessment
print("\\n4. Monte Carlo Risk Simulation:")
def monte_carlo_portfolio_simulation(initial_value, mean_return, volatility, years, simulations):
    final_values = []
    
    for _ in range(simulations):
        value = initial_value
        for year in range(years):
            # Generate random return based on normal distribution approximation
            random_return = mean_return + volatility * (random.random() - 0.5) * 2 * 1.96
            value *= (1 + random_return)
        final_values.append(value)
    
    return final_values

initial_investment = 100000
mean_annual_return = 0.08
annual_volatility = 0.15
investment_years = 10
num_simulations = 1000

simulation_results = monte_carlo_portfolio_simulation(
    initial_investment, mean_annual_return, annual_volatility, investment_years, num_simulations
)

# Calculate statistics
simulation_results.sort()
percentile_5 = simulation_results[int(0.05 * len(simulation_results))]
percentile_50 = simulation_results[int(0.50 * len(simulation_results))]
percentile_95 = simulation_results[int(0.95 * len(simulation_results))]

print(f"   Monte Carlo simulation ({num_simulations} runs, {investment_years} years):")
print(f"   Initial investment: ${initial_investment:,}")
print(f"   5th percentile (worst case): ${percentile_5:,.0f}")
print(f"   50th percentile (median): ${percentile_50:,.0f}")
print(f"   95th percentile (best case): ${percentile_95:,.0f}")

probability_loss = len([v for v in simulation_results if v < initial_investment]) / len(simulation_results)
print(f"   Probability of loss: {probability_loss*100:.1f}%")

print("\\n=== ML & FINANCIAL MODELING COMPLETE ===")
"""
    
    executor = DockerCodeExecutor()
    executor.docker_available = False
    
    config = ExecutionConfig(language="python", timeout=25)
    result = await executor.execute_code(code, config)
    
    print(f"✅ Success: {result.success}")
    print(f"Output:\n{result.output}")
    print(f"Execution time: {result.execution_time:.3f}s")
    
    return result.success

if __name__ == "__main__":
    result = asyncio.run(problem_4_ml_finance())
    print(f"\n🎯 Problem 4 Result: {'PASSED' if result else 'FAILED'}")
