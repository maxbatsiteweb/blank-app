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
        ref_pace = st.text_input(f"Allure de Référence ({categories[i]}) MM:SS", key=f"ref_pace_{i}")
        slope = st.number_input(f"Pente (%) ({categories[i]})", min_value=-20.0, max_value=20.0, step=0.1, key=f"slope_{i}")
        
        # Validation et calcul
        if time and ref_pace:
            if validate_time_format(time) and validate_time_format(ref_pace):
                time_seconds = pace_to_seconds(time)  # Convertit le temps en secondes
                ref_pace_seconds = pace_to_seconds(ref_pace)  # Convertit l'allure de référence en secondes
                if distance > 0:
                    real_pace = round(time_seconds / distance)  # Allure réelle
                    performance_index = calculate_performance_index(real_pace, ref_pace_seconds)  # Calcul indice de performance

                    # Affichage des résultats
                    st.write(f"Allure réelle : {seconds_to_pace(real_pace)} / km")
                    st.write(f"Indice de performance : {performance_index} / 100")

                    # Ajout des résultats dans un dictionnaire pour calculer les graphiques globaux
                    inputs[categories[i]] = performance_index

                    # Jauge horizontale individuelle
                    st.progress(int(performance_index))
                else:
                    st.warning("Veuillez entrer une distance supérieure à 0.")
            else:
                st.error("Veuillez entrer le temps et l'allure de référence au format MM:SS.")
                inputs[categories[i]] = 0
        else:
            st.write("Veuillez remplir tous les champs pour voir les résultats.")
            inputs[categories[i]] = 0

# Jauge finale globale
if all(value > 0 for value in inputs.values()):
    total = sum(inputs.values())
    normalized_scores = [score / total * 100 for score in inputs.values()]
    
    # Création de la jauge finale
    st.subheader("Performance globale (Jauge colorée)")
    fig, ax = plt.subplots(figsize=(10, 0.5))

    # Définir les couleurs et les segments
    colors = ['#4CAF50', '#2196F3', '#FFC107']  # Vert, Bleu, Jaune
    left = 0
    for score, color, category in zip(normalized_scores, colors, categories):
        ax.barh(0, score, height=0.2, color=color, left=left, edgecolor='black')
        # Ajouter du texte dans la jauge
        ax.text(left + score / 2, 0, f"{category} {round(score, 1)}%", 
                va='center', ha='center', color='white', fontsize=10, fontweight='bold')
        left += score

    # Ajustements visuels
    ax.set_xlim(0, 100)
    ax.axis('off')  # Supprime tous les axes

    # Afficher la jauge
    st.pyplot(fig)
