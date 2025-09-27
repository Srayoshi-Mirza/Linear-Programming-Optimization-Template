"""
SUPPLY CHAIN OPTIMIZATION TEMPLATE
========================================
A concise template for multi-echelon supply chain optimization.
Replace placeholders with your actual data and parameters.
"""

from pulp import *
import pandas as pd
import numpy as np

# =============================================================================
# DEFINE NETWORK DIMENSIONS (Replace with your values)
# =============================================================================
F = 6  # Number of suppliers/farms
D = 6  # Number of distributors/intermediaries  
R = 6  # Number of retailers/customers
T = 10 # Number of time periods

# =============================================================================
# DEFINE SETS
# =============================================================================
suppliers = range(F)
distributors = range(D)
retailers = range(R)
time_periods = range(T)

# =============================================================================
# LOAD DATA (Replace with your data loading logic)
# =============================================================================
def load_data():
    """Load your supply chain parameters - customize this function"""
    
    # Example data structure - replace with your actual data
    data = {
        # Demand: demand[r][t] = demand for retailer r in period t
        'demand': [[100 + np.random.randint(-20, 20) for t in time_periods] for r in retailers],
        
        # Capacity: capacity[f][t] = capacity of supplier f in period t
        'capacity': [[500 for t in time_periods] for f in suppliers],
        
        # Costs: cost[f] = unit production cost at supplier f
        'production_cost': [2.5 + 0.1*f for f in suppliers],
        
        # Distances/Transport costs
        'transport_fd': [[10 + abs(f-d)*5 for d in distributors] for f in suppliers],
        'transport_dr': [[5 + abs(d-r)*3 for r in retailers] for d in distributors],
        
        # Storage and waste costs
        'storage_cost_dist': 0.2,
        'storage_cost_retail': 0.5,
        'waste_cost_dist': 150,
        'waste_cost_retail': 180,
        'shelf_life_limit': 100
    }
    
    return data

# =============================================================================
# DECISION VARIABLES
# =============================================================================
# x[f][d][t] = flow from supplier f to distributor d in period t
x = LpVariable.dicts("SupplierToDistributor", (suppliers, distributors, time_periods), lowBound=0)

# y[d][r][t] = flow from distributor d to retailer r in period t  
y = LpVariable.dicts("DistributorToRetailer", (distributors, retailers, time_periods), lowBound=0)

# Inventory variables
I_dist = LpVariable.dicts("DistributorInventory", (distributors, time_periods), lowBound=0)
I_retail = LpVariable.dicts("RetailerInventory", (retailers, time_periods), lowBound=0)

# Waste variables (optional - for perishable products)
W_dist = LpVariable.dicts("DistributorWaste", (distributors, time_periods), lowBound=0)
W_retail = LpVariable.dicts("RetailerWaste", (retailers, time_periods), lowBound=0)

# =============================================================================
# CREATE OPTIMIZATION MODEL
# =============================================================================
model = LpProblem("SupplyChainOptimization", LpMinimize)

# Load data
data = load_data()

# =============================================================================
# OBJECTIVE FUNCTION - Minimize total costs
# =============================================================================
model += (
    # Production costs
    lpSum(data['production_cost'][f] * x[f][d][t] 
          for f in suppliers for d in distributors for t in time_periods)
    
    # Transportation costs: supplier to distributor
    + lpSum(data['transport_fd'][f][d] * x[f][d][t] 
            for f in suppliers for d in distributors for t in time_periods)
    
    # Transportation costs: distributor to retailer
    + lpSum(data['transport_dr'][d][r] * y[d][r][t] 
            for d in distributors for r in retailers for t in time_periods)
    
    # Storage costs
    + lpSum(data['storage_cost_dist'] * I_dist[d][t] 
            for d in distributors for t in time_periods)
    + lpSum(data['storage_cost_retail'] * I_retail[r][t] 
            for r in retailers for t in time_periods)
    
    # Waste costs (optional)
    + lpSum(data['waste_cost_dist'] * W_dist[d][t] 
            for d in distributors for t in time_periods)  
    + lpSum(data['waste_cost_retail'] * W_retail[r][t] 
            for r in retailers for t in time_periods)
)

# =============================================================================
# CONSTRAINTS
# =============================================================================

# 1. Demand satisfaction
for r in retailers:
    for t in time_periods:
        model += lpSum(y[d][r][t] for d in distributors) >= data['demand'][r][t]

# 2. Supplier capacity constraints
for f in suppliers:
    for t in time_periods:
        model += lpSum(x[f][d][t] for d in distributors) <= data['capacity'][f][t]

# 3. Inventory balance - Distributors
for d in distributors:
    for t in time_periods:
        inflow = lpSum(x[f][d][t] for f in suppliers)
        outflow = lpSum(y[d][r][t] for r in retailers)
        prev_inventory = I_dist[d][t-1] if t > 0 else 0
        
        model += I_dist[d][t] == prev_inventory + inflow - outflow - W_dist[d][t]

# 4. Inventory balance - Retailers  
for r in retailers:
    for t in time_periods:
        inflow = lpSum(y[d][r][t] for d in distributors)
        prev_inventory = I_retail[r][t-1] if t > 0 else 0
        
        model += I_retail[r][t] == prev_inventory + inflow - data['demand'][r][t] - W_retail[r][t]

# 5. Waste constraints (optional - for perishable products)
for d in distributors:
    for t in time_periods:
        model += W_dist[d][t] >= I_dist[d][t] - data['shelf_life_limit']

for r in retailers:
    for t in time_periods:
        model += W_retail[r][t] >= I_retail[r][t] - data['shelf_life_limit']

# =============================================================================
# SOLVE MODEL
# =============================================================================
print(" Solving optimization model...")
model.solve(PULP_CBC_CMD(msg=1))

print(f"Status: {LpStatus[model.status]}")
if model.status == LpStatusOptimal:
    print(f" Total Cost: {value(model.objective):,.2f}")
    
    # Extract key results (non-zero flows only)
    print("\n KEY RESULTS:")
    
    # Flow results
    for f in suppliers:
        for d in distributors:
            for t in time_periods:
                if x[f][d][t].value() > 0:
                    print(f"Supplier {f} → Distributor {d} (Period {t}): {x[f][d][t].value():.1f}")
    
    # Export results to CSV (optional)
    results = []
    for f in suppliers:
        for d in distributors:
            for t in time_periods:
                if x[f][d][t].value() > 0:
                    results.append({
                        'Supplier': f, 'Distributor': d, 'Period': t,
                        'Flow': x[f][d][t].value(),
                        'Cost': x[f][d][t].value() * data['production_cost'][f]
                    })
    
    if results:
        df = pd.DataFrame(results)
        df.to_csv('supply_chain_results.csv', index=False)
        print(f" Results exported to supply_chain_results.csv")

else:
    print(" No optimal solution found")