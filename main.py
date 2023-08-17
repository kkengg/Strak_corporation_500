import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load the data
loss_url = 'https://raw.githubusercontent.com/kkengg/Strak_corporation_500/main/loss_money.csv'
price_url = 'https://raw.githubusercontent.com/kkengg/Strak_corporation_500/main/price.csv'
timeline_url = 'https://raw.githubusercontent.com/kkengg/Strak_corporation_500/main/Timeline%20Stark.csv'
loss_data = pd.read_csv(loss_url)
price_data = pd.read_csv(price_url)
timeline_data = pd.read_csv(timeline_url)

# Replace '-' with 0 in loss_data
loss_data = loss_data.replace('-', '0')

# Convert relevant columns to numeric
numeric_cols = ['institutional_loan', 'pp', 'bond_value', 'common_stock']
loss_data[numeric_cols] = loss_data[numeric_cols].apply(pd.to_numeric)

# Extract the 'Start Date' and 'REMARK' columns from the timeline_data
timeline_remarks = timeline_data[['Start Date', 'REMARK']]

# Merge the 'price_data' and 'timeline_remarks' based on the 'Date' and 'Start Date' columns
merged_data = pd.merge(price_data, timeline_remarks, left_on='Date', right_on='Start Date', how='left')

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    dcc.Tabs(id='tabs', value='page-1', children=[
        dcc.Tab(label='Page 1', value='page-1'),
        dcc.Tab(label='Page 2', value='page-2'),
    ]),
    html.Div(id='page-content')
])

# Define callback to switch between pages
@app.callback(
    Output('page-content', 'children'),
    [Input('tabs', 'value')]
)
def display_page(tab):
    if tab == 'page-1':
        return html.Div([
            html.H1("Strak Corporation Analysis"),
            
            dcc.RangeSlider(
                id='year-slicer',
                min=loss_data['Year'].min(),
                max=loss_data['Year'].max(),
                step=1,
                marks={str(year): str(year) for year in loss_data['Year'].unique()},
                value=[loss_data['Year'].min(), loss_data['Year'].max()]
            ),
            
            html.Div(id='price-stats', style={'display': 'flex', 'flex-direction': 'column'}),
            
            dcc.Graph(id='area-chart'),
            
            html.Div([
                html.Div(id='new-stats', style={'display': 'inline-block', 'margin-right': '20px'}),
                html.Div(id='sum-stats', style={'display': 'inline-block'}),
            ]),
        ])
    elif tab == 'page-2':
        return html.Div([
            html.H1("Page 2 Content Goes Here")
            # You can add your content for Page 2 here
        ])

# Callback to update the area chart and statistics on Page 1
@app.callback(
    [Output('area-chart', 'figure'), Output('price-stats', 'children'), Output('new-stats', 'children')],
    [Input('year-slicer', 'value')]
)
def update_chart_stats(selected_years):
    filtered_price_data = merged_data[(merged_data['Year'] >= selected_years[0]) & (merged_data['Year'] <= selected_years[1])]
    avg_close = filtered_price_data['Close'].mean()
    avg_growth = filtered_price_data['Growth'].mean()
    avg_volume = filtered_price_data['Volume'].mean()
    
    # Filter loss_data based on selected years
    filtered_loss_data = loss_data[(loss_data['Year'] >= selected_years[0]) & (loss_data['Year'] <= selected_years[1])]
    
    # Calculate the new statistics from the filtered loss_data
    institutional_loan_sum = filtered_loss_data['institutional_loan'].sum()
    pp_sum = filtered_loss_data['pp'].sum()
    bond_value_sum = filtered_loss_data['bond_value'].sum()
    common_stock_sum = filtered_loss_data['common_stock'].sum()
    total_sum = filtered_loss_data.drop(columns=['Year']).sum().sum()
    
    # Create a subplot with two y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add the area chart for 'Close' data with red color and transparency
    fig.add_trace(go.Scatter(x=filtered_price_data['Date'], y=filtered_price_data['Close'], name='Close',
                             fill='tozeroy', fillcolor='rgba(255, 0, 0, 0.52)'))
    
    # Add the 'Volume' data to the secondary y-axis as a filled area (green color and transparency)
    fig.add_trace(go.Scatter(x=filtered_price_data['Date'], y=filtered_price_data['Volume'], name='Volume',
                             line=dict(color='green'), fill='tozeroy', fillcolor='rgba(0, 255, 0, 0.52)'), secondary_y=True)
    
    # Adding annotations (remarks) to the area chart using the 'REMARK' column
    for row in filtered_price_data.itertuples():
        annotation_text = row.REMARK
        if pd.notnull(annotation_text):  # Only add annotation if REMARK is not null
            fig.add_annotation(
                text=annotation_text,
                x=row.Date,
                y=row.Close,
                xanchor='center',
                yanchor='bottom',
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='black',
                font=dict(size=12),
            )
    
    fig.update_layout(
        title='Strak Corporation Analysis',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Close', color='red'),
        yaxis2=dict(title='Volume', overlaying='y', side='right', color='green'),
    )
    
    stats = [
        html.H3(f"Avg Close Price: {avg_close:.2f}"),
        html.H3(f"Avg Growth: {avg_growth:.2f}"),
        html.H3(f"Avg Volume: {avg_volume:.2f}"),
    ]
    
    new_stats = [
        html.H3(f"Total institutional loan: {institutional_loan_sum:.2f}"),
        html.H3(f"Total private placement: {pp_sum:.2f}"),
        html.H3(f"Total bond value: {bond_value_sum:.2f}"),
        html.H3(f"Total common stock value: {common_stock_sum:.2f}"),
    ]
    
    return fig, stats, new_stats

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
