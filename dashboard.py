# dashboard.py
import datetime
import pandas as pd
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
from firebase_config import db
from firebase_admin import firestore

layout = html.Div([
    html.H1("Dashboard Reseau  local - Donnes Cloud", style={'textAlign': 'center'}),
    html.Button(" Actualiser", id="refresh-btn", n_clicks=0,
                style={'margin': '10px', 'padding': '10px 20px'}),
    html.Div(id='gauges-container', style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center'}),
    html.Div(id='graphs-container', style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center'}),
    dcc.Interval(id='interval-component', interval=30*1000, n_intervals=0),
    html.Div(id='last-updated', style={'textAlign': 'center', 'marginTop': '20px'})
])

def register_callbacks(app):
    @app.callback(
        [Output('gauges-container', 'children'),
         Output('graphs-container', 'children'),
         Output('last-updated', 'children')],
        [Input('refresh-btn', 'n_clicks'),
         Input('interval-component', 'n_intervals')]
    )
    def update_dashboard(n_clicks, n_intervals):
        try:
            # Get last 200 documents from Firebase history collection
            docs = db.collection("donne_dh11_history")\
                     .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                     .limit(200).stream()

            data = [doc.to_dict() for doc in docs]
            if not data:
                return [], [], "Aucune donne"

            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            # Convert to numeric
            for col in ['temperature', 'humidite']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Drop invalid rows
            df = df.dropna(subset=['temperature', 'humidite'])
            df = df.sort_values('timestamp')

            gauges, graphs = [], []

            for field in ['temperature', 'humidite']:
                topic_data = df[['timestamp', field]].copy()
                topic_data.rename(columns={field: 'value'}, inplace=True)

                last_value = topic_data['value'].iloc[-1]
                display_name = field.capitalize()

                # Gauge
                gauges.append(dcc.Graph(
                    figure=go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=last_value,
                        title={"text": display_name},
                        gauge={'axis': {'range': [0, topic_data['value'].max() * 1.1]},
                               'bar': {'color': "green"}}
                    )),
                    style={'width': '400px', 'margin': '20px'}
                ))

                # Graph
                y_min = topic_data['value'].min()
                y_max = topic_data['value'].max()
                margin = (y_max - y_min) * 0.1 if (y_max - y_min) > 0 else 1

                graphs.append(dcc.Graph(
                    figure=go.Figure(go.Scatter(
                        x=topic_data['timestamp'],
                        y=topic_data['value'],
                        mode='lines+markers',
                        line=dict(width=3)
                    )).update_layout(
                        title=display_name,
                        height=400,
                        yaxis=dict(range=[y_min - margin, y_max + margin]),
                        margin=dict(t=50, b=50)
                    ),
                    style={'width': '48%', 'margin': '15px'}
                ))

            last_updated = f"Dernire mise  jour: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            return gauges, graphs, last_updated

        except Exception as e:
            return [], [], f"Erreur: {e}"
