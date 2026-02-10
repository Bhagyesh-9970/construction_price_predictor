import pandas as pd
import numpy as np

# Generate 2000 daily dates starting from 2019-01-01
dates = pd.date_range(start="2019-01-01", periods=2000, freq="D")

# Create smooth upward trends with random fluctuations
cement_base = np.linspace(300, 500, 2000) + np.random.normal(0, 3, 2000)
steel_base = np.linspace(50000, 65000, 2000) + np.random.normal(0, 800, 2000)
brick_base = np.linspace(6.5, 9.5, 2000) + np.random.normal(0, 0.1, 2000)
sand_base = np.linspace(800, 1200, 2000) + np.random.normal(0, 15, 2000)

# Create DataFrame
data = pd.DataFrame({
    "Date": dates,
    "Cement_Price": cement_base.round(2),
    "Steel_Price": steel_base.round(2),
    "Brick_Price": brick_base.round(2),
    "Sand_Price": sand_base.round(2)
})

# Add helper column used by models
data["Days_Since_Start"] = (data["Date"] - data["Date"].min()).dt.days

# Save as CSV
data.to_csv("construction_estimates_material_prices.csv", index=False)

print("✅ Dataset with 2000 entries generated successfully!")
print(data.head())
