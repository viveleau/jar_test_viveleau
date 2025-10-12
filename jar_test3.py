import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
import json
import sqlite3
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# Configuration de la page
st.set_page_config(
    page_title="Rapport Jar Test",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2e86ab;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .result-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2f77b4;
        margin: 1rem 0;
    }
    .config-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
    }
    .table-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        overflow-x: auto;
    }
</style>
""", unsafe_allow_html=True)

class DatabaseManager:
    def __init__(self):
        self.db_file = "jar_test_database.db"
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mesures_jar_test (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_test TEXT,
                operateur TEXT,
                site_prelevement TEXT,
                type_eau TEXT,
                volume_echantillon REAL,
                temps_coagulation INTEGER,
                vitesse_coagulation INTEGER,
                temps_floculation INTEGER,
                vitesse_floculation INTEGER,
                combinaison TEXT,
                essai INTEGER,
                coagulant_ml REAL,
                floculant_ml REAL,
                dco_entree REAL,
                ph_entree REAL,
                dco_sortie REAL,
                ph_sortie REAL,
                v_boue REAL,
                turbidite TEXT,
                abattement REAL,
                turbidite_entree REAL,
                turbidite_sortie REAL,
                couleur_entree REAL,
                couleur_sortie REAL,
                mes_entree REAL,
                mes_sortie REAL,
                uv254_entree REAL,
                uv254_sortie REAL,
                aluminium_residuel REAL,
                fer_residuel REAL,
                conductivite_entree REAL,
                conductivite_sortie REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_mesure(self, data):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO mesures_jar_test (
                date_test, operateur, site_prelevement, type_eau, volume_echantillon,
                temps_coagulation, vitesse_coagulation, temps_floculation, vitesse_floculation,
                combinaison, essai, coagulant_ml, floculant_ml, dco_entree, ph_entree,
                dco_sortie, ph_sortie, v_boue, turbidite, abattement, turbidite_entree,
                turbidite_sortie, couleur_entree, couleur_sortie, mes_entree, mes_sortie,
                uv254_entree, uv254_sortie, aluminium_residuel, fer_residuel,
                conductivite_entree, conductivite_sortie
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['date_test'], data['operateur'], data['site_prelevement'], data['type_eau'],
            data['volume_echantillon'], data['temps_coagulation'], data['vitesse_coagulation'],
            data['temps_floculation'], data['vitesse_floculation'], data['combinaison'],
            data['essai'], data['coagulant_ml'], data['floculant_ml'], data['dco_entree'],
            data['ph_entree'], data['dco_sortie'], data['ph_sortie'], data['v_boue'],
            data['turbidite'], data['abattement'], data['turbidite_entree'],
            data['turbidite_sortie'], data['couleur_entree'], data['couleur_sortie'],
            data['mes_entree'], data['mes_sortie'], data['uv254_entree'], data['uv254_sortie'],
            data['aluminium_residuel'], data['fer_residuel'], data['conductivite_entree'],
            data['conductivite_sortie']
        ))
        
        conn.commit()
        conn.close()
    
    def get_all_mesures(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM mesures_jar_test ORDER BY created_at DESC')
        results = cursor.fetchall()
        
        columns = [description[0] for description in cursor.description]
        conn.close()
        
        return pd.DataFrame(results, columns=columns)

class ConfigManager:
    def __init__(self):
        self.coagulants_file = "coagulants_config.json"
        self.floculants_file = "floculants_config.json"
        self.parametres_file = "parametres_config.json"
    
    def load_coagulants(self):
        try:
            with open(self.coagulants_file, 'r') as f:
                coagulants = json.load(f)
            if coagulants and coagulants[0]["nom"] != "Aucun":
                for i, coag in enumerate(coagulants):
                    if coag["nom"] == "Aucun":
                        coagulants.insert(0, coagulants.pop(i))
                        break
                else:
                    coagulants.insert(0, {
                        "nom": "Aucun",
                        "dilution": 1.0,
                        "densite": 1.0,
                        "matiere_active": 100.00,
                        "prix_kg": 0.00
                    })
            return coagulants
        except:
            return [
                {
                    "nom": "Aucun",
                    "dilution": 1.0,
                    "densite": 1.0,
                    "matiere_active": 100.00,
                    "prix_kg": 0.00
                },
                {
                    "nom": "Chlorure ferrique (FeCl3)",
                    "dilution": 1.0,
                    "densite": 1.45,
                    "matiere_active": 40.00,
                    "prix_kg": 0.85
                },
                {
                    "nom": "Sulfate d'aluminium (Al2(SO4)3)",
                    "dilution": 1.0,
                    "densite": 1.33,
                    "matiere_active": 48.0,
                    "prix_kg": 0.65
                },
                {
                    "nom": "PAC (PolyAluminium Chlorure)",
                    "dilution": 1.0,
                    "densite": 1.33,
                    "matiere_active": 70.00,
                    "prix_kg": 1.20
                },
                {
                    "nom": "Sulfate ferreux (FeSO4)",
                    "dilution": 1.0,
                    "densite": 1.28,
                    "matiere_active": 35.0,
                    "prix_kg": 0.45
                },
                {
                    "nom": "Chaux (Ca(OH)2)",
                    "dilution": 1.0,
                    "densite": 1.2,
                    "matiere_active": 85.0,
                    "prix_kg": 0.25
                }
            ]
    
    def save_coagulants(self, data):
        with open(self.coagulants_file, 'w') as f:
            json.dump(data, f, indent=4)
    
    def load_floculants(self):
        try:
            with open(self.floculants_file, 'r') as f:
                floculants = json.load(f)
            if floculants and floculants[0]["nom"] != "Aucun":
                for i, floc in enumerate(floculants):
                    if floc["nom"] == "Aucun":
                        floculants.insert(0, floculants.pop(i))
                        break
                else:
                    floculants.insert(0, {
                        "nom": "Aucun",
                        "type": "Liquide",
                        "dilution": 1.0,
                        "densite": 1.0,
                        "matiere_active": 100.00,
                        "prix_kg": 0.00
                    })
            return floculants
        except:
            return [
                {
                    "nom": "Aucun",
                    "type": "Liquide",
                    "dilution": 1.0,
                    "densite": 1.0,
                    "matiere_active": 100.00,
                    "prix_kg": 0.00
                },
                {
                    "nom": "Polyacrylamide anionique",
                    "type": "Solide",
                    "dilution": 0.1,
                    "densite": 1.0,
                    "matiere_active": 90.00,
                    "prix_kg": 12.5
                },
                {
                    "nom": "Polyacrylamide cationique",
                    "type": "Solide",
                    "dilution": 0.1,
                    "densite": 1.0,
                    "matiere_active": 90.00,
                    "prix_kg": 14.0
                },
                {
                    "nom": "PolyDADMAC",
                    "type": "Liquide",
                    "dilution": 1.0,
                    "densite": 1.1,
                    "matiere_active": 40.00,
                    "prix_kg": 3.2
                },
                {
                    "nom": "Chitosan",
                    "type": "Solide",
                    "dilution": 0.5,
                    "densite": 1.0,
                    "matiere_active": 85.0,
                    "prix_kg": 45.0
                },
                {
                    "nom": "Alginate de sodium",
                    "type": "Solide",
                    "dilution": 0.5,
                    "densite": 1.0,
                    "matiere_active": 95.0,
                    "prix_kg": 28.0
                }
            ]
    
    def save_floculants(self, data):
        with open(self.floculants_file, 'w') as f:
            json.dump(data, f, indent=4)
    
    def load_parametres(self):
        try:
            with open(self.parametres_file, 'r') as f:
                return json.load(f)
        except:
            return {
                "parametres_mesures": ["Turbidité", "Couleur", "pH", "Conductivité", "MES", "UV254", "Aluminium résiduel", "Fer résiduel", "DCO"],
                "parametres_selectionnes": ["Turbidité", "pH", "DCO"]
            }
    
    def save_parametres(self, data):
        with open(self.parametres_file, 'w') as f:
            json.dump(data, f, indent=4)

def calculer_volume_ppm(dilution, densite, matiere_active):
    """Calcule le volume de solution commerciale pure pour 1 ppm (mL/kg)"""
    if dilution == 0 or densite == 0 or matiere_active == 0:
        return 0
    volume_ppm = 1 / (densite * (matiere_active/100) * dilution)
    return volume_ppm

def calculer_ppm_from_ml(volume_ml, volume_ppm, volume_eau_l=1.0):
    """Calcule les ppm à partir du volume en mL"""
    if volume_ppm == 0:
        return 0
    return (volume_ml / volume_eau_l) * (1 / volume_ppm)

def calculer_ppm_actif(ppm_commercial, matiere_active):
    """Calcule les ppm actifs à partir des ppm commerciaux"""
    return ppm_commercial * (matiere_active / 100)

def calculer_volume_solution_commerciale(ppm_commercial, volume_ppm, volume_eau_l=1.0):
    """Calcule le volume de solution commerciale pure"""
    return ppm_commercial * volume_ppm * volume_eau_l

def generer_rapport_pdf(date_test, operateur, site_prelevement, type_eau, volume_echantillon, 
                       temps_coagulation, vitesse_coagulation, temps_floculation, vitesse_floculation,
                       caracteristiques, debit_annuel, meilleur_abattement, coagulants_config, floculants_config,
                       tableau_essais):
    """Génère un rapport PDF avec les informations actuelles et les tableaux des essais"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Titre
    title_style = styles['Heading1']
    title_style.alignment = 1
    title = Paragraph("RAPPORT JAR TEST - TRAITEMENT DES EAUX", title_style)
    story.append(title)
    story.append(Spacer(1, 0.3*inch))
    
    # Informations Générales
    story.append(Paragraph("📋 Informations Générales", styles['Heading2']))
    info_generales = [
        ["Date du test", str(date_test)],
        ["Opérateur", operateur],
        ["Site de prélèvement", site_prelevement],
        ["Type d'eau", type_eau]
    ]
    table_info = Table(info_generales, colWidths=[2*inch, 4*inch])
    table_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table_info)
    story.append(Spacer(1, 0.2*inch))
    
    # Paramètres du Test
    story.append(Paragraph("⚙️ Paramètres du Test", styles['Heading2']))
    params_test = [
        ["Volume d'échantillon", f"{volume_echantillon:.2f} L"],
        ["Temps de coagulation", f"{temps_coagulation} min"],
        ["Vitesse coagulation", f"{vitesse_coagulation} rpm"],
        ["Temps de floculation", f"{temps_floculation} min"],
        ["Vitesse floculation", f"{vitesse_floculation} rpm"]
    ]
    table_params = Table(params_test, colWidths=[2*inch, 4*inch])
    table_params.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table_params)
    story.append(Spacer(1, 0.2*inch))
    
    # Caractéristiques de l'eau brute
    story.append(Paragraph("🔬 Caractéristiques de l'eau brute", styles['Heading2']))
    carac_eau = []
    for key, value in caracteristiques.items():
        if 'entree' in key:
            param_name = key.replace('_entree', '').replace('_', ' ').title()
            carac_eau.append([param_name, f"{value:.2f}"])
    
    if carac_eau:
        table_carac = Table(carac_eau, colWidths=[2*inch, 4*inch])
        table_carac.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table_carac)
    story.append(Spacer(1, 0.2*inch))
    
    # Tableaux des essais
    if tableau_essais:
        story.append(Paragraph("📊 Tableaux des Essais", styles['Heading2']))
        
        for combinaison, df in tableau_essais.items():
            story.append(Paragraph(f"Combinaison: {combinaison}", styles['Heading3']))
            story.append(Spacer(1, 0.1*inch))
            
            # Préparer les données pour le tableau
            table_data = [["Essai", "Coag (ppm)", "Coag (actif)", "Floc (ppm)", "Floc (actif)", "DCO e", "DCO s", "Abatt%", "V boue"]]
            
            for i, row in df.iterrows():
                # Trouver les infos des réactifs pour cette combinaison
                coag_nom = "Aucun"
                floc_nom = "Aucun"
                if "Coagulant seul:" in combinaison:
                    coag_nom = combinaison.replace("Coagulant seul: ", "")
                elif "Floculant seul:" in combinaison:
                    floc_nom = combinaison.replace("Floculant seul: ", "")
                elif " + " in combinaison:
                    parts = combinaison.split(" + ")
                    coag_nom = parts[0]
                    floc_nom = parts[1]
                
                coag_info = next((c for c in coagulants_config if c["nom"] == coag_nom), None)
                floc_info = next((f for f in floculants_config if f["nom"] == floc_nom), None)
                
                coag_actif = calculer_ppm_actif(row['Coagulant_ppm_com'], coag_info['matiere_active']) if coag_info and coag_info['nom'] != "Aucun" else 0
                floc_actif = calculer_ppm_actif(row['Floculant_ppm_com'], floc_info['matiere_active']) if floc_info and floc_info['nom'] != "Aucun" else 0
                
                table_data.append([
                    str(int(row['Essai'])),
                    f"{row['Coagulant_ppm_com']:.1f}",
                    f"{coag_actif:.1f}",
                    f"{row['Floculant_ppm_com']:.1f}",
                    f"{floc_actif:.1f}",
                    f"{row['DCO_entree']:.0f}",
                    f"{row['DCO_sortie']:.0f}",
                    f"{row['Abattement']:.1f}%",
                    f"{row['V_boue']:.1f}"
                ])
            
            # Créer le tableau
            table = Table(table_data, colWidths=[0.5*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
            ]))
            story.append(table)
            story.append(Spacer(1, 0.2*inch))
    
    # Meilleur Résultat
    if meilleur_abattement is not None:
        story.append(Paragraph("🏆 Meilleur Résultat", styles['Heading2']))
        meilleur_resultat = [
            ["Combinaison", meilleur_abattement['combinaison']],
            ["Essai", str(int(meilleur_abattement['essai']))],
            ["Abattement DCO", f"{meilleur_abattement['abattement']:.2f}%"],
            ["Volume de boue", f"{meilleur_abattement['v_boue']:.2f} mL"]
        ]
        table_meilleur = Table(meilleur_resultat, colWidths=[2*inch, 4*inch])
        table_meilleur.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table_meilleur)
    
    # Pied de page
    story.append(Spacer(1, 0.3*inch))
    date_gen = datetime.now().strftime("%d/%m/%Y à %H:%M")
    pied_page = Paragraph(f"<i>Rapport généré automatiquement le {date_gen}</i>", styles['Italic'])
    story.append(pied_page)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def afficher_tableaux_resultats(mesures_courantes):
    """Affiche les résultats sous forme de tableaux au lieu de graphiques"""
    
    if mesures_courantes.empty:
        st.info("Aucune donnée disponible pour afficher les résultats.")
        return
    
    st.subheader("📈 Résultats des Essais")
    
    # Tableau d'abattement DCO
    st.markdown("**Abattement DCO par combinaison**")
    abattement_data = mesures_courantes.groupby('combinaison').agg({
        'abattement': ['max', 'mean'],
        'essai': 'count'
    }).round(2)
    abattement_data.columns = ['Abattement Max (%)', 'Abattement Moyen (%)', 'Nombre Essais']
    st.dataframe(abattement_data, use_container_width=True)
    
    # Tableau détaillé des essais
    st.markdown("**Détail des essais**")
    colonnes_a_afficher = ['combinaison', 'essai', 'coagulant_ml', 'floculant_ml', 'dco_entree', 'dco_sortie', 'abattement', 'v_boue']
    colonnes_disponibles = [col for col in colonnes_a_afficher if col in mesures_courantes.columns]
    st.dataframe(mesures_courantes[colonnes_disponibles], use_container_width=True)

def configurer_reactifs():
    st.markdown('<h2 class="section-header">⚗️ Configuration des Réactifs</h2>', unsafe_allow_html=True)
    
    config_manager = ConfigManager()
    
    tab1, tab2, tab3 = st.tabs(["🧪 Coagulants", "🧴 Floculants", "📊 Paramètres Mesures"])
    
    with tab1:
        st.subheader("Configuration des Coagulants")
        coagulants = config_manager.load_coagulants()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Ajouter/Modifier un coagulant")
            
            coagulant_a_modifier = None
            for coag in coagulants:
                if f"modify_coag_{coag['nom']}" in st.session_state and st.session_state[f"modify_coag_{coag['nom']}"]:
                    coagulant_a_modifier = coag
                    break
            
            with st.form("coagulant_form"):
                if coagulant_a_modifier:
                    nom = st.text_input("Nom du coagulant", value=coagulant_a_modifier["nom"])
                    dilution = st.number_input("Dilution", min_value=0.1, value=float(coagulant_a_modifier["dilution"]), step=0.1, format="%.2f")
                    densite = st.number_input("Densité (kg/L)", min_value=0.1, value=float(coagulant_a_modifier["densite"]), step=0.1, format="%.2f")
                    matiere_active = st.number_input("Matière active (%)", min_value=0.1, max_value=100.00, value=float(coagulant_a_modifier["matiere_active"]), step=0.1, format="%.2f")
                    prix_kg = st.number_input("Prix du kilo (€)", min_value=0.00, value=float(coagulant_a_modifier["prix_kg"]), step=0.1, format="%.2f")
                    
                    submitted = st.form_submit_button("💾 Enregistrer les modifications")
                    
                    if submitted and nom and nom != "Aucun":
                        for i, coag in enumerate(coagulants):
                            if coag["nom"] == coagulant_a_modifier["nom"]:
                                coagulants[i] = {
                                    "nom": nom,
                                    "dilution": dilution,
                                    "densite": densite,
                                    "matiere_active": matiere_active,
                                    "prix_kg": prix_kg
                                }
                                config_manager.save_coagulants(coagulants)
                                st.success(f"Coagulant '{nom}' modifié avec succès!")
                                st.session_state[f"modify_coag_{coagulant_a_modifier['nom']}"] = False
                                st.rerun()
                
                else:
                    nom = st.text_input("Nom du coagulant")
                    dilution = st.number_input("Dilution", min_value=0.1, value=1.0, step=0.1, format="%.2f")
                    densite = st.number_input("Densité (kg/L)", min_value=0.1, value=1.0, step=0.1, format="%.2f")
                    matiere_active = st.number_input("Matière active (%)", min_value=0.1, max_value=100.00, value=100.00, step=0.1, format="%.2f")
                    prix_kg = st.number_input("Prix du kilo (€)", min_value=0.00, value=10.00, step=0.1, format="%.2f")
                    
                    col_add, col_update = st.columns(2)
                    with col_add:
                        submitted_add = st.form_submit_button("➕ Ajouter")
                    with col_update:
                        submitted_update = st.form_submit_button("✏️ Modifier")
                    
                    if submitted_add and nom and nom != "Aucun":
                        nouveau_coagulant = {
                            "nom": nom,
                            "dilution": dilution,
                            "densite": densite,
                            "matiere_active": matiere_active,
                            "prix_kg": prix_kg
                        }
                        coagulants.append(nouveau_coagulant)
                        config_manager.save_coagulants(coagulants)
                        st.success(f"Coagulant '{nom}' ajouté avec succès!")
                        st.rerun()
                    
                    if submitted_update and nom:
                        for i, coag in enumerate(coagulants):
                            if coag["nom"] == nom:
                                coagulants[i] = {
                                    "nom": nom,
                                    "dilution": dilution,
                                    "densite": densite,
                                    "matiere_active": matiere_active,
                                    "prix_kg": prix_kg
                                }
                                config_manager.save_coagulants(coagulants)
                                st.success(f"Coagulant '{nom}' modifié avec succès!")
                                st.rerun()
                        else:
                            st.error(f"Coagulant '{nom}' non trouvé!")
        
        with col2:
            st.subheader("Coagulants configurés")
            coagulants_a_afficher = [c for c in coagulants if c["nom"] != "Aucun"]
            
            if not coagulants_a_afficher:
                st.info("Aucun coagulant configuré. Ajoutez-en un dans le formulaire de gauche.")
            else:
                for i, coag in enumerate(coagulants_a_afficher):
                    index_reel = coagulants.index(coag)
                    with st.expander(f"🔬 {coag['nom']}", expanded=False):
                        st.write(f"**Dilution:** {coag['dilution']:.2f}")
                        st.write(f"**Densité:** {coag['densite']:.2f} kg/L")
                        st.write(f"**Matière active:** {coag['matiere_active']:.2f}%")
                        st.write(f"**Prix:** {coag['prix_kg']:.2f} €/kg")
                        
                        volume_ppm = calculer_volume_ppm(coag['dilution'], coag['densite'], coag['matiere_active'])
                        st.write(f"**Volume pour 1 ppm:** {volume_ppm:.4f} mL/kg")
                        
                        col_mod, col_del = st.columns(2)
                        with col_mod:
                            if st.button("✏️ Modifier", key=f"mod_coag_{index_reel}"):
                                st.session_state[f"modify_coag_{coag['nom']}"] = True
                                st.rerun()
                        with col_del:
                            if st.button("🗑️ Supprimer", key=f"del_coag_{index_reel}"):
                                coagulants.pop(index_reel)
                                config_manager.save_coagulants(coagulants)
                                st.success(f"Coagulant '{coag['nom']}' supprimé!")
                                st.rerun()
    
    with tab2:
        st.subheader("Configuration des Floculants")
        floculants = config_manager.load_floculants()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Ajouter/Modifier un floculant")
            
            floculant_a_modifier = None
            for floc in floculants:
                if f"modify_floc_{floc['nom']}" in st.session_state and st.session_state[f"modify_floc_{floc['nom']}"]:
                    floculant_a_modifier = floc
                    break
            
            with st.form("floculant_form"):
                if floculant_a_modifier:
                    nom = st.text_input("Nom du floculant", value=floculant_a_modifier["nom"])
                    type_floc = st.selectbox("Type", ["Liquide", "Solide"], index=0 if floculant_a_modifier["type"] == "Liquide" else 1)
                    dilution = st.number_input("Dilution", min_value=0.1, value=float(floculant_a_modifier["dilution"]), step=0.1, format="%.2f")
                    densite = st.number_input("Densité (kg/L)", min_value=0.1, value=float(floculant_a_modifier["densite"]), step=0.1, format="%.2f")
                    matiere_active = st.number_input("Matière active (%)", min_value=0.1, max_value=100.00, value=float(floculant_a_modifier["matiere_active"]), step=0.1, format="%.2f")
                    prix_kg = st.number_input("Prix du kilo (€)", min_value=0.00, value=float(floculant_a_modifier["prix_kg"]), step=0.1, format="%.2f")
                    
                    submitted = st.form_submit_button("💾 Enregistrer les modifications")
                    
                    if submitted and nom and nom != "Aucun":
                        for i, floc in enumerate(floculants):
                            if floc["nom"] == floculant_a_modifier["nom"]:
                                floculants[i] = {
                                    "nom": nom,
                                    "type": type_floc,
                                    "dilution": dilution,
                                    "densite": densite,
                                    "matiere_active": matiere_active,
                                    "prix_kg": prix_kg
                                }
                                config_manager.save_floculants(floculants)
                                st.success(f"Floculant '{nom}' modifié avec succès!")
                                st.session_state[f"modify_floc_{floculant_a_modifier['nom']}"] = False
                                st.rerun()
                
                else:
                    nom = st.text_input("Nom du floculant")
                    type_floc = st.selectbox("Type", ["Liquide", "Solide"])
                    dilution = st.number_input("Dilution", min_value=0.1, value=1.0, step=0.1, format="%.2f")
                    densite = st.number_input("Densité (kg/L)", min_value=0.1, value=1.0, step=0.1, format="%.2f")
                    matiere_active = st.number_input("Matière active (%)", min_value=0.1, max_value=100.00, value=100.00, step=0.1, format="%.2f")
                    prix_kg = st.number_input("Prix du kilo (€)", min_value=0.00, value=10.00, step=0.1, format="%.2f")
                    
                    col_add, col_update = st.columns(2)
                    with col_add:
                        submitted_add = st.form_submit_button("➕ Ajouter")
                    with col_update:
                        submitted_update = st.form_submit_button("✏️ Modifier")
                    
                    if submitted_add and nom and nom != "Aucun":
                        nouveau_floculant = {
                            "nom": nom,
                            "type": type_floc,
                            "dilution": dilution,
                            "densite": densite,
                            "matiere_active": matiere_active,
                            "prix_kg": prix_kg
                        }
                        floculants.append(nouveau_floculant)
                        config_manager.save_floculants(floculants)
                        st.success(f"Floculant '{nom}' ajouté avec succès!")
                        st.rerun()
                    
                    if submitted_update and nom:
                        for i, floc in enumerate(floculants):
                            if floc["nom"] == nom:
                                floculants[i] = {
                                    "nom": nom,
                                    "type": type_floc,
                                    "dilution": dilution,
                                    "densite": densite,
                                    "matiere_active": matiere_active,
                                    "prix_kg": prix_kg
                                }
                                config_manager.save_floculants(floculants)
                                st.success(f"Floculant '{nom}' modifié avec succès!")
                                st.rerun()
                        else:
                            st.error(f"Floculant '{nom}' non trouvé!")
        
        with col2:
            st.subheader("Floculants configurés")
            floculants_a_afficher = [f for f in floculants if f["nom"] != "Aucun"]
            
            if not floculants_a_afficher:
                st.info("Aucun floculant configuré. Ajoutez-en un dans le formulaire de gauche.")
            else:
                for i, floc in enumerate(floculants_a_afficher):
                    index_reel = floculants.index(floc)
                    with st.expander(f"🧴 {floc['nom']}", expanded=False):
                        st.write(f"**Type:** {floc['type']}")
                        st.write(f"**Dilution:** {floc['dilution']:.2f}")
                        st.write(f"**Densité:** {floc['densite']:.2f} kg/L")
                        st.write(f"**Matière active:** {floc['matiere_active']:.2f}%")
                        st.write(f"**Prix:** {floc['prix_kg']:.2f} €/kg")
                        
                        volume_ppm = calculer_volume_ppm(floc['dilution'], floc['densite'], floc['matiere_active'])
                        st.write(f"**Volume pour 1 ppm:** {volume_ppm:.4f} mL/kg")
                        
                        col_mod, col_del = st.columns(2)
                        with col_mod:
                            if st.button("✏️ Modifier", key=f"mod_floc_{index_reel}"):
                                st.session_state[f"modify_floc_{floc['nom']}"] = True
                                st.rerun()
                        with col_del:
                            if st.button("🗑️ Supprimer", key=f"del_floc_{index_reel}"):
                                floculants.pop(index_reel)
                                config_manager.save_floculants(floculants)
                                st.success(f"Floculant '{floc['nom']}' supprimé!")
                                st.rerun()
    
    with tab3:
        st.subheader("Paramètres de Mesures")
        config_parametres = config_manager.load_parametres()
        parametres_mesures = config_parametres.get("parametres_mesures", [])
        parametres_selectionnes = config_parametres.get("parametres_selectionnes", [])
        
        st.write("Sélectionnez les paramètres à mesurer:")
        
        parametres_selectionnes = st.multiselect(
            "Paramètres à inclure dans les essais",
            options=parametres_mesures,
            default=parametres_selectionnes
        )
        
        if st.button("💾 Enregistrer la configuration"):
            config_parametres["parametres_selectionnes"] = parametres_selectionnes
            config_manager.save_parametres(config_parametres)
            st.success("Configuration des paramètres enregistrée!")

def afficher_base_donnees():
    st.markdown('<h2 class="section-header">📊 Base de Données des Mesures</h2>', unsafe_allow_html=True)
    
    db_manager = DatabaseManager()
    mesures = db_manager.get_all_mesures()
    
    if mesures.empty:
        st.info("Aucune mesure enregistrée dans la base de données.")
    else:
        st.write(f"**Total des mesures :** {len(mesures)}")
        
        # Filtres
        col1, col2, col3 = st.columns(3)
        with col1:
            dates_uniques = mesures['date_test'].unique()
            date_filtre = st.selectbox("Filtrer par date", ["Toutes"] + list(dates_uniques))
        with col2:
            sites_uniques = mesures['site_prelevement'].unique()
            site_filtre = st.selectbox("Filtrer par site", ["Tous"] + list(sites_uniques))
        with col3:
            combinaisons_uniques = mesures['combinaison'].unique()
            combinaison_filtre = st.selectbox("Filtrer par combinaison", ["Toutes"] + list(combinaisons_uniques))
        
        # Application des filtres
        if date_filtre != "Toutes":
            mesures = mesures[mesures['date_test'] == date_filtre]
        if site_filtre != "Tous":
            mesures = mesures[mesures['site_prelevement'] == site_filtre]
        if combinaison_filtre != "Toutes":
            mesures = mesures[mesures['combinaison'] == combinaison_filtre]
        
        st.dataframe(mesures, use_container_width=True)
        
        # Export des données
        csv = mesures.to_csv(index=False)
        st.download_button(
            label="📥 Exporter la base de données (CSV)",
            data=csv,
            file_name=f"base_donnees_jar_test_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

def main():
    st.markdown('<h1 class="main-header">📊 Générateur de Rapports Jar Test</h1>', unsafe_allow_html=True)
    
    # Initialisation des états de session
    if 'show_config' not in st.session_state:
        st.session_state.show_config = False
    if 'show_database' not in st.session_state:
        st.session_state.show_database = False
    if 'combinaisons' not in st.session_state:
        st.session_state.combinaisons = []
    if 'resultats_jar_test' not in st.session_state:
        st.session_state.resultats_jar_test = pd.DataFrame()
    if 'tableau_essais' not in st.session_state:
        st.session_state.tableau_essais = {}
    if 'nombre_essais_par_combinaison' not in st.session_state:
        st.session_state.nombre_essais_par_combinaison = {}
    
    # Boutons d'accueil
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⚙️ Configurer les réactifs", use_container_width=True):
            st.session_state.show_config = True
            st.rerun()
    with col2:
        if st.button("💾 Base de données", use_container_width=True):
            st.session_state.show_database = True
            st.rerun()
    with col3:
        if st.button("🔄 Nouveau Jar Test", use_container_width=True):
            st.session_state.show_config = False
            st.session_state.show_database = False
            st.rerun()
    
    if st.session_state.show_database:
        afficher_base_donnees()
        if st.button("← Retour à l'accueil"):
            st.session_state.show_database = False
            st.rerun()
        return
    
    if st.session_state.show_config:
        configurer_reactifs()
        if st.button("← Retour à l'accueil"):
            st.session_state.show_config = False
            st.rerun()
        return
    
    # Configuration des paramètres
    config_manager = ConfigManager()
    config_parametres = config_manager.load_parametres()
    parametres_selectionnes = config_parametres.get("parametres_selectionnes", ["Turbidité", "pH", "DCO"])
    
    # Sidebar pour les informations générales
    with st.sidebar:
        st.header("📋 Informations Générales")
        date_test = st.date_input("Date du test", datetime.now())
        operateur = st.text_input("Opérateur", "")
        site_prelevement = st.text_input("Site de prélèvement", "")
        type_eau = st.selectbox("Type d'eau", ["Eau de surface", "Eau souterraine", "Eau usée", "Autre"])
        
        st.header("⚙️ Paramètres du Test")
        volume_echantillon = st.number_input("Volume d'échantillon (L)", min_value=0.1, max_value=10.00, value=1.0, format="%.2f")
        
        st.subheader("Coagulation")
        temps_coagulation = st.number_input("Temps de coagulation (min)", min_value=1, max_value=60, value=2)
        vitesse_coagulation = st.number_input("Vitesse coagulation (rpm)", min_value=10, max_value=500, value=200)
        
        st.subheader("Floculation")
        temps_floculation = st.number_input("Temps de floculation (min)", min_value=1, max_value=60, value=20)
        vitesse_floculation = st.number_input("Vitesse floculation (rpm)", min_value=10, max_value=200, value=30)
        
        st.header("🔬 Caractéristiques de l'eau brute")
        caracteristiques = {}
        if "Turbidité" in parametres_selectionnes:
            caracteristiques['turbidite_entree'] = st.number_input("Turbidité initiale (NTU)", min_value=0.00, value=15.0, format="%.2f")
        if "Couleur" in parametres_selectionnes:
            caracteristiques['couleur_entree'] = st.number_input("Couleur initiale (Pt-Co)", min_value=0.00, value=25.0, format="%.2f")
        if "pH" in parametres_selectionnes:
            caracteristiques['ph_entree'] = st.number_input("pH initial", min_value=0.00, max_value=14.0, value=7.2, format="%.2f")
        if "Conductivité" in parametres_selectionnes:
            caracteristiques['conductivite_entree'] = st.number_input("Conductivité initiale (µS/cm)", min_value=0.00, value=500.00, format="%.2f")
        if "MES" in parametres_selectionnes:
            caracteristiques['mes_entree'] = st.number_input("MES initiaux (mg/L)", min_value=0.00, value=50.00, format="%.2f")
        if "UV254" in parametres_selectionnes:
            caracteristiques['uv254_entree'] = st.number_input("UV254 initial (abs)", min_value=0.00, value=0.1, step=0.001, format="%.3f")
        if "DCO" in parametres_selectionnes:
            caracteristiques['dco_entree'] = st.number_input("DCO entrée (mg/L)", min_value=0.00, value=150.00, format="%.2f")
        
        # Informations de traitement
        st.header("💧 Informations de Traitement")
        debit_eau = st.number_input("Débit d'eau à traiter (m³/h)", min_value=0.1, value=10.00, format="%.2f")
        heures_par_jour = st.number_input("Nombre d'heures de fonctionnement par jour", min_value=1, max_value=24, value=24)
        volume_journalier = debit_eau * heures_par_jour
        st.metric("Volume à traiter par jour (m³)", f"{volume_journalier:.2f}")
        jours_par_an = st.number_input("Nombre de jours par an", min_value=1, max_value=365, value=330)
        
        # Calcul du débit annuel
        debit_annuel = volume_journalier * jours_par_an
        st.metric("Débit annuel traité", f"{debit_annuel:,.2f} m³/an")
    
    # Chargement des configurations
    coagulants_config = config_manager.load_coagulants()
    floculants_config = config_manager.load_floculants()
    
    # Onglets principaux
    tab1, tab2, tab3, tab4 = st.tabs(["🔄 Combinaisons", "📊 Saisie Essais", "📈 Résultats", "📄 Rapport Complet"])
    
    with tab1:
        st.markdown('<h2 class="section-header">Configuration des Combinaisons</h2>', unsafe_allow_html=True)
        
        if not coagulants_config:
            st.warning("⚠️ Veuillez configurer des coagulants d'abord")
            if st.button("Configurer les réactifs"):
                st.session_state.show_config = True
                st.rerun()
            return
        
        # Sélection des combinaisons coagulant/floculant
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sélection des réactifs")
            coagulant_selected = st.selectbox("Coagulant", [c["nom"] for c in coagulants_config])
            floculant_selected = st.selectbox("Floculant", [f["nom"] for f in floculants_config])
        
        with col2:
            st.subheader("Paramètres de dosage")
            coagulant_info = next((c for c in coagulants_config if c["nom"] == coagulant_selected), None)
            floculant_info = next((f for f in floculants_config if f["nom"] == floculant_selected), None)
            
            if coagulant_info and coagulant_info['nom'] != "Aucun":
                st.markdown(f"""
                **Coagulant: {coagulant_info['nom']}**
                - **Matière active:** {coagulant_info['matiere_active']:.2f}%
                - **Densité:** {coagulant_info['densite']:.2f} kg/L
                - **Dilution:** {coagulant_info['dilution']:.2f}
                """)
                
                volume_ppm_coag = calculer_volume_ppm(coagulant_info['dilution'], coagulant_info['densite'], coagulant_info['matiere_active'])
                st.markdown(f"""
                - **Volume pour 1 ppm:** {volume_ppm_coag:.6f} mL/kg
                - **50 ppm =** {50 * volume_ppm_coag:.3f} mL/L
                """)
            elif coagulant_info and coagulant_info['nom'] == "Aucun":
                st.markdown("**Coagulant: Aucun**")
            
            if floculant_info and floculant_info['nom'] != "Aucun":
                st.markdown(f"""
                **Floculant: {floculant_info['nom']}**
                - **Type:** {floculant_info['type']}
                - **Matière active:** {floculant_info['matiere_active']:.2f}%
                - **Densité:** {floculant_info['densite']:.2f} kg/L
                - **Dilution:** {floculant_info['dilution']:.2f}
                """)
                
                volume_ppm_floc = calculer_volume_ppm(floculant_info['dilution'], floculant_info['densite'], floculant_info['matiere_active'])
                unite = "mL/kg" if floculant_info['type'] == 'Liquide' else "g/kg"
                st.markdown(f"""
                - **Volume/masse pour 1 ppm:** {volume_ppm_floc:.6f} {unite}
                - **1 mL solution diluée =** {calculer_ppm_from_ml(1, volume_ppm_floc):.2f} ppm
                """)
            elif floculant_info and floculant_info['nom'] == "Aucun":
                st.markdown("**Floculant: Aucun**")
        
        # Gestion des combinaisons
        st.subheader("Combinaisons à tester")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            # Déterminer le nom de la combinaison en fonction des sélections
            if coagulant_selected == "Aucun" and floculant_selected == "Aucun":
                nouvelle_combinaison = "Témoin (sans réactif)"
            elif coagulant_selected == "Aucun":
                nouvelle_combinaison = f"Floculant seul: {floculant_selected}"
            elif floculant_selected == "Aucun":
                nouvelle_combinaison = f"Coagulant seul: {coagulant_selected}"
            else:
                nouvelle_combinaison = f"{coagulant_selected} + {floculant_selected}"
        with col2:
            if st.button("➕ Ajouter combinaison") and nouvelle_combinaison not in st.session_state.combinaisons:
                st.session_state.combinaisons.append(nouvelle_combinaison)
                st.rerun()
        
        # Affichage des combinaisons
        if st.session_state.combinaisons:
            st.write("Combinaisons sélectionnées:")
            for i, combinaison in enumerate(st.session_state.combinaisons):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {combinaison}")
                with col2:
                    if st.button("❌", key=f"del_{i}"):
                        st.session_state.combinaisons.pop(i)
                        st.rerun()
    
    with tab2:
        st.markdown('<h2 class="section-header">Saisie des Essais</h2>', unsafe_allow_html=True)
        
        if not st.session_state.combinaisons:
            st.warning("Veuillez configurer au moins une combinaison dans l'onglet 'Combinaisons'")
            return
        
        # Initialisation de la base de données
        db_manager = DatabaseManager()
        
        # Tableau de saisie pour chaque combinaison
        for combinaison in st.session_state.combinaisons:
            st.markdown(f"### {combinaison}")
            
            # Configuration du nombre d'essais par défaut à 4
            if combinaison not in st.session_state.nombre_essais_par_combinaison:
                st.session_state.nombre_essais_par_combinaison[combinaison] = 4
            
            nombre_essais = st.number_input(
                f"Nombre d'essais pour {combinaison}", 
                min_value=1, 
                max_value=20, 
                value=st.session_state.nombre_essais_par_combinaison[combinaison],
                key=f"nb_essais_{combinaison}"
            )
            st.session_state.nombre_essais_par_combinaison[combinaison] = nombre_essais
            
            # Déterminer les réactifs de la combinaison
            coagulant_nom = "Aucun"
            floculant_nom = "Aucun"
            if "Coagulant seul:" in combinaison:
                coagulant_nom = combinaison.replace("Coagulant seul: ", "")
            elif "Floculant seul:" in combinaison:
                floculant_nom = combinaison.replace("Floculant seul: ", "")
            elif "Témoin" in combinaison:
                coagulant_nom = "Aucun"
                floculant_nom = "Aucun"
            elif " + " in combinaison:
                parts = combinaison.split(" + ")
                coagulant_nom = parts[0]
                floculant_nom = parts[1]
            
            coagulant_info = next((c for c in coagulants_config if c["nom"] == coagulant_nom), coagulants_config[0])
            floculant_info = next((f for f in floculants_config if f["nom"] == floculant_nom), floculants_config[0])
            
            # Initialiser le tableau pour cette combinaison
            if combinaison not in st.session_state.tableau_essais:
                donnees_initiales = []
                for i in range(nombre_essais):
                    # Calcul des dosages par défaut
                    coag_ml = 0.0
                    floc_ml = 0.0
                    coag_ppm_com = 0.0
                    floc_ppm_com = 0.0
                    
                    if coagulant_info and coagulant_info['nom'] != "Aucun":
                        volume_ppm_coag = calculer_volume_ppm(coagulant_info['dilution'], coagulant_info['densite'], coagulant_info['matiere_active'])
                        # Incrémentation de 50 ppm pour chaque essai à partir du 2ème
                        coag_ppm_com = i * 50 if i > 0 else 0.0
                        coag_ml = coag_ppm_com * volume_ppm_coag * volume_echantillon
                    
                    if floculant_info and floculant_info['nom'] != "Aucun":
                        # 1 ppm commercial pour tous les essais sauf le premier
                        floc_ppm_com = 1.0 if i > 0 else 0.0
                        volume_ppm_floc = calculer_volume_ppm(floculant_info['dilution'], floculant_info['densite'], floculant_info['matiere_active'])
                        floc_ml = floc_ppm_com * volume_ppm_floc * volume_echantillon
                    
                    donnees_initiales.append({
                        'Essai': i + 1,
                        'Coagulant_ml': coag_ml,
                        'Floculant_ml': floc_ml,
                        'Coagulant_ppm_com': coag_ppm_com,
                        'Floculant_ppm_com': floc_ppm_com,
                        'DCO_entree': caracteristiques.get('dco_entree', 0.0),
                        'pH_entree': caracteristiques.get('ph_entree', 0.0),
                        'DCO_sortie': 0.0,
                        'pH_sortie': 0.0,
                        'V_boue': 0.0,
                        'Turbidite': '',
                        'Abattement': 0.0,
                        'Turbidite_entree': caracteristiques.get('turbidite_entree', 0.0),
                        'Turbidite_sortie': 0.0,
                        'Couleur_entree': caracteristiques.get('couleur_entree', 0.0),
                        'Couleur_sortie': 0.0,
                        'MES_entree': caracteristiques.get('mes_entree', 0.0),
                        'MES_sortie': 0.0,
                        'UV254_entree': caracteristiques.get('uv254_entree', 0.0),
                        'UV254_sortie': 0.0,
                        'Aluminium_residuel': 0.0,
                        'Fer_residuel': 0.0,
                        'Conductivite_entree': caracteristiques.get('conductivite_entree', 0.0),
                        'Conductivite_sortie': 0.0
                    })
                
                st.session_state.tableau_essais[combinaison] = pd.DataFrame(donnees_initiales)
            
            # Interface de saisie
            st.write("**Tableau de saisie:**")
            
            # En-têtes du tableau
            headers = ["Essai", "Coag (ppm com.)", "Coag (ppm actif)", "Floc (ppm com.)", "Floc (ppm actif)", "DCO e", "DCO s", "pH e", "pH s", "V boue", "Abattement %"]
            
            cols = st.columns(len(headers))
            for col, header in zip(cols, headers):
                col.write(f"**{header}**")
            
            # Lignes de saisie
            for i in range(nombre_essais):
                cols = st.columns(len(headers))
                
                with cols[0]:
                    st.write(f"{i+1}")
                
                with cols[1]:
                    if coagulant_info and coagulant_info['nom'] != "Aucun":
                        ppm_commercial_coag = st.number_input(
                            "",
                            value=float(st.session_state.tableau_essais[combinaison].iloc[i]['Coagulant_ppm_com']),
                            key=f"coag_ppm_{combinaison}_{i}", 
                            format="%.2f"
                        )
                        st.session_state.tableau_essais[combinaison].iloc[i, 3] = ppm_commercial_coag
                        
                        volume_ppm_coag = calculer_volume_ppm(coagulant_info['dilution'], coagulant_info['densite'], coagulant_info['matiere_active'])
                        volume_ml_coag = ppm_commercial_coag * volume_ppm_coag * volume_echantillon
                        st.session_state.tableau_essais[combinaison].iloc[i, 1] = volume_ml_coag
                    else:
                        st.write("0.00")
                        st.session_state.tableau_essais[combinaison].iloc[i, 3] = 0.0
                        st.session_state.tableau_essais[combinaison].iloc[i, 1] = 0.0
                
                with cols[2]:
                    if coagulant_info and coagulant_info['nom'] != "Aucun":
                        ppm_commercial_coag = st.session_state.tableau_essais[combinaison].iloc[i, 3]
                        ppm_actif_coag = calculer_ppm_actif(ppm_commercial_coag, coagulant_info['matiere_active'])
                        st.write(f"{ppm_actif_coag:.2f}")
                    else:
                        st.write("0.00")
                
                with cols[3]:
                    if floculant_info and floculant_info['nom'] != "Aucun":
                        ppm_commercial_floc = st.number_input(
                            "",
                            value=float(st.session_state.tableau_essais[combinaison].iloc[i]['Floculant_ppm_com']),
                            key=f"floc_ppm_{combinaison}_{i}", 
                            format="%.2f"
                        )
                        st.session_state.tableau_essais[combinaison].iloc[i, 4] = ppm_commercial_floc
                        
                        volume_ppm_floc = calculer_volume_ppm(floculant_info['dilution'], floculant_info['densite'], floculant_info['matiere_active'])
                        volume_ml_floc = ppm_commercial_floc * volume_ppm_floc * volume_echantillon
                        st.session_state.tableau_essais[combinaison].iloc[i, 2] = volume_ml_floc
                    else:
                        st.write("0.00")
                        st.session_state.tableau_essais[combinaison].iloc[i, 4] = 0.0
                        st.session_state.tableau_essais[combinaison].iloc[i, 2] = 0.0
                
                with cols[4]:
                    if floculant_info and floculant_info['nom'] != "Aucun":
                        ppm_commercial_floc = st.session_state.tableau_essais[combinaison].iloc[i, 4]
                        ppm_actif_floc = calculer_ppm_actif(ppm_commercial_floc, floculant_info['matiere_active'])
                        st.write(f"{ppm_actif_floc:.2f}")
                    else:
                        st.write("0.00")
                
                with cols[5]:
                    dco_e = st.number_input(
                        "",
                        value=float(st.session_state.tableau_essais[combinaison].iloc[i]['DCO_entree']),
                        key=f"dco_e_{combinaison}_{i}", 
                        format="%.2f"
                    )
                    st.session_state.tableau_essais[combinaison].iloc[i, 5] = dco_e
                
                with cols[6]:
                    dco_s = st.number_input(
                        "",
                        value=float(st.session_state.tableau_essais[combinaison].iloc[i]['DCO_sortie']),
                        key=f"dco_s_{combinaison}_{i}", 
                        format="%.2f"
                    )
                    st.session_state.tableau_essais[combinaison].iloc[i, 7] = dco_s
                
                with cols[7]:
                    ph_e = st.number_input(
                        "",
                        value=float(st.session_state.tableau_essais[combinaison].iloc[i]['pH_entree']),
                        key=f"ph_e_{combinaison}_{i}", 
                        format="%.2f"
                    )
                    st.session_state.tableau_essais[combinaison].iloc[i, 6] = ph_e
                
                with cols[8]:
                    ph_s = st.number_input(
                        "",
                        value=float(st.session_state.tableau_essais[combinaison].iloc[i]['pH_sortie']),
                        key=f"ph_s_{combinaison}_{i}", 
                        format="%.2f"
                    )
                    st.session_state.tableau_essais[combinaison].iloc[i, 8] = ph_s
                
                with cols[9]:
                    v_boue = st.number_input(
                        "",
                        value=float(st.session_state.tableau_essais[combinaison].iloc[i]['V_boue']),
                        key=f"v_boue_{combinaison}_{i}", 
                        format="%.2f"
                    )
                    st.session_state.tableau_essais[combinaison].iloc[i, 9] = v_boue
                
                with cols[10]:
                    if st.session_state.tableau_essais[combinaison].iloc[i, 5] > 0 and st.session_state.tableau_essais[combinaison].iloc[i, 7] > 0:
                        abattement = ((st.session_state.tableau_essais[combinaison].iloc[i, 5] - st.session_state.tableau_essais[combinaison].iloc[i, 7]) / st.session_state.tableau_essais[combinaison].iloc[i, 5]) * 100
                        st.session_state.tableau_essais[combinaison].iloc[i, 11] = abattement
                        st.write(f"{abattement:.2f}%")
                    else:
                        st.write("")
            
            # Bouton d'enregistrement dans la base de données
            if st.button(f"💾 Enregistrer {combinaison} dans la base de données"):
                for i in range(nombre_essais):
                    data = {
                        'date_test': str(date_test),
                        'operateur': operateur,
                        'site_prelevement': site_prelevement,
                        'type_eau': type_eau,
                        'volume_echantillon': volume_echantillon,
                        'temps_coagulation': temps_coagulation,
                        'vitesse_coagulation': vitesse_coagulation,
                        'temps_floculation': temps_floculation,
                        'vitesse_floculation': vitesse_floculation,
                        'combinaison': combinaison,
                        'essai': i + 1,
                        'coagulant_ml': st.session_state.tableau_essais[combinaison].iloc[i]['Coagulant_ml'],
                        'floculant_ml': st.session_state.tableau_essais[combinaison].iloc[i]['Floculant_ml'],
                        'dco_entree': st.session_state.tableau_essais[combinaison].iloc[i]['DCO_entree'],
                        'ph_entree': st.session_state.tableau_essais[combinaison].iloc[i]['pH_entree'],
                        'dco_sortie': st.session_state.tableau_essais[combinaison].iloc[i]['DCO_sortie'],
                        'ph_sortie': st.session_state.tableau_essais[combinaison].iloc[i]['pH_sortie'],
                        'v_boue': st.session_state.tableau_essais[combinaison].iloc[i]['V_boue'],
                        'turbidite': st.session_state.tableau_essais[combinaison].iloc[i]['Turbidite'],
                        'abattement': st.session_state.tableau_essais[combinaison].iloc[i]['Abattement'],
                        'turbidite_entree': st.session_state.tableau_essais[combinaison].iloc[i]['Turbidite_entree'],
                        'turbidite_sortie': st.session_state.tableau_essais[combinaison].iloc[i]['Turbidite_sortie'],
                        'couleur_entree': st.session_state.tableau_essais[combinaison].iloc[i]['Couleur_entree'],
                        'couleur_sortie': st.session_state.tableau_essais[combinaison].iloc[i]['Couleur_sortie'],
                        'mes_entree': st.session_state.tableau_essais[combinaison].iloc[i]['MES_entree'],
                        'mes_sortie': st.session_state.tableau_essais[combinaison].iloc[i]['MES_sortie'],
                        'uv254_entree': st.session_state.tableau_essais[combinaison].iloc[i]['UV254_entree'],
                        'uv254_sortie': st.session_state.tableau_essais[combinaison].iloc[i]['UV254_sortie'],
                        'aluminium_residuel': st.session_state.tableau_essais[combinaison].iloc[i]['Aluminium_residuel'],
                        'fer_residuel': st.session_state.tableau_essais[combinaison].iloc[i]['Fer_residuel'],
                        'conductivite_entree': st.session_state.tableau_essais[combinaison].iloc[i]['Conductivite_entree'],
                        'conductivite_sortie': st.session_state.tableau_essais[combinaison].iloc[i]['Conductivite_sortie']
                    }
                    db_manager.save_mesure(data)
                st.success(f"Combinaison {combinaison} enregistrée dans la base de données!")
            
            st.markdown("---")
    
    with tab3:
        st.markdown('<h2 class="section-header">Résultats des Essais</h2>', unsafe_allow_html=True)
        
        # Récupérer les données de la base
        db_manager = DatabaseManager()
        mesures_db = db_manager.get_all_mesures()
        
        if not mesures_db.empty:
            # Filtrer les mesures de la session courante
            mesures_courantes = mesures_db[
                (mesures_db['date_test'] == str(date_test)) & 
                (mesures_db['operateur'] == operateur) &
                (mesures_db['site_prelevement'] == site_prelevement)
            ]
            
            if not mesures_courantes.empty:
                afficher_tableaux_resultats(mesures_courantes)
            else:
                st.info("Aucune donnée disponible pour la session courante. Veuillez enregistrer des essais dans l'onglet 'Saisie Essais'.")
        else:
            st.info("Aucune donnée dans la base de données. Veuillez enregistrer des essais dans l'onglet 'Saisie Essais'.")
    
    with tab4:
        st.markdown('<h2 class="section-header">Rapport Complet</h2>', unsafe_allow_html=True)
        
        # Génération du rapport basé sur la base de données
        db_manager = DatabaseManager()
        mesures_db = db_manager.get_all_mesures()
        
        if not mesures_db.empty:
            mesures_courantes = mesures_db[
                (mesures_db['date_test'] == str(date_test)) & 
                (mesures_db['operateur'] == operateur) &
                (mesures_db['site_prelevement'] == site_prelevement)
            ]
            
            if not mesures_courantes.empty:
                # Trouver les meilleurs résultats
                meilleur_abattement = mesures_courantes.loc[mesures_courantes['abattement'].idxmax()]
                
                rapport = f"""
# RAPPORT JAR TEST - TRAITEMENT DES EAUX

## 📋 Informations Générales
- **Date du test** : {date_test}
- **Opérateur** : {operateur}
- **Site de prélèvement** : {site_prelevement}
- **Type d'eau** : {type_eau}

## ⚙️ Paramètres du Test
- **Volume d'échantillon** : {volume_echantillon:.2f} L
- **Coagulation** : {temps_coagulation} min à {vitesse_coagulation} rpm
- **Floculation** : {temps_floculation} min à {vitesse_floculation} rpm

## 🔬 Caractéristiques de l'eau brute
"""
                for param in parametres_selectionnes:
                    if param in ["Turbidité", "Couleur", "pH", "Conductivité", "MES", "UV254", "DCO"]:
                        valeur = caracteristiques.get(f"{param.lower().replace(' ', '_').replace('é', 'e')}_entree", "N/A")
                        rapport += f"- **{param}** : {valeur:.2f}\n"
                
                rapport += f"""
## 💧 Informations de Traitement
- **Débit d'eau à traiter** : {debit_eau:.2f} m³/h
- **Heures de fonctionnement par jour** : {heures_par_jour}
- **Volume à traiter par jour** : {volume_journalier:.2f} m³
- **Nombre de jours par an** : {jours_par_an}
- **Débit annuel traité** : {debit_annuel:,.2f} m³/an

## 🏆 Meilleur Résultat
- **Combinaison** : {meilleur_abattement['combinaison']}
- **Essai** : {int(meilleur_abattement['essai'])}
- **Abattement DCO** : {meilleur_abattement['abattement']:.2f}%
- **Volume de boue** : {meilleur_abattement['v_boue']:.2f} mL

## 📊 Tableaux des Essais
"""
                
                # Ajouter les tableaux des essais au rapport
                for combinaison, df in st.session_state.tableau_essais.items():
                    rapport += f"\n### {combinaison}\n"
                    rapport += "| Essai | Coag (ppm) | Coag (actif) | Floc (ppm) | Floc (actif) | DCO e | DCO s | Abatt% | V boue |\n"
                    rapport += "|-------|------------|--------------|------------|--------------|-------|-------|--------|--------|\n"
                    
                    for i, row in df.iterrows():
                        # Trouver les infos des réactifs pour cette combinaison
                        coag_nom = "Aucun"
                        floc_nom = "Aucun"
                        if "Coagulant seul:" in combinaison:
                            coag_nom = combinaison.replace("Coagulant seul: ", "")
                        elif "Floculant seul:" in combinaison:
                            floc_nom = combinaison.replace("Floculant seul: ", "")
                        elif " + " in combinaison:
                            parts = combinaison.split(" + ")
                            coag_nom = parts[0]
                            floc_nom = parts[1]
                        
                        coag_info = next((c for c in coagulants_config if c["nom"] == coag_nom), None)
                        floc_info = next((f for f in floculants_config if f["nom"] == floc_nom), None)
                        
                        coag_actif = calculer_ppm_actif(row['Coagulant_ppm_com'], coag_info['matiere_active']) if coag_info and coag_info['nom'] != "Aucun" else 0
                        floc_actif = calculer_ppm_actif(row['Floculant_ppm_com'], floc_info['matiere_active']) if floc_info and floc_info['nom'] != "Aucun" else 0
                        
                        rapport += f"| {int(row['Essai'])} | {row['Coagulant_ppm_com']:.1f} | {coag_actif:.1f} | {row['Floculant_ppm_com']:.1f} | {floc_actif:.1f} | {row['DCO_entree']:.0f} | {row['DCO_sortie']:.0f} | {row['Abattement']:.1f}% | {row['V_boue']:.1f} |\n"
                
                rapport += f"\n---\n*Rapport généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*"
                
                st.markdown(rapport)
                
                # Téléchargement du rapport en PDF avec les tableaux
                pdf_buffer = generer_rapport_pdf(
                    date_test, operateur, site_prelevement, type_eau, volume_echantillon,
                    temps_coagulation, vitesse_coagulation, temps_floculation, vitesse_floculation,
                    caracteristiques, debit_annuel, meilleur_abattement, coagulants_config, floculants_config,
                    st.session_state.tableau_essais
                )
                
                st.download_button(
                    label="📥 Télécharger le rapport complet (PDF)",
                    data=pdf_buffer,
                    file_name=f"rapport_jar_test_{date_test}.pdf",
                    mime="application/pdf"
                )
                
                # Téléchargement du rapport en TXT
                txt_buffer = io.StringIO()
                txt_buffer.write(rapport)
                
                st.download_button(
                    label="📥 Télécharger le rapport complet (TXT)",
                    data=txt_buffer.getvalue(),
                    file_name=f"rapport_jar_test_{date_test}.txt",
                    mime="text/plain"
                )
            else:
                st.info("Aucune donnée disponible pour la session courante. Veuillez enregistrer des essais dans l'onglet 'Saisie Essais'.")
        else:
            st.info("Aucune donnée dans la base de données. Veuillez enregistrer des essais dans l'onglet 'Saisie Essais'.")

if __name__ == "__main__":
    main()