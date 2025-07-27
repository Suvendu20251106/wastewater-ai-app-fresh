import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# --- USER AUTHENTICATION ---
users = {"admin": "admin123", "user1": "user123"}
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.authenticated = True
            st.success("Logged in successfully!")
        else:
            st.error("Invalid credentials")

if not st.session_state.authenticated:
    login()
    st.stop()

# --- Simulated dataset ---
data = pd.DataFrame({
    'pH': [6.5, 9.2, 7.1, 5.5],
    'BOD': [30, 100, 60, 150],
    'COD': [150, 400, 200, 500],
    'TDS': [600, 800, 650, 900],
    'TSS': [200, 300, 250, 350],
    'Usable': ['Yes', 'No', 'Yes', 'No']
})

# --- Train the model ---
le = LabelEncoder()
data['Usable_Label'] = le.fit_transform(data['Usable'])

X = data[['pH', 'BOD', 'COD', 'TDS', 'TSS']]
y = data['Usable_Label']
model = RandomForestClassifier()
model.fit(X, y)

# --- Treatment rules ---
treatment_rules = {
    'acidic': 'Neutralization, Lime Dosing',
    'alkaline': 'Acid Dosing',
    'high_BOD': 'Aerobic Treatment, MBBR',
    'high_COD': 'Advanced Oxidation, Fenton',
    'normal': 'Filtration and UV'
}

# --- App UI ---
st.title("Wastewater Reuse Advisor for Pulp & Paper Industry")
ph = st.slider("pH", 0.0, 14.0, 7.0)
bod = st.number_input("BOD (mg/L)", 0.0)
cod = st.number_input("COD (mg/L)", 0.0)
tds = st.number_input("TDS (mg/L)", 0.0)
tss = st.number_input("TSS (mg/L)", 0.0)

if st.button("Analyze Water"):
    input_data = np.array([[ph, bod, cod, tds, tss]])
    prediction = model.predict(input_data)[0]
    result = le.inverse_transform([prediction])[0]

    # Suggest treatment
    treatment = []
    if ph < 6.5:
        treatment.append(treatment_rules['acidic'])
    elif ph > 8.5:
        treatment.append(treatment_rules['alkaline'])
    if bod > 50:
        treatment.append(treatment_rules['high_BOD'])
    if cod > 250:
        treatment.append(treatment_rules['high_COD'])
    if not treatment:
        treatment.append(treatment_rules['normal'])

    st.subheader(f"Water Usable: {result}")
    st.write("Suggested Treatment:", ", ".join(treatment))

    # Export result
    result_data = {
        'pH': ph, 'BOD': bod, 'COD': cod, 'TDS': tds, 'TSS': tss,
        'Usable': result,
        'Suggested Treatment': ", ".join(treatment)
    }
    df_result = pd.DataFrame([result_data])
    csv = df_result.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Report as CSV",
        data=csv,
        file_name='wastewater_analysis_result.csv',
        mime='text/csv'
    )
