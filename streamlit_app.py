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

# Fonction pour valider le format MM:SS
def validate_time_format(time_str):
    pattern = r'^\d{1,2}:\d{2}$'  # Regex pour "MM:SS" (1 ou 2 chiffres pour MM, exactement 2 chiffres pour SS)
    if re.match(pattern, time_str):
        return True
    else:
        return False

# Références
REFERENCE_PACE = "04:00"  # 4:00 / km
ADJUSTED_PACE = "05:00"  # Allure ajustée fixe à 5:00 / km

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
                    performance_index = calculate_performance_index(real_pace, REFERENCE_PACE)  # Calcul indice de performance

                    # Affichage des résultats
                    st.write(f"Allure réelle : {seconds_to_pace(real_pace)} / km")
                    st.write(f"Allure ajustée à la pente (test) : {ADJUSTED_PACE} / km")
                    st.write(f"Indice de performance : {performance_index} / 100")

                    # Ajout des résultats dans un dictionnaire pour calculer les graphiques globaux
                    inputs[categories[i]] = performance_index

                    # Jauge horizontale individuelle
                    st.progress(int(performance_index))
                else:
                    st.warning("Veuillez entrer une distance supérieure à 0.")
            else:
                st.error("Veuillez entrer le temps au format MM:SS.")
                inputs[categories[i]] = 0
        else:
            st.write("Veuillez remplir tous les champs pour voir les résultats.")
            inputs[categories[i]] = 0

# Jauge finale globale
if all(value > 0 for value in inputs.values()):
    total = sum(inputs.values())
    normalized_scores = [score / total * 100 for score in inputs.values()]
    
    # Affichage des valeurs par catégorie
    st.subheader("Répartition des performances")
    for category, score in zip(categories, normalized_scores):
        st.write(f"{category} : {round(score, 2)}%")

    # Création de la jauge finale
    st.subheader("Performance globale (Jauge colorée)")
    fig, ax = plt.subplots(figsize=(8, 1))

    # Définir les couleurs et les segments
    colors = ['#4CAF50', '#2196F3', '#FFC107']  # Vert, Bleu, Jaune
    left = 0
    for score, color in zip(normalized_scores, colors):
        ax.barh(0, score, height=0.5, color=color, left=left)
        left += score

    # Ajustements visuels
    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # Afficher la jauge
    st.pyplot(fig)
