from flask import Flask
import dash
from dash import dcc, html
import pandas as pd
import numpy as np
import plotly.express as px
import requests
from bs4 import BeautifulSoup
from dash.dependencies import Input, Output
import time

# Initialisation de l'application Flask
server = Flask(__name__)

# Initialisation de l'application Dash
app = dash.Dash(__name__, server=server, routes_pathname_prefix='/dashboard/')

# Fonction pour récupérer les cotes en direct depuis PMU.fr
def get_pmu_odds():
    url = "https://www.pmu.fr/turf/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9",
        "Referer": "https://www.google.com/"
    }
    
    try:
        time.sleep(3)  # Pause de 3 secondes pour éviter le blocage

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        horses = []
        odds = []

        for horse in soup.select('.horse-name'):
            horses.append(horse.text.strip())

        for odd in soup.select('.odds-value'):
            odds.append(odd.text.strip())

        if len(horses) == len(odds) and len(horses) > 0:
            return pd.DataFrame({"Horse": horses, "Odds": odds})
        else:
            print("⚠️ Scraping réussi mais aucune donnée récupérée.")
            return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors du scraping de PMU.fr: {e}")
        return pd.DataFrame()

# Fonction de récupération des données
def get_race_data():
    data = get_pmu_odds()
    if data.empty:
        print("⚠️ Impossible de scraper PMU.fr, utilisation des données fictives.")
        return generate_fake_data()
    return data

# Génération de données fictives
def generate_fake_data():
    np.random.seed(42)
    horses = [f"Horse {i}" for i in range(1, 11)]
    odds = np.random.uniform(1.5, 20, size=10)
    bet_amount = np.random.randint(100, 10000, size=10)
    return pd.DataFrame({"Horse": horses, "Odds": odds, "Bets": bet_amount})

# Chargement des données initiales
data = get_race_data()

# Interface Dash
app.layout = html.Div([
    html.H1("PMU AI Predictor"),
    dcc.Graph(id='odds-chart',
              figure=px.bar(data, x='Horse', y='Odds', title='Odds from PMU.fr')),
    dcc.Interval(id='interval-update', interval=60000, n_intervals=0)
])

# Callback pour mise à jour
@app.callback(
    Output('odds-chart', 'figure'),
    Input('interval-update', 'n_intervals')
)
def update_chart(n):
    new_data = get_race_data()
    fig = px.bar(new_data, x='Horse', y='Odds', title='Updated Odds from PMU.fr')
    return fig

# Exposer Flask pour Gunicorn
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
