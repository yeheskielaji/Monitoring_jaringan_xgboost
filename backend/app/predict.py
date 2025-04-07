import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import IncrementalPCA
from xgboost import XGBClassifier
import time

# Memuat model PCA dan XGBoost yang telah dilatih
ipca = joblib.load('models/pca_model.pkl')  # Memuat model PCA
xgb_model = joblib.load('models/xgb_model_smote.pkl')  # Memuat model XGBoost

# Memuat dataset untuk memproses data uji
dataset_path = 'data/CICIDS2017.csv'  # Dataset yang diberikan
data = pd.read_csv(dataset_path)

# Langkah 1: Menghilangkan spasi pada nama kolom
col_names = {col: col.strip() for col in data.columns}
data.rename(columns=col_names, inplace=True)

# Langkah 2: Mengganti nilai infinity (inf) dengan NaN
data.replace([np.inf, -np.inf], np.nan, inplace=True)

# Langkah 3: Menghitung missing values dan mengisi missing values
missing = data.isna().sum()
numeric_columns = data.select_dtypes(include=[np.number]).columns
data[numeric_columns] = data[numeric_columns].fillna(data[numeric_columns].median())  # Mengisi NaN numerik dengan median
categorical_columns = data.select_dtypes(exclude=[np.number]).columns
for col in categorical_columns:
    data[col].fillna(data[col].mode()[0], inplace=True)  # Mengisi NaN kategorikal dengan modus

# Langkah 4: Menghapus kolom dengan hanya satu nilai unik
num_unique = data.nunique()
one_variable = num_unique[num_unique == 1]
not_one_variable = num_unique[num_unique > 1].index
dropped_cols = one_variable.index
data = data[not_one_variable]

# Langkah 5: Membuat mapping untuk jenis serangan berdasarkan kolom 'Label'
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

# Langkah 6: Menambahkan kolom 'Attack Type' di DataFrame berdasarkan attack_map
data['Attack Type'] = data['Label'].map(attack_map)

# Langkah 7: Melakukan encoding hanya pada 'Label' (kolom target)
le_label = LabelEncoder()
data['Label'] = le_label.fit_transform(data['Attack Type'])  # Encode Label

# Langkah 8: Memisahkan fitur dan target (Label)
X = data.drop(['Label', 'Attack Type', 'Bwd URG Flags', 'Bwd PSH Flags'], axis=1)  
y = data['Label']  # Menyimpan 'Label' sebagai target

# Langkah 9: Melakukan scaling pada fitur
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Menyimpan scaler agar bisa digunakan untuk data uji nanti
joblib.dump(scaler, 'models/scaler.pkl')

def get_prediction(row_index):
    """Fungsi untuk mendapatkan prediksi berdasarkan row_index yang diberikan"""
    row_data = X.iloc[row_index].values.reshape(1, -1)

    # Lakukan scaling pada data tersebut
    scaled_row = scaler.transform(row_data)

    # Terapkan PCA pada data yang sudah diskalakan
    pca_features = ipca.transform(scaled_row)

    # Prediksi dengan model XGBoost
    prediction = xgb_model.predict(pca_features)

    # Ambil original_label yang sudah disimpan sebelumnya
    original_label = data.iloc[row_index]['Attack Type']  # Ambil dari kolom 'Attack Type'

    # Inverse transform untuk mendapatkan label asli
    prediction_output = le_label.inverse_transform([prediction[0]])[0]

    # Mapping hasil prediksi ke kategori yang lebih umum menggunakan attack_map
    attack_type_mapped = attack_map.get(prediction_output, prediction_output)  # Mapping original label ke kategori umum

    # Menyimpan label asli, fitur tambahan yang diminta, dan hasil prediksi
    flow_packets_s = row_data[0, X.columns.get_loc('Flow Packets/s')]
    flow_bytes_s = row_data[0, X.columns.get_loc('Flow Bytes/s')]
    total_fwd= row_data[0, X.columns.get_loc('Total Fwd Packets')]
    total_bwd= row_data[0, X.columns.get_loc('Total Backward Packets')]
    destination_port= row_data[0, X.columns.get_loc('Destination Port')]

    return {
        'prediction': attack_type_mapped,
        'original_label': original_label, 
        'flow_packets_s': flow_packets_s,
        'flow_bytes_s': flow_bytes_s,
        'total_fwd':total_fwd,
        'total_bwd':total_bwd,
        'destination_port':destination_port,
        'message': 'Prediction successful'
    }
