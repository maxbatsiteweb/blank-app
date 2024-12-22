import streamlit as st
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
def validate_pace_format(pace_str):
    pattern = r'^\d{1,2}:\d{2}$'  # Regex pour "MM:SS"
    return bool(re.match(pattern, pace_str))

# Référence fixe
REFERENCE_PACE = "04:00"  # 4:00 / km

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
        
        # Saisie de l'allure
        real_pace = st.text_input(f"Allure réelle ({categories[i]}) MM:SS / km", key=f"real_pace_{i}")
        
        # Validation et calcul
        if real_pace:
            if validate_pace_format(real_pace):
                real_pace_seconds = pace_to_seconds(real_pace)  # Convertit l'allure réelle en secondes
                performance_index = calculate_performance_index(real_pace_seconds, pace_to_seconds(REFERENCE_PACE))  # Calcul indice de performance
                
                # Affichage des résultats
                st.write(f"Allure réelle : {real_pace} / km")
                st.write(f"Allure de référence : {REFERENCE_PACE} / km")
                st.write(f"Indice de performance : {performance_index} / 100")

                # Ajout des résultats dans un dictionnaire pour calculer les graphiques globaux
                inputs[categories[i]] = performance_index

                # Jauge horizontale individuelle
                st.progress(int(performance_index))
            else:
                st.error("Veuillez entrer l'allure au format MM:SS.")
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
