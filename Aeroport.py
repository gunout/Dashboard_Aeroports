# dashboard_aeroports_france_corrige.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import random
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Analyse des Aéroports Français - Live",
    page_icon="🛫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(45deg, #0055A4, #EF4135, #FFFFFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .live-badge {
        background: linear-gradient(45deg, #0055A4, #00A3E0);
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #0055A4;
        margin: 0.5rem 0;
    }
    .section-header {
        color: #0055A4;
        border-bottom: 2px solid #0055A4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .airport-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid #0055A4;
        background-color: #f8f9fa;
    }
    .flight-status {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
        font-size: 0.9rem;
    }
    .delayed { background-color: #fff3cd; border-left: 4px solid #ffc107; }
    .on-time { background-color: #d1ecf1; border-left: 4px solid #17a2b8; }
    .cancelled { background-color: #f8d7da; border-left: 4px solid #dc3545; }
</style>
""", unsafe_allow_html=True)

class AeroportsFranceDashboard:
    def __init__(self):
        self.aeroports = self.define_aeroports()
        self.vols_data = self.initialize_vols_data()
        self.traffic_data = self.initialize_traffic_data()
        self.airlines_data = self.initialize_airlines_data()
        
    def define_aeroports(self):
        """Définit les aéroports français majeurs et leurs caractéristiques"""
        return {
            'CDG': {
                'nom_complet': 'Paris Charles de Gaulle',
                'ville': 'Paris',
                'region': 'Île-de-France',
                'code_iata': 'CDG',
                'capacite_passagers': 80_000_000,
                'pistes': 4,
                'terminales': 3,
                'couleur': '#0055A4',
                'latitude': 49.0097,
                'longitude': 2.5479
            },
            'ORY': {
                'nom_complet': 'Paris Orly',
                'ville': 'Paris',
                'region': 'Île-de-France',
                'code_iata': 'ORY',
                'capacite_passagers': 33_000_000,
                'pistes': 3,
                'terminales': 4,
                'couleur': '#EF4135',
                'latitude': 48.7233,
                'longitude': 2.3794
            },
            'NCE': {
                'nom_complet': 'Nice Côte d\'Azur',
                'ville': 'Nice',
                'region': 'Provence-Alpes-Côte d\'Azur',
                'code_iata': 'NCE',
                'capacite_passagers': 14_500_000,
                'pistes': 2,
                'terminales': 2,
                'couleur': '#00A3E0',
                'latitude': 43.6584,
                'longitude': 7.2159
            },
            'LYS': {
                'nom_complet': 'Lyon-Saint Exupéry',
                'ville': 'Lyon',
                'region': 'Auvergne-Rhône-Alpes',
                'code_iata': 'LYS',
                'capacite_passagers': 12_000_000,
                'pistes': 2,
                'terminales': 2,
                'couleur': '#FF6B00',
                'latitude': 45.7256,
                'longitude': 5.0811
            },
            'MRS': {
                'nom_complet': 'Marseille Provence',
                'ville': 'Marseille',
                'region': 'Provence-Alpes-Côte d\'Azur',
                'code_iata': 'MRS',
                'capacite_passagers': 10_200_000,
                'pistes': 2,
                'terminales': 2,
                'couleur': '#009900',
                'latitude': 43.4356,
                'longitude': 5.2136
            },
            'TLS': {
                'nom_complet': 'Toulouse-Blagnac',
                'ville': 'Toulouse',
                'region': 'Occitanie',
                'code_iata': 'TLS',
                'capacite_passagers': 9_600_000,
                'pistes': 2,
                'terminales': 2,
                'couleur': '#660099',
                'latitude': 43.6291,
                'longitude': 1.3638
            },
            'BOD': {
                'nom_complet': 'Bordeaux-Mérignac',
                'ville': 'Bordeaux',
                'region': 'Nouvelle-Aquitaine',
                'code_iata': 'BOD',
                'capacite_passagers': 7_500_000,
                'pistes': 2,
                'terminales': 2,
                'couleur': '#FFCC00',
                'latitude': 44.8283,
                'longitude': -0.7156
            }
        }
    
    def initialize_vols_data(self):
        """Initialise les données des vols en temps réel"""
        compagnies = ['Air France', 'Air France Hop', 'EasyJet', 'Ryanair', 'Transavia', 'British Airways', 'Lufthansa', 'Iberia']
        destinations_francaises = ['CDG', 'ORY', 'NCE', 'LYS', 'MRS', 'TLS', 'BOD', 'NTE', 'LIL', 'BSL']
        destinations_internationales = ['LHR', 'AMS', 'FRA', 'BCN', 'MAD', 'FCO', 'IST', 'DXB', 'JFK', 'CDG']
        
        vols = []
        for i in range(200):  # 200 vols simulés
            aeroport_depart = random.choice(list(self.aeroports.keys()))
            if random.random() > 0.3:  # 70% de vols internationaux
                aeroport_arrivee = random.choice(destinations_internationales)
                type_vol = 'International'
            else:
                aeroport_arrivee = random.choice([a for a in destinations_francaises if a != aeroport_depart])
                type_vol = 'Domestique'
            
            heure_depart = datetime.now() + timedelta(hours=random.randint(-2, 6))
            statut = random.choices(['À l\'heure', 'Retardé', 'Annulé'], weights=[0.7, 0.25, 0.05])[0]
            retard = random.randint(0, 180) if statut == 'Retardé' else 0
            
            vols.append({
                'vol_id': f'{random.choice(["AF", "U2", "FR", "TO", "BA", "LH", "IB"])}{random.randint(1000, 9999)}',
                'compagnie': random.choice(compagnies),
                'aeroport_depart': aeroport_depart,
                'aeroport_arrivee': aeroport_arrivee,
                'heure_depart_programmee': heure_depart,
                'heure_depart_estimee': heure_depart + timedelta(minutes=int(retard)),  # CORRECTION: conversion en int
                'statut': statut,
                'retard_minutes': int(retard),  # CORRECTION: conversion en int
                'porte_embarquement': f'{random.choice(["A", "B", "C", "D", "E"])}{random.randint(1, 50)}',
                'type_vol': type_vol
            })
        
        return pd.DataFrame(vols)
    
    def initialize_traffic_data(self):
        """Initialise les données de trafic historiques"""
        dates = pd.date_range('2020-01-01', datetime.now(), freq='M')
        data = []
        
        for date in dates:
            for code, info in self.aeroports.items():
                # Base de passagers pré-COVID
                base_passagers = info['capacite_passagers'] * 0.7  # 70% de capacité utilisée
                
                # Impact COVID (2020-2021)
                if date.year == 2020:
                    covid_impact = random.uniform(0.2, 0.4)  # Réduction de 60-80%
                elif date.year == 2021:
                    covid_impact = random.uniform(0.4, 0.7)  # Réduction de 30-60%
                elif date.year == 2022:
                    covid_impact = random.uniform(0.7, 0.9)  # Réduction de 10-30%
                else:
                    covid_impact = random.uniform(0.9, 1.1)  # Récupération
                
                # Saisonnalité
                if date.month in [6, 7, 8]:  # Été
                    saison_factor = 1.2
                elif date.month in [12, 1]:  # Hiver (fêtes)
                    saison_factor = 1.1
                else:
                    saison_factor = 1.0
                
                passagers_mois = base_passagers / 12 * covid_impact * saison_factor * random.uniform(0.95, 1.05)
                
                data.append({
                    'date': date,
                    'aeroport': code,
                    'passagers': passagers_mois,
                    'region': info['region'],
                    'vols_mois': random.randint(5000, 50000),
                    'taux_remplissage': random.uniform(0.6, 0.95)
                })
        
        return pd.DataFrame(data)
    
    def initialize_airlines_data(self):
        """Initialise les données des compagnies aériennes"""
        compagnies = {
            'Air France': {'pays': 'France', 'part_marche': 45, 'couleur': '#0055A4'},
            'EasyJet': {'pays': 'Royaume-Uni', 'part_marche': 18, 'couleur': '#FF6600'},
            'Ryanair': {'pays': 'Irlande', 'part_marche': 15, 'couleur': '#FFCC00'},
            'Transavia': {'pays': 'France', 'part_marche': 8, 'couleur': '#EF4135'},
            'Air France Hop': {'pays': 'France', 'part_marche': 6, 'couleur': '#00A3E0'},
            'British Airways': {'pays': 'Royaume-Uni', 'part_marche': 3, 'couleur': '#660099'},
            'Lufthansa': {'pays': 'Allemagne', 'part_marche': 2, 'couleur': '#FF0000'},
            'Autres': {'pays': 'Divers', 'part_marche': 3, 'couleur': '#999999'}
        }
        
        data = []
        for compagnie, info in compagnies.items():
            data.append({
                'compagnie': compagnie,
                'pays': info['pays'],
                'part_marche': info['part_marche'],
                'couleur': info['couleur'],
                'vols_jour': random.randint(50, 500),
                'passagers_an': random.randint(1000000, 15000000)
            })
        
        return pd.DataFrame(data)
    
    def update_live_data(self):
        """Met à jour les données en temps réel"""
        # CORRECTION: Conversion explicite des numpy.int64 en int natif
        for idx in self.vols_data.index:
            if random.random() < 0.1:  # 10% de chance de changement de statut
                nouveaux_statuts = ['À l\'heure', 'Retardé', 'Annulé']
                poids = [0.6, 0.35, 0.05]
                nouveau_statut = random.choices(nouveaux_statuts, weights=poids)[0]
                
                self.vols_data.loc[idx, 'statut'] = nouveau_statut
                if nouveau_statut == 'Retardé':
                    # CORRECTION: Conversion en int natif
                    retard_minutes = int(random.randint(5, 120))
                    self.vols_data.loc[idx, 'retard_minutes'] = retard_minutes
                    self.vols_data.loc[idx, 'heure_depart_estimee'] = (
                        self.vols_data.loc[idx, 'heure_depart_programmee'] + 
                        timedelta(minutes=retard_minutes)  # Utilisation de l'int natif
                    )
                else:
                    self.vols_data.loc[idx, 'retard_minutes'] = 0
                    self.vols_data.loc[idx, 'heure_depart_estimee'] = self.vols_data.loc[idx, 'heure_depart_programmee']
    
    def display_header(self):
        """Affiche l'en-tête du dashboard"""
        st.markdown('<h1 class="main-header">🛫 Analyse des Aéroports Français - Live</h1>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="live-badge">🔴 DONNÉES EN TEMPS RÉEL - MISES À JOUR CONTINUES</div>', 
                       unsafe_allow_html=True)
            st.markdown("**Surveillance en direct du trafic aérien français et analyse des performances**")
        
        current_time = datetime.now().strftime('%H:%M:%S')
        st.sidebar.markdown(f"**🕐 Dernière mise à jour: {current_time}**")
    
    def display_key_metrics(self):
        """Affiche les métriques clés du trafic aérien"""
        st.markdown('<h3 class="section-header">📊 INDICATEURS CLÉS DU TRAFIC AÉRIEN</h3>', 
                   unsafe_allow_html=True)
        
        # Calcul des métriques en temps réel
        vols_aujourdhui = len(self.vols_data)
        vols_retardes = len(self.vols_data[self.vols_data['statut'] == 'Retardé'])
        vols_annules = len(self.vols_data[self.vols_data['statut'] == 'Annulé'])
        taux_ponctualite = ((vols_aujourdhui - vols_retardes - vols_annules) / vols_aujourdhui * 100) if vols_aujourdhui > 0 else 0
        
        # Estimation des passagers aujourd'hui
        passagers_estimes = int(self.traffic_data['passagers'].mean() / 30)  # Moyenne mensuelle divisée par 30
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Vols Programmés Aujourd'hui",
                f"{vols_aujourdhui}",
                f"{random.randint(-5, 10)} vs hier"
            )
        
        with col2:
            st.metric(
                "Taux de Ponctualité",
                f"{taux_ponctualite:.1f}%",
                f"{random.uniform(-2, 3):.1f}% vs hier"
            )
        
        with col3:
            st.metric(
                "Vols Retardés",
                f"{vols_retardes}",
                f"{random.randint(-3, 5)} vs hier",
                delta_color="inverse"
            )
        
        with col4:
            st.metric(
                "Passagers Estimés Aujourd'hui",
                f"{passagers_estimes:,}",
                f"{random.randint(1000, 5000)} vs hier"
            )
    
    def create_aeroports_overview(self):
        """Crée la vue d'ensemble des aéroports"""
        st.markdown('<h3 class="section-header">🏛️ VUE D\'ENSEMBLE DES AÉROPORTS</h3>', 
                   unsafe_allow_html=True)
        
        # Dernières données de trafic
        latest_traffic = self.traffic_data[self.traffic_data['date'] == self.traffic_data['date'].max()]
        
        tab1, tab2, tab3, tab4 = st.tabs(["Trafic Passagers", "Performance Opérationnelle", "Carte Interactive", "Détails par Aéroport"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Trafic passagers par aéroport
                fig = px.bar(latest_traffic, 
                            x='aeroport', 
                            y='passagers',
                            title='Trafic Mensuel des Passagers par Aéroport',
                            color='aeroport',
                            color_discrete_map={code: info['couleur'] for code, info in self.aeroports.items()})
                fig.update_layout(xaxis_title="Aéroport", yaxis_title="Passagers")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Répartition par région
                region_traffic = latest_traffic.groupby('region')['passagers'].sum().reset_index()
                fig = px.pie(region_traffic, 
                            values='passagers', 
                            names='region',
                            title='Répartition du Trafic par Région')
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                # Taux de remplissage
                fig = px.bar(latest_traffic, 
                            x='aeroport', 
                            y='taux_remplissage',
                            title='Taux de Remplissage par Aéroport (%)',
                            color='aeroport',
                            color_discrete_map={code: info['couleur'] for code, info in self.aeroports.items()})
                fig.update_layout(yaxis_tickformat='.0%')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Nombre de vols par mois
                fig = px.bar(latest_traffic, 
                            x='aeroport', 
                            y='vols_mois',
                            title='Nombre de Vols par Mois',
                            color='aeroport',
                            color_discrete_map={code: info['couleur'] for code, info in self.aeroports.items()})
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Carte des aéroports français
            map_data = []
            for code, info in self.aeroports.items():
                airport_traffic = latest_traffic[latest_traffic['aeroport'] == code]
                map_data.append({
                    'aeroport': code,
                    'nom': info['nom_complet'],
                    'latitude': info['latitude'],
                    'longitude': info['longitude'],
                    'passagers': airport_traffic['passagers'].iloc[0] if len(airport_traffic) > 0 else 0,
                    'region': info['region'],
                    'taille': info['capacite_passagers'] / 1000000  # Taille relative
                })
            
            df_map = pd.DataFrame(map_data)
            
            fig = px.scatter_mapbox(df_map, 
                                  lat="latitude", 
                                  lon="longitude", 
                                  size="taille",
                                  color="region",
                                  hover_name="nom",
                                  hover_data={"passagers": True, "region": True},
                                  size_max=30,
                                  zoom=5,
                                  title="Carte des Aéroports Français")
            
            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, height=600)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            # Tableau détaillé des aéroports
            airport_details = []
            for code, info in self.aeroports.items():
                airport_traffic = latest_traffic[latest_traffic['aeroport'] == code]
                airport_flights = self.vols_data[self.vols_data['aeroport_depart'] == code]
                
                if len(airport_traffic) > 0 and len(airport_flights) > 0:
                    # CORRECTION: Conversion en int natif pour l'affichage
                    retard_moyen = float(airport_flights['retard_minutes'].mean())
                    airport_details.append({
                        'Aéroport': info['nom_complet'],
                        'Code IATA': code,
                        'Région': info['region'],
                        'Passagers Mensuels': f"{airport_traffic['passagers'].iloc[0]:,.0f}",
                        'Taux Remplissage': f"{airport_traffic['taux_remplissage'].iloc[0]:.1%}",
                        'Vols Aujourd\'hui': len(airport_flights),
                        'Retard Moyen (min)': f"{retard_moyen:.1f}",
                        'Pistes': info['pistes'],
                        'Terminaux': info['terminales']
                    })
            
            st.dataframe(pd.DataFrame(airport_details), use_container_width=True)
    
    def create_vols_live(self):
        """Affiche les vols en temps réel"""
        st.markdown('<h3 class="section-header">✈️ VOLS EN TEMPS RÉEL</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Tableau des Vols", "Statistiques Temps Réel", "Analyse des Retards"])
        
        with tab1:
            # Filtres pour les vols
            col1, col2, col3 = st.columns(3)
            with col1:
                aeroport_filtre = st.selectbox("Aéroport de départ:", 
                                             ['Tous'] + list(self.aeroports.keys()))
            with col2:
                statut_filtre = st.selectbox("Statut:", 
                                           ['Tous', 'À l\'heure', 'Retardé', 'Annulé'])
            with col3:
                type_vol_filtre = st.selectbox("Type de vol:", 
                                             ['Tous', 'Domestique', 'International'])
            
            # Application des filtres
            vols_filtres = self.vols_data.copy()
            if aeroport_filtre != 'Tous':
                vols_filtres = vols_filtres[vols_filtres['aeroport_depart'] == aeroport_filtre]
            if statut_filtre != 'Tous':
                vols_filtres = vols_filtres[vols_filtres['statut'] == statut_filtre]
            if type_vol_filtre != 'Tous':
                vols_filtres = vols_filtres[vols_filtres['type_vol'] == type_vol_filtre]
            
            # Affichage des vols
            for _, vol in vols_filtres.iterrows():
                status_class = ""
                if vol['statut'] == 'Retardé':
                    status_class = "delayed"
                elif vol['statut'] == 'À l\'heure':
                    status_class = "on-time"
                elif vol['statut'] == 'Annulé':
                    status_class = "cancelled"
                
                col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
                with col1:
                    st.markdown(f"**{vol['vol_id']}**")
                with col2:
                    st.markdown(f"**{vol['compagnie']}**")
                    st.markdown(f"{self.aeroports[vol['aeroport_depart']]['nom_complet']} → {vol['aeroport_arrivee']}")
                with col3:
                    heure_prog = vol['heure_depart_programmee'].strftime('%H:%M')
                    if vol['statut'] == 'Retardé':
                        heure_est = vol['heure_depart_estimee'].strftime('%H:%M')
                        # CORRECTION: Conversion en int natif
                        retard_minutes = int(vol['retard_minutes'])
                        st.markdown(f"**{heure_prog}** → {heure_est} (+{retard_minutes}min)")
                    else:
                        st.markdown(f"**{heure_prog}**")
                with col4:
                    st.markdown(f"<div class='flight-status {status_class}'>{vol['statut']}</div>", 
                               unsafe_allow_html=True)
                
                st.markdown("---")
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                # Répartition des statuts
                status_counts = self.vols_data['statut'].value_counts()
                fig = px.pie(values=status_counts.values, 
                            names=status_counts.index,
                            title='Répartition des Statuts de Vol')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Retards par compagnie
                delays_by_airline = self.vols_data[self.vols_data['statut'] == 'Retardé'].groupby('compagnie')['retard_minutes'].mean().reset_index()
                # CORRECTION: Conversion en float pour Plotly
                delays_by_airline['retard_minutes'] = delays_by_airline['retard_minutes'].astype(float)
                fig = px.bar(delays_by_airline, 
                            x='compagnie', 
                            y='retard_minutes',
                            title='Retard Moyen par Compagnie (minutes)',
                            color='retard_minutes',
                            color_continuous_scale='Reds')
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                # Retards par aéroport
                delays_by_airport = self.vols_data[self.vols_data['statut'] == 'Retardé'].groupby('aeroport_depart')['retard_minutes'].mean().reset_index()
                # CORRECTION: Conversion en float pour Plotly
                delays_by_airport['retard_minutes'] = delays_by_airport['retard_minutes'].astype(float)
                fig = px.bar(delays_by_airport, 
                            x='aeroport_depart', 
                            y='retard_minutes',
                            title='Retard Moyen par Aéroport de Départ (minutes)',
                            color='aeroport_depart',
                            color_discrete_map={code: info['couleur'] for code, info in self.aeroports.items()})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Distribution des retards
                # CORRECTION: Conversion en list native
                retards = self.vols_data[self.vols_data['statut'] == 'Retardé']['retard_minutes'].tolist()
                fig = px.histogram(x=retards, 
                                  nbins=20,
                                  title='Distribution des Durées de Retard',
                                  labels={'x': 'Minutes de retard'})
                st.plotly_chart(fig, use_container_width=True)
    
    def create_compagnies_analysis(self):
        """Analyse des compagnies aériennes"""
        st.markdown('<h3 class="section-header">🏢 ANALYSE DES COMPAGNIES AÉRIENNES</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Parts de Marché", "Performance", "Destinations"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Parts de marché
                fig = px.pie(self.airlines_data, 
                            values='part_marche', 
                            names='compagnie',
                            title='Parts de Marché des Compagnies Aériennes en France',
                            color='compagnie',
                            color_discrete_map={row['compagnie']: row['couleur'] for _, row in self.airlines_data.iterrows()})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Vols par jour
                fig = px.bar(self.airlines_data, 
                            x='compagnie', 
                            y='vols_jour',
                            title='Nombre de Vols Quotidiens par Compagnie',
                            color='compagnie',
                            color_discrete_map={row['compagnie']: row['couleur'] for _, row in self.airlines_data.iterrows()})
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Performance des compagnies
            performance_data = []
            for compagnie in self.airlines_data['compagnie']:
                vols_compagnie = self.vols_data[self.vols_data['compagnie'] == compagnie]
                if len(vols_compagnie) > 0:
                    # CORRECTION: Conversions en types natifs
                    taux_ponctualite = float(len(vols_compagnie[vols_compagnie['statut'] == 'À l\'heure']) / len(vols_compagnie) * 100)
                    retard_moyen = float(vols_compagnie['retard_minutes'].mean())
                    taux_annulation = float(len(vols_compagnie[vols_compagnie['statut'] == 'Annulé']) / len(vols_compagnie) * 100)
                    
                    performance_data.append({
                        'compagnie': compagnie,
                        'taux_ponctualite': taux_ponctualite,
                        'retard_moyen': retard_moyen,
                        'taux_annulation': taux_annulation
                    })
            
            df_performance = pd.DataFrame(performance_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(df_performance, 
                            x='compagnie', 
                            y='taux_ponctualite',
                            title='Taux de Ponctualité par Compagnie (%)',
                            color='taux_ponctualite',
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(df_performance, 
                            x='compagnie', 
                            y='taux_annulation',
                            title='Taux d\'Annulation par Compagnie (%)',
                            color='taux_annulation',
                            color_continuous_scale='Reds')
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Destinations populaires
            destinations_counts = self.vols_data['aeroport_arrivee'].value_counts().head(15).reset_index()
            destinations_counts.columns = ['destination', 'nombre_vols']
            
            fig = px.bar(destinations_counts, 
                        x='nombre_vols', 
                        y='destination',
                        orientation='h',
                        title='Top 15 des Destinations depuis la France',
                        color='nombre_vols',
                        color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)
    
    def create_evolution_analysis(self):
        """Analyse de l'évolution du trafic"""
        st.markdown('<h3 class="section-header">📈 ÉVOLUTION DU TRAFIC</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Évolution Temporelle", "Impact COVID-19", "Projections"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Évolution du trafic total
                total_traffic = self.traffic_data.groupby('date')['passagers'].sum().reset_index()
                fig = px.line(total_traffic, 
                             x='date', 
                             y='passagers',
                             title='Évolution du Trafic Aérien Total en France')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Évolution par aéroport
                fig = px.line(self.traffic_data, 
                             x='date', 
                             y='passagers',
                             color='aeroport',
                             title='Évolution du Trafic par Aéroport',
                             color_discrete_map={code: info['couleur'] for code, info in self.aeroports.items()})
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Analyse de l'impact COVID
            covid_period = self.traffic_data[
                (self.traffic_data['date'] >= '2020-01-01') & 
                (self.traffic_data['date'] <= '2022-12-31')
            ]
            
            # Calcul de la variation par rapport à 2019
            traffic_2019 = self.traffic_data[
                (self.traffic_data['date'] >= '2019-01-01') & 
                (self.traffic_data['date'] <= '2019-12-31')
            ]['passagers'].mean()
            
            covid_period['variation_vs_2019'] = (covid_period['passagers'] - traffic_2019) / traffic_2019 * 100
            
            fig = px.line(covid_period, 
                         x='date', 
                         y='variation_vs_2019',
                         color='aeroport',
                         title='Impact COVID-19: Variation du Trafic vs 2019 (%)',
                         color_discrete_map={code: info['couleur'] for code, info in self.aeroports.items()})
            fig.add_hline(y=0, line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Projections
            st.subheader("Projections 2024-2025")
            
            # Simulation de projections basées sur les tendances
            last_date = self.traffic_data['date'].max()
            future_dates = pd.date_range(start=last_date + timedelta(days=30), periods=12, freq='M')
            
            projection_data = []
            for aeroport in self.aeroports.keys():
                last_traffic = self.traffic_data[self.traffic_data['aeroport'] == aeroport].iloc[-1]['passagers']
                growth_rate = random.uniform(0.02, 0.05)  # Croissance de 2-5% par mois
                
                for i, date in enumerate(future_dates):
                    projected_traffic = last_traffic * (1 + growth_rate) ** (i + 1)
                    projection_data.append({
                        'date': date,
                        'aeroport': aeroport,
                        'passagers': projected_traffic,
                        'type': 'Projection'
                    })
            
            df_projection = pd.DataFrame(projection_data)
            
            # Combiner avec données historiques
            historical = self.traffic_data[self.traffic_data['date'] >= '2023-01-01'].copy()
            historical['type'] = 'Historique'
            combined_data = pd.concat([historical, df_projection])
            
            fig = px.line(combined_data, 
                         x='date', 
                         y='passagers',
                         color='aeroport',
                         line_dash='type',
                         title='Projection du Trafic 2024-2025',
                         color_discrete_map={code: info['couleur'] for code, info in self.aeroports.items()})
            st.plotly_chart(fig, use_container_width=True)
    
    def create_sidebar(self):
        """Crée la sidebar avec les contrôles"""
        st.sidebar.markdown("## 🎛️ CONTRÔLES D'ANALYSE")
        
        # Filtres temporels
        st.sidebar.markdown("### 📅 Période d'analyse")
        date_debut = st.sidebar.date_input("Date de début", 
                                         value=datetime.now() - timedelta(days=30))
        date_fin = st.sidebar.date_input("Date de fin", 
                                       value=datetime.now())
        
        # Filtres aéroports
        st.sidebar.markdown("### 🏛️ Sélection des aéroports")
        aeroports_selectionnes = st.sidebar.multiselect(
            "Aéroports à afficher:",
            list(self.aeroports.keys()),
            default=list(self.aeroports.keys())[:3]
        )
        
        # Options d'affichage
        st.sidebar.markdown("### ⚙️ Options")
        auto_refresh = st.sidebar.checkbox("Rafraîchissement automatique", value=True)
        show_projections = st.sidebar.checkbox("Afficher les projections", value=True)
        
        # Bouton de rafraîchissement manuel
        if st.sidebar.button("🔄 Rafraîchir les données"):
            self.update_live_data()
            st.rerun()
        
        return {
            'date_debut': date_debut,
            'date_fin': date_fin,
            'aeroports_selectionnes': aeroports_selectionnes,
            'auto_refresh': auto_refresh,
            'show_projections': show_projections
        }

    def run_dashboard(self):
        """Exécute le dashboard complet"""
        # Mise à jour des données live
        self.update_live_data()
        
        # Sidebar
        controls = self.create_sidebar()
        
        # Header
        self.display_header()
        
        # Métriques clés
        self.display_key_metrics()
        
        # Navigation par onglets
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🏛️ Aéroports", 
            "✈️ Vols Live", 
            "🏢 Compagnies", 
            "📈 Évolution", 
            "📊 Insights",
            "ℹ️ À Propos"
        ])
        
        with tab1:
            self.create_aeroports_overview()
        
        with tab2:
            self.create_vols_live()
        
        with tab3:
            self.create_compagnies_analysis()
        
        with tab4:
            self.create_evolution_analysis()
        
        with tab5:
            st.markdown("## 📊 INSIGHTS STRATÉGIQUES")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 🎯 TENDANCES DU MARCHÉ
                
                **📈 Croissance Post-COVID:**
                - Récupération complète du trafic en 2024
                - Croissance moyenne de 4-6% par mois
                - Augmentation de la demande pour les vols domestiques
                
                **🌍 Évolution des Destinations:**
                - Augmentation des vols vers l'Asie
                - Croissance des destinations soleil (Méditerranée, Caraïbes)
                - Développement des vols cargo
                
                **💼 Modèles Économiques:**
                - Compétition accrue sur les prix
                - Développement des services premium
                - Digitalisation des processus
                """)
            
            with col2:
                st.markdown("""
                ### 🚨 DÉFIS OPÉRATIONNELS
                
                **⚡ Capacité Aéroportuaire:**
                - Saturation aux heures de pointe à CDG et ORY
                - Besoin d'extension des terminaux
                - Optimisation des processus de sécurité
                
                **🌫️ Impact Environnemental:**
                - Pression réglementaire croissante
                - Développement des carburants durables
                - Optimisation des trajectoires de vol
                
                **🔧 Maintenance Infrastructure:**
                - Modernisation des équipements
                - Gestion des travaux d'entretien
                - Adaptation aux nouvelles normes
                """)
            
            st.markdown("""
            ### 💡 RECOMMANDATIONS STRATÉGIQUES
            
            1. **Investissement Infrastructure:** Modernisation des terminaux et pistes
            2. **Digitalisation:** Développement des services sans contact
            3. **Développement Durable:** Transition vers l'aviation verte
            4. **Expansion:** Ouverture de nouvelles destinations stratégiques
            5. **Optimisation:** Amélioration de la ponctualité et réduction des retards
            """)
        
        with tab6:
            st.markdown("## 📋 À propos de ce dashboard")
            st.markdown("""
            Ce dashboard présente une analyse en temps réel du trafic aérien français 
            et des performances des aéroports.
            
            **Méthodologie :**
            - Données basées sur les statistiques officielles et modèles prédictifs
            - Mises à jour quotidiennes avec variations réalistes
            - Analyse multidimensionnelle (trafic, ponctualité, performance)
            
            **Aéroports couverts :**
            - Paris Charles de Gaulle (CDG)
            - Paris Orly (ORY)
            - Nice Côte d'Azur (NCE)
            - Lyon-Saint Exupéry (LYS)
            - Marseille Provence (MRS)
            - Toulouse-Blagnac (TLS)
            - Bordeaux-Mérignac (BOD)
            
            **⚠️ Note :** Les données sont simulées pour la démonstration. 
            Dans un contexte réel, elles proviendraient de sources officielles (DGAC, Aéroports de Paris, etc.)
            
            **🔒 Confidentialité:** Toutes les données des vols sont simulées et anonymisées.
            """)
        
        # Rafraîchissement automatique
        if controls['auto_refresh']:
            time.sleep(30)  # Rafraîchissement toutes les 30 secondes
            st.rerun()

# Lancement du dashboard
if __name__ == "__main__":
    dashboard = AeroportsFranceDashboard()
    dashboard.run_dashboard()