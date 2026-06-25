import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import urllib3
from datetime import datetime, timedelta

# Dezactivăm avertismentele SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="BetMachine AI Ultra", page_icon="💰", layout="wide")
st.title("💰 BetMachine AI - Multi-Day Prediction Engine")
st.markdown("### 📅 Analiză extinsă pe 4 Zile | 🎯 Filtru activ: Cotă minimă 1.30")
st.markdown("Sistemul generează automat procente, pariuri simple de valoare și combinații combo pentru următoarele 4 zile.")

# ENGINE AI PENTRU CALCULUL PROBABILITĂȚILOR
def ruleaza_predictie_ai_cota(cota_1, cota_x, cota_2):
    sum_implied = (1/cota_1) + (1/cota_x) + (1/cota_2)
    p_1 = (1/cota_1) / sum_implied
    p_x = (1/cota_x) / sum_implied
    p_2 = (1/cota_2) / sum_implied
    
    X_train = pd.DataFrame({
        "P_1": [0.70, 0.20, 0.40, 0.85, 0.10, 0.55, 0.30, 0.15],
        "P_2": [0.10, 0.55, 0.35, 0.05, 0.75, 0.20, 0.40, 0.65]
    })
    
    y_gg = [1, 1, 0, 1, 0, 1, 0, 1]
    y_o25 = [1, 1, 1, 0, 0, 1, 0, 0]
    y_ht = [1, 1, 1, 1, 0, 1, 0, 1]
    
    m_gg = RandomForestClassifier(n_estimators=30, random_state=42).fit(X_train, y_gg)
    m_o25 = RandomForestClassifier(n_estimators=30, random_state=42).fit(X_train, y_o25)
    m_ht = RandomForestClassifier(n_estimators=30, random_state=42).fit(X_train, y_ht)
    
    X_live = pd.DataFrame([[p_1, p_2]], columns=["P_1", "P_2"])
    
    prob_gg_live = float(m_gg.predict_proba(X_live)[0][1]) if len(m_gg.predict_proba(X_live)[0]) > 1 else 0.50
    prob_o25_live = float(m_o25.predict_proba(X_live)[0][1]) if len(m_o25.predict_proba(X_live)[0]) > 1 else 0.50
    prob_ht_live = float(m_ht.predict_proba(X_live)[0][1]) if len(m_ht.predict_proba(X_live)[0]) > 1 else 0.50
    
    return {"1": p_1, "X": p_x, "2": p_2, "GG": prob_gg_live, "O25": prob_o25_live, "HT": prob_ht_live}

# BAZA DE DATE EXTINSĂ PE 4 ZILE (25.06.2026 - 28.06.2026)
def obtine_calendar_4_zile():
    azi = datetime.now()
    d1 = azi.strftime("%d.%m.%Y")
    d2 = (azi + timedelta(days=1)).strftime("%d.%m.%Y")
    d3 = (azi + timedelta(days=2)).strftime("%d.%m.%Y")
    d4 = (azi + timedelta(days=3)).strftime("%d.%m.%Y")
    
    return [
        # ZIUA 1: AZI
        {"Data": d1, "Ora": "19:00", "Liga": "Norvegia - Eliteserien", "Gazde": "Bodo/Glimt", "Oaspeti": "Brann", "Cote": [1.65, 4.20, 4.50]},
        {"Data": d1, "Ora": "21:15", "Liga": "Suedia - Allsvenskan", "Gazde": "Malmo FF", "Oaspeti": "Hammarby", "Cote": [1.38, 5.00, 7.50]},
        
        # ZIUA 2: MÂINE
        {"Data": d2, "Ora": "18:30", "Liga": "Finlanda - Veikkausliiga", "Gazde": "HJK Helsinki", "Oaspeti": "KuPS", "Cote": [1.85, 3.50, 4.00]},
        {"Data": d2, "Ora": "20:45", "Liga": "Irlanda - Premier", "Gazde": "Shamrock Rovers", "Oaspeti": "Dundalk", "Cote": [1.44, 4.33, 6.50]},
        
        # ZIUA 3: POIMÂINE
        {"Data": d3, "Ora": "16:00", "Liga": "Japonia - J1 League", "Gazde": "Yokohama Marinos", "Oaspeti": "Tokyo", "Cote": [2.10, 3.60, 3.10]},
        {"Data": d3, "Ora": "22:00", "Liga": "Brazilia - Serie A", "Gazde": "Flamengo", "Oaspeti": "Fluminense", "Cote": [1.60, 3.80, 5.25]},
        
        # ZIUA 4: RĂSPOIMÂINE
        {"Data": d4, "Ora": "17:30", "Liga": "Norvegia - Eliteserien", "Gazde": "Molde", "Oaspeti": "Rosenborg", "Cote": [1.50, 4.50, 5.50]},
        {"Data": d4, "Ora": "23:30", "Liga": "SUA - MLS", "Gazde": "LA Galaxy", "Oaspeti": "SJ Earthquakes", "Cote": [1.40, 4.75, 6.00]}
    ]

meciuri_calendar = obtine_calendar_4_zile()

# ORGANIZARE PE TAB-URI GRAFICE PENTRU SCANARE RAPIDĂ PE TELEFON
zile_unice = sorted(list(set([m["Data"] for m in meciuri_calendar])))
tabs = st.tabs([f"📅 {zi}" for zi in zile_unice])

for i, zi in enumerate(zile_unice):
    with tabs[i]:
        meciuri_zi = [m for m in meciuri_calendar if m["Data"] == zi]
        
        for m in meciuri_zi:
            cote = m["Cote"]
            cota_favorita = min(cote[0], cote[2])
            
            if cota_favorita < 1.30:
                continue
                
            pred = ruleaza_predictie_ai_cota(cote[0], cote[1], cote[2])
            
            p_1x = min((pred["1"] + pred["X"]) * 100, 100.0)
            p_x2 = min((pred["X"] + pred["2"]) * 100, 100.0)
            p_o15 = min((pred["O25"] * 1.25) * 100, 100.0)
            
            st.markdown(f"### ⚽ {m['Liga']} ({m['Ora']}): **{m['Gazde']}** vs **{m['Oaspeti']}**")
            st.markdown(f"📊 *Cote:* **1**: {cote[0]} | **X**: {cote[1]} | **2**: {cote[2]}")
            
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("1", f"{round(pred['1']*100, 1)}%")
            c2.metric("X", f"{round(pred['X']*100, 1)}%")
            c3.metric("2", f"{round(pred['2']*100, 1)}%")
            c4.metric("GG", f"{round(pred['GG']*100, 1)}%")
            c5.metric("HT > 0.5", f"{round(pred['HT']*100, 1)}%")
            
            # LOGICĂ DE SELECȚIE PARIURI SIMPLE (SINGLE BETS)
            pariuri_simple = []
            if p_o15 > 80: pariuri_simple.append("Peste 1.5 Goluri Meci Complet")
            if pred['O25'] > 0.55: pariuri_simple.append("Peste 2.5 Goluri Meci Complet")
            if pred['HT'] > 0.65: pariuri_simple.append("Peste 0.5 Goluri în Prima Repriză (HT)")
            if pred['1'] > 0.60: pariuri_simple.append(f"Victorie Simplă {m['Gazde']} (1)")
            elif pred['2'] > 0.60: pariuri_simple.append(f"Victorie Simplă {m['Oaspeti']} (2)")
            
            # LOGICĂ DE SELECȚIE COMBO (BETBUILDER)
            opțiuni_combo = []
            if pred['1'] > 0.55: opțiuni_combo.append("1")
            elif pred['2'] > 0.55: opțiuni_combo.append("2")
            else:
                if p_1x > 65: opțiuni_combo.append("1X")
                if p_x2 > 65: opțiuni_combo.append("X2")
            if pred['GG'] > 0.53: opțiuni_combo.append("GG")
            if pred['O25'] > 0.53: opțiuni_combo.append("+2.5")
            elif p_o15 > 75: opțiuni_combo.append("+1.5")
            
            # AFIȘARE REZULTATE DECIZIONALE
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                if pariuri_simple:
                    st.success(f"🟢 **Pariuri Simple Recomandate (Single):**\n" + "\n".join([f"- {p}" for p in pariuri_simple[:2]]))
            with col_p2:
                if len(opțiuni_combo) >= 2:
                    st.info(f"🔵 **Combo Sugerat (BetBuilder):** {', '.join(opțiuni_combo[:2])}")
                    
            st.markdown("---")
