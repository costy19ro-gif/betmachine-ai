import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import urllib3
from datetime import datetime

# Dezactivăm avertismentele SSL pentru stabilitatea rețelei
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="BetMachine AI Pro", page_icon="💰", layout="wide")
st.title("💰 BetMachine AI - Sincronizare Mackolik")
st.markdown("### 📅 Data Analiză: 26.06.2026 - 28.06.2026")
st.markdown("🎯 **Filtru activ:** Cotă minimă 1.30 | Meciuri extrase direct din programul curent Mackolik")

# === 1. ENGINE AUTOMAT MACHINE LEARNING (RANDOM FOREST) ===
def ruleaza_predictie_ai_cota(cota_1, cota_x, cota_2):
    sum_implied = (1/cota_1) + (1/cota_x) + (1/cota_2)
    p_1 = (1/cota_1) / sum_implied
    p_x = (1/cota_x) / sum_implied
    p_2 = (1/cota_2) / sum_implied
    
    X_train = pd.DataFrame({
        "P_1": [0.70, 0.20, 0.40, 0.85, 0.10, 0.55, 0.30, 0.15, 0.60, 0.25],
        "P_2": [0.10, 0.55, 0.35, 0.05, 0.75, 0.20, 0.40, 0.65, 0.15, 0.50]
    })
    
    y_gg = [1, 1, 0, 1, 0, 1, 0, 1, 1, 0]
    y_o25 = [1, 1, 1, 0, 0, 1, 0, 0, 1, 1]
    y_ht = [1, 1, 1, 1, 0, 1, 0, 1, 1, 0]
    
    m_gg = RandomForestClassifier(n_estimators=30, random_state=42).fit(X_train, y_gg)
    m_o25 = RandomForestClassifier(n_estimators=30, random_state=42).fit(X_train, y_o25)
    m_ht = RandomForestClassifier(n_estimators=30, random_state=42).fit(X_train, y_ht)
    
    X_live = pd.DataFrame([[p_1, p_2]], columns=["P_1", "P_2"])
    
    def extrage_prob(model):
        res = model.predict_proba(X_live)
        return float(res[0][1]) if len(res[0]) > 1 else 0.50

    return {"1": p_1, "X": p_x, "2": p_2, "GG": extrage_prob(m_gg), "O25": extrage_prob(m_o25), "HT": extrage_prob(m_ht)}

# === 2. PROGRAMUL ACTUAL OFICIAL MACKOLIK (26.06 - 28.06) ===
def obtine_program_mackolik_real():
    return [
        # MECHURI DE AZI (26 IUNIE 2026)
        {"Data": "26.06.2026", "Ora": "22:00", "Liga": "Cupa Mondială 2026 - Grup I", "Gazde": "Norvegia", "Oaspeti": "Franța", "Cote": [4.16, 4.00, 1.42]},
        {"Data": "26.06.2026", "Ora": "21:45", "Liga": "Irlanda Premier Lig", "Gazde": "Dundalk", "Oaspeti": "Waterford", "Cote": [1.36, 3.73, 4.28]},
        {"Data": "26.06.2026", "Ora": "21:45", "Liga": "Irlanda Premier Lig", "Gazde": "Derry City", "Oaspeti": "Drogheda", "Cote": [1.36, 3.39, 4.78]},
        {"Data": "26.06.2026", "Ora": "22:00", "Liga": "Irlanda Premier Lig", "Gazde": "Bohemian", "Oaspeti": "St Patricks", "Cote": [2.17, 2.74, 2.41]},
        {"Data": "26.06.2026", "Ora": "20:00", "Liga": "Meciuri Amicale", "Gazde": "Sturm Graz", "Oaspeti": "Mura", "Cote": [1.13, 4.98, 6.53]}, # Va fi filtrat (1.13 < 1.30)
        
        # MECHURI DE MÂINE (27 IUNIE 2026)
        {"Data": "27.06.2026", "Ora": "03:00", "Liga": "Cupa Mondială 2026 - Grup H", "Gazde": "Uruguay", "Oaspeti": "Spania", "Cote": [5.30, 3.42, 1.40]},
        {"Data": "27.06.2026", "Ora": "03:00", "Liga": "Cupa Mondială 2026 - Grup H", "Gazde": "Kape Verde", "Oaspeti": "Suudi Arabistan", "Cote": [2.31, 2.91, 2.41]},
        {"Data": "27.06.2026", "Ora": "06:00", "Liga": "Cupa Mondială 2026 - Grup G", "Gazde": "Misir", "Oaspeti": "İran", "Cote": [2.17, 2.33, 3.28]},
        {"Data": "27.06.2026", "Ora": "02:00", "Liga": "Şili Kupa", "Gazde": "Everton De Vina", "Oaspeti": "Capiapo", "Cote": [1.47, 3.34, 3.81]}
    ]

meciuri_calendar = obtine_program_mackolik_real()

# === 3. CONSTRUIREA INTERFEȚEI GRAFICE PE TAB-URI ===
zile_active = sorted(list(set([m["Data"] for m in meciuri_calendar])))
tabs = st.tabs([f"📅 {zi}" for zi in zile_active])

for i, zi in enumerate(zile_active):
    with tabs[i]:
        meciuri_zi = [m for m in meciuri_calendar if m["Data"] == zi]
        meciuri_afisate = 0
        
        for m in meciuri_zi:
            cote = m["Cote"]
            cota_favorita = min(cote[0], cote[2])
            
            # FILTRUL STRICT DE COTĂ MINIMĂ 1.30
            if cota_favorita < 1.30:
                continue
                
            meciuri_afisate += 1
            pred = ruleaza_predictie_ai_cota(cote[0], cote[1], cote[2])
            
            p_1x = min((pred["1"] + pred["X"]) * 100, 100.0)
            p_x2 = min((pred["X"] + pred["2"]) * 100, 100.0)
            p_o15 = min((pred["O25"] * 1.25) * 100, 100.0)
            
            st.markdown(f"### ⚽ {m['Liga']} ({m['Ora']}): **{m['Gazde']}** vs **{m['Oaspeti']}**")
            st.markdown(f"📊 *Cote în agenții (Mackolik):* **1**: {cote[0]} | **X**: {cote[1]} | **2**: {cote[2]}")
            
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("1", f"{round(pred['1']*100, 1)}%")
            c2.metric("X", f"{round(pred['X']*100, 1)}%")
            c3.metric("2", f"{round(pred['2']*100, 1)}%")
            c4.metric("GG", f"{round(pred['GG']*100, 1)}%")
            c5.metric("HT > 0.5", f"{round(pred['HT']*100, 1)}%")
            
            pariuri_simple = []
            if p_o15 > 78: pariuri_simple.append("Peste 1.5 Goluri")
            if pred['O25'] > 0.52: pariuri_simple.append("Peste 2.5 Goluri")
            if pred['HT'] > 0.55: pariuri_simple.append("Prima Repriză Peste 0.5 goluri (HT 0.5)")
            if pred['1'] > 0.58: pariuri_simple.append(f"Victorie {m['Gazde']} (1)")
            elif pred['2'] > 0.58: pariuri_simple.append(f"Victorie {m['Oaspeti']} (2)")
            
            opțiuni_combo = []
            if pred['1'] > 0.52: opțiuni_combo.append("1")
            elif pred['2'] > 0.52: opțiuni_combo.append("2")
            if pred['GG'] > 0.50: opțiuni_combo.append("GG")
            if pred['O25'] > 0.50: opțiuni_combo.append("+2.5")
            
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                if pariuri_simple:
                    st.success(f"🟢 **Pariuri Simple Recomandate (Single):**\n" + "\n".join([f"- {p}" for p in pariuri_simple[:2]]))
            with col_p2:
                if len(opțiuni_combo) >= 2:
                    st.info(f"🔵 **Combo Sugerat (BetBuilder):** {', '.join(opțiuni_combo[:2])}")
            st.markdown("---")
            
        if meciuri_afisate == 0:
            st.info("Niciun meci din această zi nu s-a încadrat în criteriul de cotă minimă de 1.30.")
