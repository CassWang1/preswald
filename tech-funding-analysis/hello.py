from preswald import text, plotly, connect, get_df, table, sidebar
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import numpy as np

sidebar()

text("# Tech Funding Analysis (2020-2021)")
text("""
**Business Use Case: Why It Matters and Who It's For**

Understanding the flow of capital in the technology sector is crucial for various stakeholders. Venture capitalists seek emerging trends and promising regions, founders benchmark their progress and identify potential investors, market analysts track sector health, and economic developers gauge regional innovation.

This analysis explores a dataset of technology company funding rounds from early 2020 through mid-2021 to answer key questions:
*   Where is funding geographically concentrated?
*   Which industry verticals are attracting the most capital?
*   What are the typical funding amounts at different stages (Seed, Series A, etc.)?
*   Which companies secured the largest rounds during this period?
*   What are the summary statistics for deals at each funding stage?
""")

text("""
**The Data: Source and Content**

The analysis is based on the `tech_fundings.csv` dataset, representing a snapshot of publicly reported or compiled funding rounds. Key columns include:
*   `Company`: The name of the company receiving funding.
*   `Region`: The geographical location of the company headquarters.
*   `Vertical`: The industry sector the company operates in.
*   `Funding Amount (USD)`: The amount raised in the funding round (converted to USD).
*   `Funding Stage`: The stage of the funding round (e.g., Seed, Series A, Private Equity).
*   `Funding Date`: The approximate date the funding round was announced or closed.
""")

connect()
df = get_df('fundings_data')

if df is None:
    text("Error: Could not load funding data. Please check configuration.")
    sys.exit()

df_cleaned = df.copy()

columns_to_drop = ['index', 'Website']
existing_columns_to_drop = [col for col in columns_to_drop if col in df_cleaned.columns]
if existing_columns_to_drop:
    df_cleaned = df_cleaned.drop(columns=existing_columns_to_drop)

if 'Funding Amount (USD)' in df_cleaned.columns:
    df_cleaned['Funding Amount (USD)'] = pd.to_numeric(df_cleaned['Funding Amount (USD)'], errors='coerce')
    df_cleaned.dropna(subset=['Funding Amount (USD)'], inplace=True)
else:
    text("Error: Required column 'Funding Amount (USD)' not found.")
    sys.exit()

if 'Funding Date' in df_cleaned.columns:
    df_cleaned['Funding Date'] = pd.to_datetime(df_cleaned['Funding Date'], format='%b-%y', errors='coerce')
    df_cleaned.dropna(subset=['Funding Date'], inplace=True)

if df_cleaned.empty:
    text("Error: No valid data remaining after cleaning.")
    sys.exit()


text("## Overall Funding Landscape: Key Metrics")
total_funding = df_cleaned['Funding Amount (USD)'].sum()
average_funding = df_cleaned['Funding Amount (USD)'].mean()
median_funding = df_cleaned['Funding Amount (USD)'].median()
num_deals = len(df_cleaned)

text(f"Based on {num_deals} analyzed deals:")
text(f"*   **Total Funding:** ${total_funding:,.0f}")
text(f"*   **Average Funding per Deal:** ${average_funding:,.0f}")
text(f"*   **Median Funding per Deal:** ${median_funding:,.0f}")


text("## Detailed Analysis & Visualizations")

text("### Geographic Concentration: Funding by Region (Top 10)")
text("This chart highlights the regions attracting the most investment capital, indicating major tech hubs or areas with significant funding activity during this period.")
if 'Region' in df_cleaned.columns:
    region_funding = df_cleaned.groupby('Region')['Funding Amount (USD)'].sum().nlargest(10).reset_index()
    if not region_funding.empty:
        fig_region = px.bar(region_funding,
                            x='Region',
                            y='Funding Amount (USD)',
                            title='Top 10 Regions by Total Funding Amount',
                            labels={'Funding Amount (USD)': 'Total Funding (USD)'},
                            text_auto='.2s',
                            color='Region',
                            color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_region.update_layout(xaxis={'categoryorder':'total descending'}, template='plotly_white', title_x=0.5, showlegend=False)
        plotly(fig_region)

text("### Sector Focus: Funding by Vertical (Top 10)")
text("Identifying the top-funded industry verticals reveals which sectors were perceived as having high growth potential or requiring significant capital investment.")
if 'Vertical' in df_cleaned.columns:
    vertical_funding = df_cleaned.groupby('Vertical')['Funding Amount (USD)'].sum().nlargest(10).reset_index()
    if not vertical_funding.empty:
        vertical_funding['Vertical'] = vertical_funding['Vertical'].str.split(',').str[0].str.strip()
        fig_vertical = px.bar(vertical_funding,
                              x='Vertical',
                              y='Funding Amount (USD)',
                              title='Top 10 Verticals by Total Funding Amount',
                              labels={'Funding Amount (USD)': 'Total Funding (USD)'},
                              text_auto='.2s',
                              color='Vertical',
                              color_discrete_sequence=px.colors.qualitative.Set3)
        fig_vertical.update_layout(xaxis={'categoryorder':'total descending'}, template='plotly_white', title_x=0.5, showlegend=False)
        plotly(fig_vertical)

text("### Deal Size Insights: Funding Amount Distribution by Stage")
text("This box plot shows the range and median funding amount for different investment stages. The logarithmic scale helps visualize the wide variance in deal sizes. **Note: Extreme outliers (top 0.5%) have been excluded for visual clarity.**")
stage_order = ['Pre-Seed', 'Seed', 'Angel', 'Series A', 'Series B', 'Series C', 'Series D', 'Series E', 'Series F', 'Series G', 'Series H', 'ICO', 'Debt Financing', 'Private Equity', 'Crowdfunding', 'Grant', 'Unknown', 'Undisclosed']
if 'Funding Stage' in df_cleaned.columns:
    cutoff_threshold = df_cleaned['Funding Amount (USD)'].quantile(0.995)
    df_cleaned['Funding Stage Cat'] = pd.Categorical(df_cleaned['Funding Stage'], categories=stage_order, ordered=True)
    df_stage_filtered = df_cleaned.dropna(subset=['Funding Stage Cat'])
    df_plot_data = df_stage_filtered[df_stage_filtered['Funding Amount (USD)'] < cutoff_threshold]

    if not df_plot_data.empty:
        fig_stage = px.box(df_plot_data.sort_values('Funding Stage Cat'),
                       x='Funding Stage Cat',
                       y='Funding Amount (USD)',
                       title='Funding Amount Distribution by Stage (Log Scale, Outliers Excluded)',
                       labels={'Funding Stage Cat': 'Funding Stage', 'Funding Amount (USD)': 'Funding Amount (USD, Log Scale)'},
                       log_y=True,
                       color='Funding Stage Cat',
                       color_discrete_sequence=px.colors.qualitative.Plotly)
        fig_stage.update_layout(xaxis_title="Funding Stage", template='plotly_white', title_x=0.5, showlegend=False)
        plotly(fig_stage)
    else:
        text("No data available for box plot after filtering outliers.")

    if 'Funding Stage Cat' in df_cleaned.columns:
         df_cleaned = df_cleaned.drop(columns=['Funding Stage Cat'])


text("### Notable Rounds: Top 10 Funded Companies")
text("Highlighting the companies that secured the largest individual funding rounds during this period provides insight into significant market players and potentially disruptive technologies.")
if 'Company' in df_cleaned.columns and 'Funding Date' in df_cleaned.columns:
    columns_to_select = ['Company', 'Funding Amount (USD)', 'Vertical', 'Region', 'Funding Stage']
    is_date_col_valid = pd.api.types.is_datetime64_any_dtype(df_cleaned['Funding Date'])
    if is_date_col_valid:
        columns_to_select.append('Funding Date')
    top_companies = df_cleaned.nlargest(10, 'Funding Amount (USD)')[columns_to_select].reset_index(drop=True)
    top_companies['Funding Amount (USD)'] = top_companies['Funding Amount (USD)'].apply(lambda x: f"${x:,.0f}")
    if 'Funding Date' in top_companies.columns and is_date_col_valid:
        top_companies['Funding Date'] = top_companies['Funding Date'].dt.strftime('%b %Y')
    table(top_companies, title="Top 10 Largest Funding Rounds")

text("### Benchmarking Deals: Funding Statistics by Stage")
text("This table provides quantitative benchmarks (deal count, total, average, median funding) for each funding stage, useful for comparing specific deals against industry norms.")
if 'Funding Stage' in df_cleaned.columns:
    stage_summary = df_cleaned.groupby('Funding Stage')['Funding Amount (USD)'].agg(
        ['count', 'sum', 'mean', 'median']
    ).reset_index()
    stage_summary.columns = ['Funding Stage', 'Number of Deals', 'Total Funding (USD)', 'Average Funding (USD)', 'Median Funding (USD)']
    stage_order_map = {stage: i for i, stage in enumerate(stage_order)}
    stage_summary['sort_order'] = stage_summary['Funding Stage'].map(stage_order_map)
    stage_summary = stage_summary.sort_values('sort_order', na_position='last').drop(columns=['sort_order'])
    stage_summary['Total Funding (USD)'] = stage_summary['Total Funding (USD)'].apply(lambda x: f"${x:,.0f}")
    stage_summary['Average Funding (USD)'] = stage_summary['Average Funding (USD)'].apply(lambda x: f"${x:,.0f}")
    stage_summary['Median Funding (USD)'] = stage_summary['Median Funding (USD)'].apply(lambda x: f"${x:,.0f}")
    table(stage_summary.reset_index(drop=True), title="Summary Statistics per Funding Stage")


text("## Summary of Insights")
text("""
This analysis reveals several key aspects of the tech funding landscape during 2020-2021:
*   **Geographic Focus:** Funding remains heavily concentrated in specific regions (e.g., US, specific European countries).
*   **Sector Preferences:** Certain verticals like B2B Software, AI, and Fintech consistently attracted substantial investment.
*   **Stage Dynamics:** While there is a wide disparity in funding amounts across stages, the bulk of deals (excluding extreme outliers) show clearer progression when visualized without the highest-value rounds compressing the scale.
*   **Major Players:** A handful of companies secured exceptionally large funding rounds, often dominating the headlines and total capital raised.
*   **Stage Benchmarks:** The summary statistics provide a baseline for evaluating deal sizes relative to the stage norms observed in this dataset.
""")