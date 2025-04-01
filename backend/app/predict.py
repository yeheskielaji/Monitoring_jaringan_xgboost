import joblib
import pandas as pd
import numpy as np
from flask import request, jsonify
from app import create_app

app = create_app()

# Load pre-trained model and dataset
model = joblib.load('models/xgb_model_smote.pkl')
data = pd.read_csv('data/CICIDS2017.csv')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Ambil data input dari request JSON
        input_data = request.get_json(force=True)
        
        # Ubah input menjadi numpy array
        features = np.array([
            input_data['feature1'],
            input_data['feature2'],
            input_data['feature3'],
            input_data['feature4'],
            input_data['feature5']
        ])

        # Prediksi dengan model XGBoost
        prediction = model.predict(features.reshape(1, -1))
        
        # Ambil baris pertama dari dataset untuk contoh data tambahan
        predicted_row = data.iloc[0]
        ip_address = predicted_row['IP']
        timestamp = predicted_row['Timestamp']
        protocol = predicted_row['Protocol']
        
        # Kembalikan hasil prediksi dan data tambahan
        response = {
            'prediction': prediction[0],
            'IP': ip_address,
            'Timestamp': timestamp,
            'Protocol': protocol
        }
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
