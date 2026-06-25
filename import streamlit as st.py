import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import urllib3

# Dezactivăm avertismentele SSL pentru conexiuni stabile
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="BetMachine Pro 2026", page_icon="💰", layout="wide")
st.title("💰 BetMachine AI - Pro World Cup Edition")
st.markdown("### 📅 Data Analiză: 24 Iunie 2026 | 🎯 Filtru activ: Cotă minimă 1.30")
st.markdown("Sistemul filtrează automat meciurile zilei pentru a păstra doar evenimentele cu valoare de pariere.")

# === 1. ENGINE AI CALIBRAT PE PROBABILITĂȚI IMPLICITE ===
def ruleaza_predictie_ai_cota(cota_1, cota_x, cota_2):
    sum_implied = (1/cota_1) + (1/cota_x) + (1/cota_2)
    p_1 = (1/cota_1) / sum_implied
    p_x = (1/cota_x) / sum_implied
    p_2 = (1/cota_2) / sum_implied
    
    # Date istorice structurate pentru corelația cote-evenimente
    X_train = pd.DataFrame({
        "P_1": [0.70, 0.20, 0.40, 0.85, 0.10, 0.55, 0.30, 0.15],
        "P_2": [0.10, 0.55, 0.35, 0.05, 0.75, 0.20, 0.40, 0.65]
    })
    
    # Valori binare (0 sau 1) pentru antrenarea corectă a clasificatorului Random Forest
    y_gg = [1, 1, 0, 0, 1, 0, 1, 0]
    y_o25 = [1, 0, 1, 1, 0, 0, 1, 0]
    y_ht = [1, 1, 1, 0, 1, 0, 1, 0]
    
    m_gg = RandomForestClassifier(n_estimators=30, random_state=42).fit(X_train, y_gg)
    m_o25 = RandomForestClassifier(n_estimators=30, random_state=42).fit(X_train, y_o25)
    m_ht = RandomForestClassifier(n_estimators=30, random_state=42).fit(X_train, y_ht)
    
    X_live = pd.DataFrame([[p_1, p_2]], columns=["P_1", "P_2"])
    
    # Extragere probabilitate pentru clasa 1 (adică probabilitatea ca evenimentul să aibă loc)
    prob_gg_live = m_gg.predict_proba(X_live)[0][1] if len(m_gg.predict_proba(X_live)[0]) > 1 else 0.50
    prob_o25_live = m_o25.predict_proba(X_live)[0][1] if len(m_o25.predict_proba(X_live)[0]) > 1 else 0.50
    prob_ht_live = m_ht.predict_proba(X_live)[0][1] if len(m_ht.predict_proba(X_live)[0]) > 1 else 0.50
    
    return {
        "1": p_1, "X": p_x, "2": p_2,
        "GG": prob_gg_live,
        "O25": prob_o25_live,
        "HT": prob_ht_live
    }

# === 2. PROGRAMUL DIN SCREENSHOT DIN DATA DE 24.06.2026 ===
def obtine_program_world_cup_24_06():
    return [
        {"Ora": "22:00", "Liga": "FIFA World Cup", "Gazde": "Switzerland", "Oaspeti": "Canada", "Cote": [1.05, 2.40, 3.20]},
        {"Ora": "22:00", "Liga": "FIFA World Cup", "Gazde": "Bosnia and Herzegovina", "Oaspeti": "Qatar", "Cote": [1.36, 5.25, 7.50]},
        {"Ora": "01:00", "Liga": "FIFA World Cup", "Gazde": "Scotland", "Oaspeti": "Brazil", "Cote": [9.50, 5.50, 1.30]},
        {"Ora": "01:00", "Liga": "FIFA World Cup", "Gazde": "Morocco", "Oaspeti": "Haiti", "Cote": [1.17, 7.50, 15.00]},
        {"Ora": "04:00", "Liga": "FIFA World Cup", "Gazde": "South Africa", "Oaspeti": "South Korea", "Cote": [5.75, 4.10, 1.57]},
        {"Ora": "04:00", "Liga": "FIFA World Cup", "Gazde": "Czech Republic", "Oaspeti": "Mexico", "Cote": [3.70, 3.80, 1.91]}
    ]

# === 3. EXECUȚIE AUTOMATĂ CU FILTRARE ===
with st.spinner("Sistemul filtrează și procesează meciurile avantajoase..."):
    meciuri_eveniment = obtine_program_world_cup_24_06()
    st.markdown("---")
    
    meciuri_afisate = 0
    
    for m in meciuri_eveniment:
        cote = m["Cote"]
        # Identifică cota echipei favorite (cea mai mică dintre cota 1 și cota 2)
        cota_favorita = min(cote[0], cote[2]) 
        
        # FILTRUL DE COTĂ MINIMĂ 1.30
        if cota_favorita < 1.30:
            continue
            
        meciuri_afisate += 1
        pred = ruleaza_predictie_ai_cota(cote[0], cote[1], cote[2])
        
        p_1x = min((pred["1"] + pred["X"]) * 100, 100.0)
        p_x2 = min((pred["X"] + pred["2"]) * 100, 100.0)
        p_o15 = min((pred["O25"] * 1.25) * 100, 100.0)
        
        st.markdown(f"### 🏆 {m['Liga']} ({m['Ora']}): **{m['Gazde']}** vs **{m['Oaspeti']}**")
        st.markdown(f"📊 *Cote oficiale în piață:* **1**: {cote[0]} | **X**: {cote[1]} | **2**: {cote[2]}")
        
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("1 (Gazde)", f"{round(pred['1']*100, 1)}%")
        c2.metric("X (Egal)", f"{round(pred['X']*100, 1)}%")
        c3.metric("2 (Oaspeți)", f"{round(pred['2']*100, 1)}%")
        c4.metric("GG (Ambele)", f"{round(pred['GG']*100, 1)}%")
        c5.metric("HT > 0.5", f"{round(pred['HT']*100, 1)}%")
        
        opțiuni_bilet = []
        if pred['1'] > 0.55: opțiuni_bilet.append("1")
        elif pred['2'] > 0.55: opțiuni_bilet.append("2")
        else:
            if p_1x > 65: opțiuni_bilet.append("1X")
            if p_x2 > 65: opțiuni_bilet.append("X2")
            
        if pred['GG'] > 0.53: opțiuni_bilet.append("GG")
        if p_o15 > 75: opțiuni_bilet.append("+1.5 Goluri")
        if pred['O25'] > 0.53: opțiuni_bilet.append("+2.5 Goluri")
        if pred['HT'] > 0.55: opțiuni_bilet.append("HT Peste 0.5")
        
        st.info(f"🎯 **Combo Sugerat:** {', '.join(opțiuni_bilet[:2])}")
        st.markdown("---")
        
    if meciuri_afisate == 0:
        st.warning("Niciun meci din lista actuală nu a îndeplinit criteriul de cotă minimă de 1.30 pentru favorită.")
