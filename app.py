import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime
import yfinance as yf
from prophet import Prophet
import plotly.graph_objects as go
import flask

app = dash.Dash(__name__)
server = app.server
colors = {
    'background': '#191414',
    'text': '#466ec3'
}
assets_path = os.path.join(os.getcwd(), 'assets')

# CSS stylesheets
stylesheets = ['style.css']
app.layout = html.Div(
    style={'backgroundColor': colors['background'], 'fontFamily': "Sulphur Point, sans-serif", 'width': '100%', 'height': '100vh', 'margin': '0px', 'display': 'flex', 'flexDirection': 'column'},
    children=[
        html.Meta(
            name='viewport',
            content='width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no',
        ),
        html.Title("BlackGem AI Forecast"),
        html.H1(
            children='BlackGem AI Stock Forecast',
            style={
                'textAlign': 'center',
                'color': colors['text'],
                'fontSize': '4rem',
                'marginTop': '2rem',
            }
        ),

        html.Div(
            children='Stock price forecasting chart for the next 90 days.',
            style={
                'textAlign': 'center',
                'color': colors['text'],
                'fontSize': '1.5rem',
                'marginTop': '1rem',
            }
        ),

        html.Div(
            className='form-control',
            children=[
                dcc.Input(
                    id='input_symbol',
                    type='text',
                    value='COIN',
                    required='required'
                ),
                html.Label(
                    [
                        html.Span('Enter a stock symbol:', style={'transition-delay': '0ms'}),
                    ],
                    style={'color': colors['text'], 'fontSize': '1.5rem'}
                )
            ]
        ),
        # Submit Button
        html.Button(
            id='submit_button',
            n_clicks=0,
            children='Scan',
            className='form-control',  # Added CSS class name
        ),

        html.Div(
            style={'flex': '1'},
            children=[
                dcc.Loading(
                    id="loading",
                    type="circle",
                    children=[
                        # Plotly stock graph
                        dcc.Graph(
                            id='graph_scatter',
                        )
                    ]
                )
            ]
        )
    ]
)

@app.callback(
    Output('graph_scatter', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('input_symbol', 'value')]
)
def update_scatter(n_clicks, symbol):
    if n_clicks == 0:
        ticker_data = yf.Ticker('COIN')
        df = ticker_data.history(period='1d', start=datetime(2015, 1, 1), end=datetime.now())
    else:
        ticker_data = yf.Ticker(symbol)
        df = ticker_data.history(period='1d', start=datetime(2015, 1, 1), end=datetime.now())

    prophet_df = df.reset_index()[["Date", "Close"]]
    prophet_df.columns = ["ds", "y"]

    # Remove timezone from the "ds" column
    prophet_df["ds"] = prophet_df["ds"].dt.tz_localize(None)

    m = Prophet()
    m.fit(prophet_df)
    future = m.make_future_dataframe(periods=90)
    forecast = m.predict(future)
    forecast1 = forecast.set_index("ds")[datetime.now():].copy()

    historic = go.Scatter(
        x=df.index,
        y=df["Close"],
        name="Data values",
        line=dict(color='#80ed99')
    )

    yhat = go.Scatter(
        x=forecast1.index,
        y=forecast1["yhat"],
        mode='lines',
        name="Forecast",
        line=dict(color='#fb8500')
    )

    yhat_upper = go.Scatter(
        x=forecast1.index,
        y=forecast1["yhat_upper"],
        mode='lines',
        fill="tonexty",
        line={"color": "#2f2f2f"},
        name="Higher uncertainty interval"
    )

    yhat_lower = go.Scatter(
        x=forecast1.index,
        y=forecast1["yhat_lower"],
        mode='lines',
        fill="tonexty",
        line={"color": "#2f2f2f"},
        name="Lower uncertainty interval"
    )

    data = [historic, yhat, yhat_upper, yhat_lower]

    figure = {
        'data': data,
        'layout': {
            'title': f"{symbol} closing value",
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': '#ffffff',
                'size': 18,
                'family': 'Sulphur Point, sans-serif'
            }
        }
    }

    return figure


@app.server.route('/assets/<path:path>')
def serve_assets(path):
    return flask.send_from_directory(assets_path, path)


if __name__ == '__main__':
    app.run_server(debug=False)
