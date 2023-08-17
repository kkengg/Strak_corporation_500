import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly
from plotly.subplots import make_subplots


# Load the data
stark_sh_url = 'https://raw.githubusercontent.com/kkengg/Strak_corporation_500/main/stark_sh.csv'
stark_sh_data = pd.read_csv(stark_sh_url)

incomecom_url = 'https://raw.githubusercontent.com/kkengg/Strak_corporation_500/main/incomecom.csv'
incomecom_data = pd.read_csv(incomecom_url)

income_url = 'https://raw.githubusercontent.com/kkengg/Strak_corporation_500/main/income.csv'
income_data = pd.read_csv(income_url)

financial_url = 'https://raw.githubusercontent.com/kkengg/Strak_corporation_500/main/financial.csv'
financial_data = pd.read_csv(financial_url)
#financial_data['year'] = financial_data['year'] + 4  # Convert year from 2560 to 2564

capacity_url = 'https://raw.githubusercontent.com/kkengg/Strak_corporation_500/main/capacity.csv'
capacity_data = pd.read_csv(capacity_url)


# Convert 'sh' column to numeric
stark_sh_data['sh'] = pd.to_numeric(stark_sh_data['sh'], errors='coerce')

colors = plotly.colors.qualitative.Prism

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.H1("Horizontal Stacked Bar Chart Example"),
    
    dcc.Graph(id='stacked-bar-chart'),
    dcc.Graph(id='grouped-bar-chart-incomecom'),
    dcc.Graph(id='stacked-bar-chart-income'),
    dcc.Graph(id='grouped-bar-chart-financial'),
    dcc.Graph(id='filtered-bar-chart-capacity'),
    dcc.Graph(id='combined-chart'), 
        
    
    ])

# Callback to update the horizontal stacked bar chart
@app.callback(
    Output('stacked-bar-chart', 'figure'),
    Input('stacked-bar-chart', 'relayoutData')
)
def update_stacked_bar_chart(relayoutData):
    fig = px.bar(stark_sh_data, x='sh', y='type',
                 color='name', orientation='h', barmode='stack',
                 text='sh')

    fig.update_traces(textfont_size=12, marker_color=colors, showlegend=False)

    fig.update_layout(title={'text': "Horizontal Stacked Bar Chart",
                             'x': 0.5, 'xanchor': 'center'},
                      title_font_size=30,
                      xaxis_title='Shareholder Percentage',
                      yaxis_title='Type',
                      width=1000, height=600)

    return fig

# Callback to update the grouped bar chart for incomecom.csv
@app.callback(
    Output('grouped-bar-chart-incomecom', 'figure'),
    Input('grouped-bar-chart-incomecom', 'relayoutData')
)
def update_grouped_bar_chart_incomecom(relayoutData):
    fig = px.bar(incomecom_data, x='Year', y='Value', color='type', barmode='group',
                 title='Grouped Bar Chart: Incomecom by Year and Type')
    return fig

# Callback to update the stacked bar chart for income.csv
@app.callback(
    Output('stacked-bar-chart-income', 'figure'),
    Input('stacked-bar-chart-income', 'relayoutData')
)
def update_stacked_bar_chart_income(relayoutData):
    fig = px.bar(income_data, x='year', y='value', color='type', barmode='group',
                 title='Stacked Bar Chart: Income by Year and Type')
    return fig

# Callback to update the grouped bar chart for financial.csv
@app.callback(
    Output('grouped-bar-chart-financial', 'figure'),
    Input('grouped-bar-chart-financial', 'relayoutData')
)
def update_grouped_bar_chart_financial(relayoutData):
    fig = px.bar(financial_data, x='year', y='value', color='type', barmode='group',
                 title='Grouped Bar Chart: Financial by Year and Type')
    return fig

# Callback to update the filtered bar chart for capacity.csv (type = 'capacity')
@app.callback(
    Output('filtered-bar-chart-capacity', 'figure'),
    Input('filtered-bar-chart-capacity', 'relayoutData')
)
def update_filtered_bar_chart_capacity(relayoutData):
    filtered_capacity_data = capacity_data[capacity_data['type'] == 'capacity']
    fig = px.bar(filtered_capacity_data, x='year', y='value', 
                 title='Filtered Bar Chart: Capacity by Year',
                 labels={'year': 'Year', 'value': 'Value'})
    return fig


# Callback to update the combined chart (line chart and bar chart)
@app.callback(
    Output('combined-chart', 'figure'),
    Input('combined-chart', 'relayoutData')
)
def update_combined_chart(relayoutData):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    filtered_capacity_data = capacity_data[capacity_data['type'] == 'capacity']
    filtered_percapacity_data = capacity_data[capacity_data['type'] == 'percapacity']
    
    # Add the bar chart for capacity
    bar_trace = px.bar(x=filtered_capacity_data['year'], y=filtered_capacity_data['value'],
                       labels={'x': 'Year', 'y': 'Capacity'})
    fig.add_trace(bar_trace.data[0])

    # Add the line chart for percapacity
    line_trace = px.line(x=filtered_percapacity_data['year'], y=filtered_percapacity_data['value'],
                         labels={'x': 'Year', 'y': 'Per Capacity'})
    fig.add_trace(line_trace.data[0], secondary_y=True)
    
    fig.update_layout(title='Combined Chart: Capacity and Per Capacity by Year',
                      xaxis=dict(title='Year'),
                      yaxis=dict(title='Capacity', color='blue'),
                      yaxis2=dict(title='Per Capacity', overlaying='y', side='right', color='red'))
    
    return fig




# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
