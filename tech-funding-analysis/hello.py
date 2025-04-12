from preswald import (
    text, plotly, connect, get_df, table, sidebar, query,
    selectbox, slider, checkbox, alert, separator
)
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import numpy as np

sidebar()

text("# Tech Funding Analysis (2020-2021)")
text("""
**Business Use Case: Understanding the Investment Landscape**

In the dynamic world of technology, tracking investment flow is vital. This dashboard provides insights into funding trends from early 2020 to mid-2021, aimed at helping venture capitalists identify opportunities, founders benchmark progress, and analysts assess market health. We explore geographical distributions, sector hotspots, stage-specific deal sizes, and key players.
""")

text("""
**Data Source:** Analysis based on the `tech_fundings.csv` dataset, reflecting reported funding rounds. Key fields include Company, Region, Vertical, Funding Amount (USD), Funding Stage, and Funding Date.
""")

connect()
df_raw = get_df('fundings_data')

if df_raw is None:
    alert("Critical Error: Could not load funding data. Please verify the data source configuration in preswald.toml.", level="error")
    sys.exit()

df_cleaned = df_raw.copy()
initial_rows = len(df_cleaned)

columns_to_drop = ['index', 'Website']
existing_columns_to_drop = [col for col in columns_to_drop if col in df_cleaned.columns]
if existing_columns_to_drop:
    df_cleaned = df_cleaned.drop(columns=existing_columns_to_drop)

if 'Funding Amount (USD)' in df_cleaned.columns:
    df_cleaned['Funding Amount (USD)'] = pd.to_numeric(df_cleaned['Funding Amount (USD)'], errors='coerce')
    df_cleaned.dropna(subset=['Funding Amount (USD)'], inplace=True)
else:
    alert("Data Error: Required column 'Funding Amount (USD)' not found or invalid.", level="error")
    sys.exit()

if 'Funding Date' in df_cleaned.columns:
    df_cleaned['Funding Date'] = pd.to_datetime(df_cleaned['Funding Date'], format='%b-%y', errors='coerce')
    df_cleaned.dropna(subset=['Funding Date'], inplace=True)

final_rows = len(df_cleaned)
if final_rows == 0:
    alert("Data Error: No valid data remaining after essential cleaning (amounts/dates).", level="error")
    sys.exit()

alert(f"Data processed: Analyzing {final_rows} valid funding deals.", level="info")

separator()

text("## Overall Funding Landscape: High-Level View")
total_funding = df_cleaned['Funding Amount (USD)'].sum()
average_funding = df_cleaned['Funding Amount (USD)'].mean()
median_funding = df_cleaned['Funding Amount (USD)'].median()

text("These metrics provide a quick pulse check on the overall market activity and typical deal sizes during the period.")
text(f"*   **Total Capital Deployed:** ${total_funding:,.0f}")
text(f"*   **Average Deal Size:** ${average_funding:,.0f} (Sensitive to large outliers)")
text(f"*   **Median Deal Size:** ${median_funding:,.0f} (Represents the 'typical' deal midpoint)")

separator()

text("## Geographic & Sector Insights: Where is the Money Going?")
text("Analyze investment concentration by location and industry vertical. Use sliders to explore beyond the top 10.")

n_regions = slider("Number of Top Regions to Display", min_val=3, max_val=20, step=1, default=10, size=0.5)
n_verticals = slider("Number of Top Verticals to Display", min_val=3, max_val=20, step=1, default=10, size=0.5)

text("### Geographic Hotspots")
text("Understanding regional concentration helps identify established tech hubs and potentially emerging ecosystems.")
if 'Region' in df_cleaned.columns:
    region_funding = df_cleaned.groupby('Region')['Funding Amount (USD)'].sum().nlargest(int(n_regions)).reset_index()
    if not region_funding.empty:
        fig_region = px.bar(region_funding, x='Region', y='Funding Amount (USD)', title=f'Total Funding by Top {int(n_regions)} Regions', labels={'Funding Amount (USD)': 'Total Funding (USD)'}, text_auto='.2s', color='Region', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_region.update_layout(xaxis={'categoryorder':'total descending'}, template='plotly_white', title_x=0.5, showlegend=False)
        plotly(fig_region)

text("### Leading Industry Verticals")
text("Tracking top-funded verticals reveals investor confidence and perceived growth areas within the tech landscape.")
if 'Vertical' in df_cleaned.columns:
    vertical_funding = df_cleaned.groupby('Vertical')['Funding Amount (USD)'].sum().nlargest(int(n_verticals)).reset_index()
    if not vertical_funding.empty:
        vertical_funding['Vertical'] = vertical_funding['Vertical'].str.split(',').str[0].str.strip()
        fig_vertical = px.bar(vertical_funding, x='Vertical', y='Funding Amount (USD)', title=f'Total Funding by Top {int(n_verticals)} Verticals', labels={'Funding Amount (USD)': 'Total Funding (USD)'}, text_auto='.2s', color='Vertical', color_discrete_sequence=px.colors.qualitative.Set3)
        fig_vertical.update_layout(xaxis={'categoryorder':'total descending'}, template='plotly_white', title_x=0.5, showlegend=False)
        plotly(fig_vertical)

separator()

text("## Funding Stage Dynamics: Deal Size & Benchmarks")

text("### How Deal Sizes Vary by Stage")
show_outlier_note = checkbox("Explain outlier exclusion?", default=True, size=1.0)
if show_outlier_note:
    text("This box plot illustrates funding amount ranges per stage (log scale), indicating typical capital needs and valuations at different maturity levels. **Note: Top 0.5% extreme outliers removed for clearer visualization of common ranges.**")
else:
     text("Funding amount ranges per stage (log scale, outliers excluded).")

stage_order = ['Pre-Seed', 'Seed', 'Angel', 'Series A', 'Series B', 'Series C', 'Series D', 'Series E', 'Series F', 'Series G', 'Series H', 'ICO', 'Debt Financing', 'Private Equity', 'Crowdfunding', 'Grant', 'Unknown', 'Undisclosed']
if 'Funding Stage' in df_cleaned.columns:
    cutoff_threshold = df_cleaned['Funding Amount (USD)'].quantile(0.995)
    df_cleaned['Funding Stage Cat'] = pd.Categorical(df_cleaned['Funding Stage'], categories=stage_order, ordered=True)
    df_stage_filtered = df_cleaned.dropna(subset=['Funding Stage Cat'])
    df_plot_data = df_stage_filtered[df_stage_filtered['Funding Amount (USD)'] < cutoff_threshold]
    if not df_plot_data.empty:
        fig_stage = px.box(df_plot_data.sort_values('Funding Stage Cat'), x='Funding Stage Cat', y='Funding Amount (USD)', title='Funding Distribution by Stage (Log Scale, Outliers Excluded)', labels={'Funding Stage Cat': 'Funding Stage', 'Funding Amount (USD)': 'Funding Amount (USD, Log Scale)'}, log_y=True, color='Funding Stage Cat', color_discrete_sequence=px.colors.qualitative.Plotly)
        fig_stage.update_layout(xaxis_title="Funding Stage", template='plotly_white', title_x=0.5, showlegend=False)
        plotly(fig_stage)
    if 'Funding Stage Cat' in df_cleaned.columns:
         df_cleaned = df_cleaned.drop(columns=['Funding Stage Cat'])

text("### Stage-Specific Benchmarks")
text("This table offers quantitative benchmarks (count, total, average, median) per stage, useful for comparing a specific company's round against typical deals at that level.")
if 'Funding Stage' in df_cleaned.columns:
    stage_summary = df_cleaned.groupby('Funding Stage')['Funding Amount (USD)'].agg(['count', 'sum', 'mean', 'median']).reset_index()
    stage_summary.columns = ['Funding Stage', 'Number of Deals', 'Total Funding (USD)', 'Average Funding (USD)', 'Median Funding (USD)']
    stage_order_map = {stage: i for i, stage in enumerate(stage_order)}
    stage_summary['sort_order'] = stage_summary['Funding Stage'].map(stage_order_map)
    stage_summary = stage_summary.sort_values('sort_order', na_position='last').drop(columns=['sort_order'])
    stage_summary['Total Funding (USD)'] = stage_summary['Total Funding (USD)'].apply(lambda x: f"${x:,.0f}")
    stage_summary['Average Funding (USD)'] = stage_summary['Average Funding (USD)'].apply(lambda x: f"${x:,.0f}")
    stage_summary['Median Funding (USD)'] = stage_summary['Median Funding (USD)'].apply(lambda x: f"${x:,.0f}")
    table(stage_summary.reset_index(drop=True), title="Summary Statistics per Funding Stage")

separator()

# --- Section 6: Interactive Exploration & Notable Rounds ---
text("## Regional Deep Dive & Notable Rounds")

text("### Explore Deals by Specific Region")
text("Use the dropdown to focus the deal table on a selected region. This demonstrates interactive filtering using Pandas based on user input.")
if 'Region' in df_cleaned.columns:
    region_options = ['All'] + sorted(df_cleaned['Region'].dropna().astype(str).unique())
    # Use a shorter label for the selectbox
    selected_region = selectbox("Filter by Region:", options=region_options, default='All')

    if selected_region == 'All':
        # Show recent deals instead of top funded when 'All' is selected
        text("Showing 20 most recent deals across all regions:")
        display_df = df_cleaned.nlargest(20, 'Funding Date')
    else:
        text(f"Showing deals for: **{selected_region}**")
        display_df = df_cleaned[df_cleaned['Region'] == selected_region].copy()

    if not display_df.empty:
        display_df_formatted = display_df.copy()
        columns_to_show = ['Company', 'Vertical', 'Funding Amount (USD)', 'Funding Stage', 'Funding Date', 'Region']
        columns_to_show = [col for col in columns_to_show if col in display_df_formatted.columns]
        display_df_formatted = display_df_formatted[columns_to_show]
        if 'Funding Amount (USD)' in display_df_formatted.columns:
             display_df_formatted['Funding Amount (USD)'] = display_df_formatted['Funding Amount (USD)'].apply(lambda x: f"${x:,.0f}")
        if 'Funding Date' in display_df_formatted.columns and pd.api.types.is_datetime64_any_dtype(display_df_formatted['Funding Date']):
             display_df_formatted['Funding Date'] = display_df_formatted['Funding Date'].dt.strftime('%Y-%m-%d')
        table(display_df_formatted.reset_index(drop=True), title=f"Funding Deals for {selected_region}")
    else:
        alert(f"No deals found for the selected region: {selected_region}.", level="warning")


text("### Spotlight: Top 10 Largest Funding Rounds")
text("These represent the most significant capital injections during the period, often highlighting market leaders or 'unicorn' valuations.")
if 'Company' in df_cleaned.columns and 'Funding Date' in df_cleaned.columns:
    columns_to_select = ['Company', 'Funding Amount (USD)', 'Vertical', 'Region', 'Funding Stage']
    is_date_col_valid = pd.api.types.is_datetime64_any_dtype(df_cleaned['Funding Date'])
    if is_date_col_valid:
        columns_to_select.append('Funding Date')
    top_companies = df_cleaned.nlargest(10, 'Funding Amount (USD)')[columns_to_select].reset_index(drop=True)
    top_companies['Funding Amount (USD)'] = top_companies['Funding Amount (USD)'].apply(lambda x: f"${x:,.0f}")
    if 'Funding Date' in top_companies.columns and is_date_col_valid:
        top_companies['Funding Date'] = top_companies['Funding Date'].dt.strftime('%b %Y')
    table(top_companies, title="Top 10 Largest Individual Rounds")


separator()

# --- Section 7: SQL-like Query Demonstration (Seed Stage Deals) ---
text("## Query Example: Seed Stage Deals")
text("Demonstrating the `preswald.query` function to perform SQL-like filtering on the raw data source, focusing on early-stage (Seed) investments.")

# Query for Seed stage deals, selecting relevant columns
sql_seed_deals = """
SELECT
    Company,
    Region,
    Vertical,
    "Funding Amount (USD)",
    "Funding Date"
FROM
    fundings_data
WHERE
    "Funding Stage" = 'Seed'
ORDER BY
    "Funding Amount (USD)" DESC
LIMIT 10
"""
try:
    seed_deals_result = query(sql_seed_deals, 'fundings_data')
    if seed_deals_result is not None and not seed_deals_result.empty:
         table(seed_deals_result, title="Top 10 Largest Seed Deals (Query Example)")
    elif seed_deals_result is not None:
         text("No Seed deals found via query.")
    else:
         alert("Query execution for Seed deals failed.", level="warning")
except Exception as e:
    alert(f"Error executing Seed deals query: {e}", level="error")

separator()

# --- Section 8: Conclusion ---
text("## Summary & Conclusion")
text("""
This dashboard provides a multi-faceted view of the 2020-2021 tech funding environment. Key observations include the dominance of specific geographic hubs and verticals (like B2B Software and AI), and the expected exponential increase in deal size with later funding stages.

Interactive elements allow users to adjust the scope of regional and sector analysis, while the regional filter enables deeper investigation into specific markets. The successful demonstration of filtering Seed stage deals using `preswald.query` confirms the ability to leverage SQL-like operations for targeted data retrieval.

Overall, this analysis offers valuable benchmarks and insights for anyone navigating or observing the technology investment landscape.
""")