# Supply Chain Optimization Template

A clean, concise template for multi-echelon supply chain optimization using linear programming.

## Overview

This template provides a mathematical framework for optimizing supply chain flows, inventory levels, and costs across multiple suppliers, intermediaries, and customers over multiple time periods.

## Features

- **Multi-echelon network**: Suppliers → Distributors → Retailers
- **Multi-period planning**: Time-based optimization
- **Cost minimization**: Production, transportation, inventory, and waste costs
- **Inventory management**: Balance equations with waste handling
- **Flexible structure**: Easy to adapt for different industries

## Quick Start

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your network dimensions**:
   ```python
   F = 6  # Number of suppliers
   D = 6  # Number of distributors  
   R = 6  # Number of retailers
   T = 10 # Number of time periods
   ```

5. **Run the template**:
   ```python
   python supply_chain_template.py
   ```

## Customization Guide

### 1. Change Network Dimensions

Update the constants at the top of the file:

```python
F = your_num_suppliers
D = your_num_intermediaries  
R = your_num_customers
T = your_planning_periods
```

### 2. Replace Data Loading

Modify the `load_data()` function to load your actual data:

```python
def load_data():
    # Load demand from CSV
    demand_df = pd.read_csv('your_demand.csv')
    data['demand'] = demand_df.values.tolist()
    
    # Load costs from your files
    cost_df = pd.read_csv('your_costs.csv')
    data['production_cost'] = cost_df['unit_cost'].tolist()
    
    # Load distances/transport costs
    data['transport_fd'] = your_distance_matrix
    
    return data
```

### 3. Modify Constraints

Add or modify constraints based on your business rules:

```python
# Example: Add minimum order quantity
for f in suppliers:
    for d in distributors:
        for t in time_periods:
            model += x[f][d][t] >= 50  # Minimum 50 units per order

# Example: Add vehicle capacity constraints
for f in suppliers:
    for t in time_periods:
        model += lpSum(x[f][d][t] for d in distributors) <= vehicle_capacity

# Example: Add storage space limits
for d in distributors:
    for t in time_periods:
        model += I_dist[d][t] <= warehouse_capacity[d]
```

### 4. Customize Objective Function

Add or remove cost components:

```python
model += (
    # Existing costs...
    
    # Add setup costs
    + lpSum(setup_cost[f] * binary_var[f][t] for f in suppliers for t in time_periods)
    
    # Add carbon footprint penalty
    + lpSum(carbon_factor[f] * x[f][d][t] for f in suppliers for d in distributors for t in time_periods)
    
    # Change to profit maximization
    # - lpSum(revenue[r][t] * sales[r][t] for r in retailers for t in time_periods)
)
```

## Industry-Specific Adaptations

### Manufacturing Supply Chain
```python
# Network: Plants → Warehouses → Stores  
suppliers = plants = range(P)
distributors = warehouses = range(W)
retailers = stores = range(S)

# Add: Setup costs, production capacities, quality constraints
```

### Food/Perishables Supply Chain
```python
# Network: Farms → Processing Centers → Supermarkets
suppliers = farms = range(F)
distributors = processing_centers = range(C)
retailers = supermarkets = range(M)

# Add: Temperature requirements, expiration tracking, freshness constraints
```

### Pharmaceutical Supply Chain
```python
# Network: Manufacturers → Wholesalers → Pharmacies
suppliers = manufacturers = range(M)
distributors = wholesalers = range(W)
retailers = pharmacies = range(P)

# Add: Regulatory compliance, batch tracking, cold chain requirements
```

### E-commerce/Retail Supply Chain
```python
# Network: Vendors → Distribution Centers → Customers
suppliers = vendors = range(V)
distributors = fulfillment_centers = range(FC)
retailers = customer_zones = range(CZ)

# Add: Seasonal demand, promotional planning, last-mile delivery costs
```

## Data Structure Requirements

### Demand Data Format
```python
# demand[retailer][time_period] = demand_amount
demand = [
    [100, 120, 110, 95, ...],  # Retailer 0 demand across periods
    [150, 140, 160, 135, ...], # Retailer 1 demand across periods
    ...
]
```

### Cost Parameters Format
```python
data = {
    'demand': demand_matrix,
    'capacity': capacity_matrix,
    'production_cost': [cost_per_supplier],
    'transport_fd': [[distance_supplier_to_dist]],
    'transport_dr': [[distance_dist_to_retailer]],
    'storage_cost_dist': unit_storage_cost,
    'waste_cost_dist': unit_waste_cost,
    'shelf_life_limit': max_inventory_level
}
```

## Example Use Cases

### Basic Cost Minimization
- Minimize total supply chain costs
- Meet all customer demand  
- Respect supplier capacities
- Track inventory levels

### Advanced Scenarios
- **Service Level Optimization**: Add constraints for minimum service levels
- **Risk Management**: Include supplier reliability factors
- **Sustainability**: Add carbon footprint or environmental constraints
- **Multi-Objective**: Balance cost vs. service level vs. environmental impact

## Output and Results

The template generates:
- **Optimal flows**: Supplier → Distributor → Retailer for each time period
- **Inventory levels**: Stock levels at each location and time
- **Total cost**: Breakdown by cost component
- **CSV export**: Detailed results for further analysis

## Extensions and Advanced Features

### Add Binary Variables
```python
# For facility selection or setup decisions
binary_var = LpVariable.dicts("Setup", (suppliers, time_periods), cat='Binary')
```

### Add Multi-Product Support
```python
# Extend all variables with product dimension
x = LpVariable.dicts("Flow", (suppliers, distributors, products, time_periods), lowBound=0)
```

### Add Stochastic Demand
```python
# Use scenario-based optimization for uncertain demand
for scenario in scenarios:
    for r in retailers:
        for t in time_periods:
            model += lpSum(y[d][r][t] for d in distributors) >= demand_scenario[scenario][r][t]
```

## Troubleshooting

### Common Issues
1. **Infeasible Solution**: Check if total capacity >= total demand
2. **Unbounded Solution**: Ensure all variables have appropriate bounds
3. **Long Solve Time**: Consider reducing network size or time periods for testing

### Performance Tips
- Start with smaller network sizes (F=2, D=2, R=2, T=3)
- Use commercial solvers (Gurobi, CPLEX) for large problems
- Consider problem decomposition for very large networks

## Contributing

This template is designed to be easily customizable. Feel free to:
- Add industry-specific constraints
- Implement additional objective functions
- Create specialized data loading functions
- Add visualization and reporting features

## License

Open source - feel free to use and modify for your supply chain optimization needs.