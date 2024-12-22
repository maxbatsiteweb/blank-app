import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

# Configuration de l'application
st.set_page_config(page_title="Test de Profilage", layout="wide")

# Fonction pour convertir une allure en secondes/km
def pace_to_seconds(pace):
    minutes, seconds = map(int, pace.split(':'))
    return minutes * 60 + seconds

# Fonction pour convertir des secondes/km en allure mm:ss/km
def seconds_to_pace(seconds):
    minutes = seconds // 60
    sec = seconds % 60
    return f"{int(minutes):02}:{int(sec):02}"

# Fonction pour calculer l'indice de performance
def calculate_performance_index(real_pace, reference_pace):
    return min(100, round((pace_to_seconds(reference_pace) / real_pace) * 100, 2))

# Fonction pour ajuster l'allure en fonction de la pente
def adjust_pace_for_slope(real_pace, slope_adjustment):
    return pace_to_seconds(real_pace) + slope_adjustment

# Fonction pour valider le format MM:SS
def validate_time_format(time_str):
    pattern = r'^\d{1,2}:\d{2}$'  # Regex pour "MM:SS" (1 ou 2 chiffres pour MM, exactement 2 chiffres pour SS)
    if re.match(pattern, time_str):
        return True
    else:
        return False

# Références
REFERENCE_PACE = "04:00"  # 4:00 / km
DEFAULT_ADJUSTED_PACE = pace_to_seconds("04:30")  # 4:30 / km

# Titre principal
st.title("Test de Profilage")

# Colonnes pour les trois types de segments
col1, col2, col3 = st.columns(3)

# Champs communs
categories = ["Plat", "Montée", "Descente"]
inputs = {}

for i, col in enumerate([col1, col2, col3]):
    with col:
        st.subheader(categories[i])
        
        # Saisie utilisateur
        distance = st.number_input(f"Distance ({categories[i]}) en km", min_value=0.0, step=0.01, key=f"distance_{i}")
        time = st.text_input(f"Temps ({categories[i]}) MM:SS", key=f"time_{i}")
        slope = st.number_input(f"Pente (%) ({categories[i]})", min_value=-20.0, max_value=20.0, step=0.1, key=f"slope_{i}")
        
        # Validation et calcul
        if time:
            if validate_time_format(time):
                time_seconds = pace_to_seconds(time)  # Convertit le temps en secondes
                if distance > 0:
                    real_pace = round(time_seconds / distance)  # Allure réelle
                    adjusted_pace = adjust_pace_for_slope(real_pace, slope * 2)  # Ajustement avec pente
                    performance_index = calculate_performance_index(real_pace, REFERENCE_PACE)  # Calcul indice de performance

                    # Affichage des résultats
                    st.write(f"Allure réelle : {seconds_to_pace(real_pace)} / km")
                    st.write(f"Allure ajustée à la pente : {seconds_to_pace(adjusted_pace)} / km")
                    st.write(f"Indice de performance : {performance_index} / 100")

                    # Ajout des résultats dans un dictionnaire pour calculer les graphiques globaux
                    inputs[categories[i]] = performance_index

                    # Jauge verticale
                    st.progress(int(performance_index))
                else:
                    st.warning("Veuillez entrer une distance supérieure à 0.")
            else:
                st.error("Veuillez entrer le temps au format MM:SS.")
                inputs[categories[i]] = 0
        else:
            st.write("Veuillez remplir tous les champs pour voir les résultats.")
            inputs[categories[i]] = 0

# Graphique Camembert (anneau)
if all(value > 0 for value in inputs.values()):
    total = sum(inputs.values())
    normalized_scores = [score / total * 100 for score in inputs.values()]
    
    # Création du graphique
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        normalized_scores, 
        labels=categories, 
        autopct='%1.1f%%', 
        startangle=90, 
        wedgeprops=dict(width=0.3)
    )
    ax.set_aspect('equal')
    st.pyplot(fig)
