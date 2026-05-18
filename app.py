import os
import sys
import requests
from flask import Flask, render_template, request, jsonify

# Ensure we can import test_product from the same directory
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

import test_product

app = Flask(__name__)

# Try to load the model on startup
if not test_product.load_model("1"):
    if not test_product.load_model("2"):
        print("WARNING: No model loaded! Please train models first by running run_epics.py")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    return jsonify({"status": "ok", "model_loaded": test_product.rf_model is not None})

# Serve PWA static files (manifest, service worker) from static dir
@app.route('/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')

@app.route('/sw.js')
def service_worker():
    return app.send_static_file('sw.js')

DISEASE_LABELS = {
    "none": "No condition",
    "diabetes": "Diabetes",
    "high_blood_pressure": "High blood pressure",
    "heart_disease": "Heart disease",
    "kidney_disease": "Kidney disease",
}

DISEASE_THRESHOLDS = {
    "diabetes": {
        "sugars_100g": [(25, "Very high sugar content — avoid this product."),
                         (12, "High sugar content is not recommended for people with diabetes.")],
    },
    "high_blood_pressure": {
        "salt_100g": [(1.0, "Very high salt content is not recommended for high blood pressure."),
                       (0.5, "High salt content is not ideal for high blood pressure.")],
        "saturated-fat_100g": [(6, "High saturated fat can also worsen blood pressure over time.")],
    },
    "heart_disease": {
        "saturated-fat_100g": [(6, "Very high saturated fat content is risky for heart disease."),
                                (5, "High saturated fat content is risky for heart disease.")],
        "salt_100g": [(0.8, "Very high salt content is not recommended for heart health."),
                       (0.5, "High salt content is not recommended for heart health.")],
    },
    "kidney_disease": {
        "salt_100g": [(0.6, "Very high salt content can stress kidneys."),
                       (0.3, "High salt content can stress kidneys.")],
        "proteins_100g": [(20, "Very high protein content may be hard for kidneys to process.")],
    },
}


def evaluate_health_risk(diseases, values, grade):
    if not diseases:
        diseases = ["none"]

    selected_conditions = [d for d in diseases if d != "none"]
    if not selected_conditions:
        selected_conditions = ["none"]

    disease_names = [DISEASE_LABELS.get(d, "Unknown condition") for d in selected_conditions]
    disease_label = ", ".join(disease_names)
    grade_key = str(grade).strip().lower()
    warnings = []

    if grade_key in ["d", "e"]:
        health_message = "This product is not healthy and should be avoided when possible."
    elif grade_key == "c":
        health_message = "This product is average; choose healthier options when possible."
    else:
        health_message = "This product is generally healthy for most people."

    if selected_conditions != ["none"]:
        for disease in selected_conditions:
            if disease in DISEASE_THRESHOLDS:
                rule_set = DISEASE_THRESHOLDS[disease]
                for feature, thresholds in rule_set.items():
                    value = float(values.get(feature, 0.0) or 0.0)
                    for threshold, message in thresholds:
                        if value >= threshold:
                            if message not in warnings:
                                warnings.append(message)
                            break

            if disease == "diabetes" and float(values.get("fruits-vegetables-nuts-estimate_100g", 0.0) or 0.0) >= 50:
                note = "This product has a good amount of fruits/vegetables/nuts, but sugar remains the main concern."
                if note not in warnings:
                    warnings.append(note)

        if not warnings:
            warnings.append(f"This product is generally acceptable for {disease_label.lower()} based on these nutrient values.")

    return disease_label, health_message, warnings

@app.route('/api/features')
def get_features():
    if not test_product.features:
        return jsonify({"error": "Model not loaded"}), 500
    
    # Return features and their human readable labels
    features_info = []
    for f in test_product.features:
        features_info.append({
            "id": f,
            "label": test_product.FEATURE_LABELS.get(f, f)
        })
    return jsonify({"features": features_info})

@app.route('/api/barcode/<barcode>')
def get_barcode_data(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    headers = {"User-Agent": "NutriScorePredictor/1.0 (local test)"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        if data.get("status") != 1:
            return jsonify({"error": "Product not found"}), 404
        
        product = data.get("product", {})
        nutriments = product.get("nutriments", {})
        
        # Map model feature names to possible API nutriment keys (in priority order)
        FEATURE_API_KEYS = {
            'energy_100g': ['energy-kcal_100g', 'energy-kcal'],
            'energy-kcal_100g': ['energy-kcal_100g', 'energy-kcal'],
            'fiber_100g': ['fiber_100g', 'fiber'],
            'fruits-vegetables-nuts-estimate_100g': [
                'fruits-vegetables-nuts-estimate-from-ingredients_100g',
                'fruits-vegetables-nuts-estimate_100g',
            ],
        }

        # Check if nutriments data is essentially empty
        has_data = any(
            nutriments.get(k) not in (None, "", 0, 0.0)
            for k in nutriments
            if '_100g' in k
        )

        result = {}
        for f in test_product.features:
            val = None
            # Try alternate API keys first
            for alt_key in FEATURE_API_KEYS.get(f, []):
                val = nutriments.get(alt_key)
                if val is not None and val != "":
                    break
            # Fall back to direct key match
            if val is None or val == "":
                val = nutriments.get(f, 0.0)
            # Try without _100g suffix (some products use bare keys)
            if (val is None or val == "" or val == 0) and f.endswith('_100g'):
                bare_key = f.replace('_100g', '')
                val = nutriments.get(bare_key, 0.0)
            if val == "" or val is None:
                val = 0.0
            result[f] = float(val)
            
        response = {
            "product_name": product.get("product_name") or product.get("abbreviated_product_name") or "Unknown Product",
            "image_url": product.get("image_front_url", ""),
            "nutriments": result
        }
        if not has_data:
            response["warning"] = "This product has no nutritional data in the database. Please enter the values manually from the product label."
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    if not test_product.rf_model:
        return jsonify({"error": "Model not loaded on server."}), 500
        
    data = request.json
    if not data or 'values' not in data:
        return jsonify({"error": "No values provided"}), 400
        
    try:
        val_dict = data['values']
        diseases = data.get('diseases', [])
        if not diseases and data.get('disease'):
            diseases = [data.get('disease')]

        ordered_values = []
        for f in test_product.features:
            ordered_values.append(float(val_dict.get(f, 0.0)))
            
        grade = test_product.predict_nutriscore(ordered_values)
        display_info = test_product.get_grade_display(grade)
        disease_name, health_message, warnings = evaluate_health_risk(
            diseases,
            val_dict,
            str(display_info['grade'])
        )
        return jsonify({
            "grade": display_info['grade'],
            "emoji": display_info['emoji'],
            "label": display_info['label'],
            "health_message": health_message,
            "disease": disease_name,
            "warnings": warnings
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port, ssl_context='adhoc')
