from flask import Flask, render_template, jsonify
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.express as px
import requests
from sklearn.ensemble import RandomForestClassifier
from dash.dependencies import Input, Output

# Initialisation de l'application Flask
server = Flask(__name__)

# Initialisation de l'application Dash
app = dash.Dash(__name__, server=server, routes_pathname_prefix='/dashboard/')

# Fonction pour récupérer les données des courses (exemple fictif)
def get_race_data():
    url = "https://api.example.com/race_data"  # Remplace par une API réelle
    response = requests.get(url)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        return pd.DataFrame({})

# Génération de données fictives si aucune API disponible
def generate_fake_data():
    np.random.seed(42)
    horses = [f"Horse {i}" for i in range(1, 11)]
    odds = np.random.uniform(1.5, 20, size=10)
    bet_amount = np.random.randint(100, 10000, size=10)
    race_data = pd.DataFrame({"Horse": horses, "Odds": odds, "Bets": bet_amount})
    return race_data

# Charger les données de course
data = get_race_data()
if data.empty:
    data = generate_fake_data()

# Détection des mouvements de mise suspects
data['Bet Change'] = data['Bets'].pct_change().fillna(0)
data['Suspicious'] = data['Bet Change'].apply(lambda x: True if x > 0.5 else False)

# Création de l'interface Dash
app.layout = html.Div([
    html.H1("PMU AI Predictor"),
    dcc.Graph(id='odds-chart',
              figure=px.bar(data, x='Horse', y='Odds', color='Suspicious', title='Odds and Suspicious Bets')),
    dcc.Interval(id='interval-update', interval=60000, n_intervals=0)
])

# Callback pour mettre à jour le graphique en temps réel
@app.callback(
    Output('odds-chart', 'figure'),
    Input('interval-update', 'n_intervals')
)
def update_chart(n):
    new_data = get_race_data()
    if new_data.empty:
        new_data = generate_fake_data()
    new_data['Bet Change'] = new_data['Bets'].pct_change().fillna(0)
    new_data['Suspicious'] = new_data['Bet Change'].apply(lambda x: True if x > 0.5 else False)
    fig = px.bar(new_data, x='Horse', y='Odds', color='Suspicious', title='Odds and Suspicious Bets')
    return fig

# Lancer l'application Flask
if __name__ == '__main__':
    app.run_server(debug=True)
