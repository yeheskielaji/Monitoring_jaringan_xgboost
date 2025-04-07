import streamlit as st
import pandas as pd
import numpy as np
import joblib
import time
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import IncrementalPCA
from xgboost import XGBClassifier

# Memuat model PCA, XGBoost, dan Scaler
ipca = joblib.load('models/pca_model.pkl')
xgb_model = joblib.load('models/xgb_model_smote.pkl')
scaler = joblib.load('models/scaler.pkl')

# Memuat dataset
dataset_path = 'data/CICIDS2017.csv'
data = pd.read_csv(dataset_path)

# Preprocessing data
col_names = {col: col.strip() for col in data.columns}
data.rename(columns=col_names, inplace=True)
data.replace([np.inf, -np.inf], np.nan, inplace=True)
numeric_columns = data.select_dtypes(include=[np.number]).columns
data[numeric_columns] = data[numeric_columns].fillna(data[numeric_columns].median())
categorical_columns = data.select_dtypes(exclude=[np.number]).columns
for col in categorical_columns:
    data[col].fillna(data[col].mode()[0], inplace=True)
num_unique = data.nunique()
one_variable = num_unique[num_unique == 1]
not_one_variable = num_unique[num_unique > 1].index
data = data[not_one_variable]

attack_map = {
    'BENIGN': 'BENIGN',
    'DDoS': 'DDoS',
    'DoS Hulk': 'DoS',
    'DoS GoldenEye': 'DoS',
    'DoS slowloris': 'DoS',
    'DoS Slowhttptest': 'DoS',
    'PortScan': 'Port Scan',
    'FTP-Patator': 'Brute Force',
    'SSH-Patator': 'Brute Force',
    'Bot': 'Bot',
    'Web Attack � Brute Force': 'Web Attack',
    'Web Attack � XSS': 'Web Attack',
    'Web Attack � Sql Injection': 'Web Attack',
    'Infiltration': 'Infiltration',
    'Heartbleed': 'Heartbleed'
}

data['Attack Type'] = data['Label'].map(attack_map)
le_label = LabelEncoder()
data['Label'] = le_label.fit_transform(data['Label'])

X = data.drop(['Label', 'Attack Type', 'Bwd URG Flags', 'Bwd PSH Flags'], axis=1)
y = data['Label']
X_scaled = scaler.transform(X)

# Fungsi untuk prediksi
def predict_attack(row_index):
    try:
        row_data = X.iloc[row_index].values.reshape(1, -1)
        scaled_row = scaler.transform(row_data)
        pca_features = ipca.transform(scaled_row)
        prediction = xgb_model.predict(pca_features)
        original_label = le_label.inverse_transform([prediction[0]])[0]
        attack_type_mapped = attack_map.get(original_label, original_label)
        return attack_type_mapped
    except Exception as e:
        return str(e)

# Menampilkan informasi di Streamlit
st.set_page_config(page_title="Monitoring Jaringan dengan Deteksi Serangan", layout="wide")
st.title("Monitoring Jaringan dengan Deteksi Serangan")

# Membagi layar menjadi dua kolom
col1, col2 = st.columns([2, 1])

with col1:
    # Menampilkan grafik Flow Packets/s
    st.subheader("Grafik Flow Packets/s")
    st.line_chart(data['Flow Packets/s'])

    # Menampilkan grafik SYN Flag Count
    st.subheader("Grafik SYN Flag Count")
    st.line_chart(data['SYN Flag Count'])

    # Menampilkan histogram Packet Length Distribution
    st.subheader("Distribusi Panjang Paket")
    st.bar_chart(data['Packet Length Std'])

with col2:
    # Menampilkan diagram batang klasifikasi serangan
    st.subheader("Diagram Batang Klasifikasi Serangan")
    attack_labels_xgb = [predict_attack(i) for i in range(len(data))]
    attack_labels_db = data['Attack Type'].values
    df_attack_comparison = pd.DataFrame({
        'Label Asli': attack_labels_db,
        'Prediksi XGBoost': attack_labels_xgb
    })

    # Menambahkan Pie Chart untuk hasil klasifikasi
    st.subheader("Hasil Klasifikasi Serangan")
    attack_counts_db = pd.Series(attack_labels_db).value_counts()
    attack_counts_xgb = pd.Series(attack_labels_xgb).value_counts()
    fig, ax = plt.subplots(figsize=(8, 6))
    width = 0.35
    x = np.arange(len(attack_counts_db))

    # Membuat diagram batang untuk perbandingan
    ax.bar(x - width/2, attack_counts_db, width, label='Label Asli')
    ax.bar(x + width/2, attack_counts_xgb, width, label='Prediksi XGBoost')
    ax.set_xlabel('Jenis Serangan')
    ax.set_ylabel('Jumlah Kasus')
    ax.set_title('Perbandingan Klasifikasi Serangan')
    ax.set_xticks(x)
    ax.set_xticklabels(attack_counts_db.index, rotation=45, ha='right')
    ax.legend()
    st.pyplot(fig)

    # Membuat Pie Chart dari hasil klasifikasi
    st.subheader("Distribusi Jenis Serangan (Pie Chart)")
    fig_pie, ax_pie = plt.subplots(figsize=(6, 6))
    attack_counts_pie = pd.Series(attack_labels_xgb).value_counts()
    ax_pie.pie(attack_counts_pie, labels=attack_counts_pie.index, autopct='%1.1f%%', startangle=90, colors=["#00FF00", "#FF9900", "#FF3300", "#6600CC"])
    ax_pie.axis('equal')  # Equal aspect ratio ensures that pie chart is circular.
    st.pyplot(fig_pie)

# Alarm Notifikasi
st.subheader("Alarm Notifikasi")
# Simulasikan deteksi serangan jika jumlah prediksi tertentu lebih besar dari ambang batas
alarms = pd.Series(attack_labels_xgb).value_counts()
if alarms.get('DDoS', 0) > 10:  # Contoh alarm jika DDoS lebih dari 10 kali
    st.warning("ALERT: Terjadi Serangan DDoS!")

# Riwayat Alarm
st.subheader("Riwayat Alarm")
alarm_history = [
    {"time": "21 Feb 2019 04:50:27", "message": "Deteksi Serangan DDoS"},
    {"time": "21 Feb 2019 04:55:34", "message": "Deteksi PortScan"},
    {"time": "21 Feb 2019 04:56:34", "message": "Deteksi Serangan Bot"}
]
for alarm in alarm_history:
    st.write(f"{alarm['time']} - {alarm['message']}")

with elements("nivo_charts"):

    # Streamlit Elements includes 45 dataviz components powered by Nivo.

    from streamlit_elements import nivo

    DATA = [
        { "taste": "fruity", "chardonay": 93, "carmenere": 61, "syrah": 114 },
        { "taste": "bitter", "chardonay": 91, "carmenere": 37, "syrah": 72 },
        { "taste": "heavy", "chardonay": 56, "carmenere": 95, "syrah": 99 },
        { "taste": "strong", "chardonay": 64, "carmenere": 90, "syrah": 30 },
        { "taste": "sunny", "chardonay": 119, "carmenere": 94, "syrah": 103 },
    ]

    with mui.Box(sx={"height": 500}):
        nivo.Radar(
            data=DATA,
            keys=[ "chardonay", "carmenere", "syrah" ],
            indexBy="taste",
            valueFormat=">-.2f",
            margin={ "top": 70, "right": 80, "bottom": 40, "left": 80 },
            borderColor={ "from": "color" },
            gridLabelOffset=36,
            dotSize=10,
            dotColor={ "theme": "background" },
            dotBorderWidth=2,
            motionConfig="wobbly",
            legends=[
                {
                    "anchor": "top-left",
                    "direction": "column",
                    "translateX": -50,
                    "translateY": -40,
                    "itemWidth": 80,
                    "itemHeight": 20,
                    "itemTextColor": "#999",
                    "symbolSize": 12,
                    "symbolShape": "circle",
                    "effects": [
                        {
                            "on": "hover",
                            "style": {
                                "itemTextColor": "#000"
                            }
                        }
                    ]
                }
            ],
            theme={
                "background": "#FFFFFF",
                "textColor": "#31333F",
                "tooltip": {
                    "container": {
                        "background": "#FFFFFF",
                        "color": "#31333F",
                    }
                }
            }
        )