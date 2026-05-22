import sys
import os
import dash
import pandas as pd
from dash import dcc, html, Input, Output
import plotly.express as px

# Ensure python can locate your 'utils' folder cleanly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ==============================================================================
# 1. DATA LOADING & INITIALIZATION
# ==============================================================================
from utils.data_loader import load_market_data

df = load_market_data()

# Clean trailing spaces from all column headers
df.columns = df.columns.str.strip()

# Extract columns 
ticker_col = 'ticker'
asset_col = 'asset_class'
ret_col = 'return_1w_pct'
vol_col = 'volatility_30d_ann'

# Force conversion of missing or text cells to clean numeric values
df[ret_col] = pd.to_numeric(df[ret_col], errors='coerce')
df[vol_col] = pd.to_numeric(df[vol_col], errors='coerce')

# Drop items missing performance or risk records to protect the plots
df = df.dropna(subset=[ret_col, vol_col])

# Cast categorical grouping column for backend sorting speed
df[asset_col] = df[asset_col].astype('category')
df = df.copy() 

# Create the sorted unique options directly from your dataset column
unique_assets = sorted(list(df[asset_col].unique()))

# ==============================================================================
# 2. INITIALIZE DASH APP
# ==============================================================================
app = dash.Dash(__name__)

# ==============================================================================
# 3. APP LAYOUT
# ==============================================================================
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '20px', 'backgroundColor': '#f9f9f9'}, children=[ 
    
    html.H1("Cross-Asset Risk & Market Intelligence", style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'}), 
    
    # Control Panel Filters Row 
    html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '30px', 'justifyContent': 'center'}, children=[ 
        
        # Dropdown 1: Broad Asset Class Selector
        html.Div(style={'width': '30%'}, children=[ 
            html.Label("1. Select Asset Class Grouping:", style={'fontWeight': 'bold', 'color': '#34495e'}), 
            dcc.Dropdown( 
                id='asset-dropdown', 
                options=[{'label': i, 'value': i} for i in unique_assets], 
                value=unique_assets[0] if unique_assets else None, # FIXED: Safely passes a single string to start up
                clearable=False 
            ) 
        ]), 
        
        # Dropdown 2: Dynamic Cascading Ticker Selector
        html.Div(style={'width': '30%'}, children=[ 
            html.Label("2. Select Specific Ticker to Highlight:", style={'fontWeight': 'bold', 'color': '#34495e'}), 
            dcc.Dropdown(id='ticker-dropdown', clearable=False) 
        ]) 
    ]),
    
    # Graphs Layout Grid
    html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px'}, children=[
        # Chart 1 Container
        html.Div(style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
            dcc.Graph(id='timeline-chart')
        ]),
        # Chart 2 Container
        html.Div(style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
            dcc.Graph(id='scatter-chart')
        ])
    ])
])

# ==============================================================================
# 4. APP INTERACTIVE CALLBACKS
# ==============================================================================

# Callback 1: Dynamically filters the ticker choices based on the selected Asset Class
@app.callback(
    [Output('ticker-dropdown', 'options'),
     Output('ticker-dropdown', 'value')],
    Input('asset-dropdown', 'value')
)
def update_ticker_options(selected_asset):
    if not selected_asset:
        return [], None
        
    filtered_df = df[df[asset_col] == selected_asset]
    tickers = sorted(filtered_df[ticker_col].unique()) if ticker_col in filtered_df.columns else []
    
    options = [{'label': t, 'value': t} for t in tickers]
    default_ticker = tickers[0] if tickers else None # Default to the first alphabetical ticker string
    
    return options, default_ticker

# Callback 2: Redraws both peer-comparison charts based on the dropdown targets
@app.callback(
    [Output('timeline-chart', 'figure'),
     Output('scatter-chart', 'figure')],
    [Input('asset-dropdown', 'value'),
     Input('ticker-dropdown', 'value')]
)
def update_graphs(selected_asset, selected_ticker):
    if not selected_ticker or not selected_asset:
        return px.scatter(title="Select criteria to update data metrics"), px.scatter(title="Select criteria to update data metrics")
        
    peer_df = df[df[asset_col] == selected_asset].copy()
    if peer_df.empty:
        return px.scatter(title="No data found"), px.scatter(title="No data found")
    
    # Color-highlight the single selected asset against its peers
    peer_df['Focus'] = peer_df[ticker_col].apply(
        lambda x: f"Selected ({selected_ticker})" if str(x).strip() == str(selected_ticker).strip() else "Peers"
    )
    
    # CHART 1: Cross-Sectional Ranking Bar Chart (Top 20 Leaderboard)
    top_peers = peer_df.sort_values(by=ret_col, ascending=False).head(20)
    timeline_fig = px.bar(
        top_peers, 
        x=ticker_col, 
        y=ret_col, 
        color='Focus',
        color_discrete_map={f"Selected ({selected_ticker})": "#e74c3c", "Peers": "#34495e"},
        labels={ticker_col: 'Asset Symbol', ret_col: '1-Week % Return Performance'},
        title=f"Top 20 Tickers in {selected_asset} by Weekly Gains",
        template='plotly_white'
    )
    timeline_fig.update_layout(
        xaxis_tickangle=-45, 
        margin={'l': 50, 'b': 80, 't': 50, 'r': 20},
        title={
            'text': f"Top 20 Tickers in {selected_asset} by Weekly Gains",
            'font': {'size': 14}
        }
    )
    
    # CHART 2: Risk-Return Matrix Scatter Plot (The Investment Efficient Frontier)
    scatter_fig = px.scatter(
        peer_df, 
        x=vol_col, 
        y=ret_col, 
        color='Focus', 
        hover_name='longName',
        color_discrete_map={f"Selected ({selected_ticker})": "#e74c3c", "Peers": "#3498db"},
        labels={vol_col: '30-Day Market Volatility Risk Factor', ret_col: '1-Week % Return Reward'},
        title=f"Risk vs. Reward Landscape: {selected_asset} Cluster Peer Universe",
        template='plotly_white'
    )
    # Style tweaks for polished visual appeal
    scatter_fig.update_traces(marker=dict(size=14, line=dict(width=1, color='DarkSlateGrey')))
    scatter_fig.update_layout(
        margin={'l': 65, 'b': 65, 't': 50, 'r': 20},
        title={
            'text': f"Risk vs. Reward Landscape: {selected_asset} Cluster Peer Universe",
            'font': {'size': 14}
        }
    )
    
    return timeline_fig, scatter_fig


# ==============================================================================
# 5. RUN SERVER
# ==============================================================================
if __name__ == '__main__':
    app.run(debug=True)