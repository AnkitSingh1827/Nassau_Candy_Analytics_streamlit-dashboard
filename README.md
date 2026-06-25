# Nassau Candy Dashboard

This project is a Streamlit dashboard for exploring the Nassau Candy Distributor sales file in a simple, visual way. It helps answer questions like:

- Which products make the most profit?
- Which divisions are performing best?
- Where are costs too high compared with sales?
- Which products or factories depend on most of the revenue or profit?

The dashboard reads the CSV file in `data/Nassau Candy Distributor.csv`, cleans it, calculates business metrics, and shows the results across several pages.

## What this project does

The app is built for easy business analysis. It includes:

- A main executive dashboard with high-level sales and profit metrics.
- Global filters that apply across the app.
- Product analysis for top products, product segments, and profit contribution.
- Division analysis for comparing sales, profit, and margin by division.
- Cost diagnostics for finding products with low margins or weak pricing.
- Pareto analysis for spotting products that drive most revenue or profit.
- Factory analysis with charts and a map view.

## Main Filters

Every page uses the same filter panel from the sidebar:

- Date range
- Division selection
- Product search
- Margin threshold

These filters make it easier to focus on a specific time period or business segment without changing pages.

## Project Files

```text
app.py
nassau_utils.py
README.md
requirements.txt
assets/
data/
    Nassau Candy Distributor.csv
pages/
    1_Product_Analysis.py
    2_Division_Analysis.py
    3_Cost_Diagnostics.py
    4_Pareto_Analysis.py
    5_Factory_Analysis.py
```

## Page Guide

### Main dashboard

The main app in `app.py` shows an executive summary with:

- Total sales
- Total profit
- Gross margin
- Number of products
- Best division
- Top product by profit
- Monthly trend charts
- Business recommendations

### Product Analysis

This page focuses on product-level performance. It shows:

- Top products by profit
- Top products by margin
- Product segment tables
- A treemap for profit contribution
- A detailed product table

### Division Analysis

This page compares divisions and shows:

- Best and worst performing divisions
- Revenue vs profit comparison
- Margin by division
- Ranking tables

### Cost Diagnostics

This page highlights products that may need attention. It includes:

- Cost vs sales chart
- Cost vs profit chart
- Products below the selected margin threshold
- Repricing suggestions

### Pareto Analysis

This page helps find concentration risk by showing:

- Products that drive 80% of revenue
- Products that drive 80% of profit
- Cumulative contribution charts
- Pareto tables

### Factory Analysis

This page shows factory-level performance with:

- Profit by factory
- Sales by factory
- Margin by factory
- A map of factory locations
- A factory summary table

## Data Cleaning and Preparation

The shared utility module in `nassau_utils.py` handles the data preparation step. It:

- Cleans text fields and column names.
- Standardizes division names.
- Normalizes product names.
- Converts sales, cost, profit, and units to numeric values.
- Parses order and ship dates.
- Fills missing unit values using product and division medians.
- Removes invalid rows.
- Creates extra columns like gross margin, profit per unit, cost rate, order month, and factory name.

## Key Metrics

The dashboard uses these common formulas:

- Gross Margin % = Gross Profit / Sales * 100
- Profit Per Unit = Gross Profit / Units
- Revenue Contribution % = Sales / Total Sales * 100
- Profit Contribution % = Gross Profit / Total Gross Profit * 100
- Margin Volatility = rolling standard deviation of monthly gross margin

## Factory Mapping

Products are mapped to these factories:

- Lot's O' Nuts
- Wicked Choccy's
- Sugar Shack
- Secret Factory
- The Other Factory
- Unmapped / Other

The factory page uses these names to place markers on the map and to group profit and sales by factory.

## How To Run

1. Open a terminal in the project folder.
2. Install the Python dependencies.

```bash
pip install -r requirements.txt
```

3. Start the dashboard.

```bash
streamlit run app.py
```

If `python` points to the Microsoft Store on Windows, use your installed Python path instead.

## Required Packages

The project uses:

- streamlit
- pandas
- numpy
- plotly
- folium
- streamlit-folium

## Recommended Use

1. Open the main dashboard first.
2. Set the sidebar filters to match the time period or division you want.
3. Open the page tabs to explore product, division, cost, Pareto, and factory views.
4. Use the recommendation section to find the most useful follow-up actions.

## Notes

- Keep the CSV file in `data/Nassau Candy Distributor.csv`.
- The app uses one shared utility module so every page follows the same cleaning and filtering logic.
- On Windows, the real Python interpreter may be at `%LocalAppData%\Programs\Python\Python312\python.exe` if the PATH is not set yet.

- ## 👩‍💻 Author

*Ankit Singh*  
[GitHub](https://github.com/AnkitSingh1827) | [LinkedIn](https://www.linkedin.com/in/ankit-singh257)
