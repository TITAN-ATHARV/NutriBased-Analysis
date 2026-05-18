# 🥗 Nutri-Score AI Predictor

> An AI-powered nutrition analysis web app that predicts **Nutri-Score grades (A–E)** for food products using **Machine Learning**, barcode scanning, and personalized health recommendations.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web_App-black?style=for-the-badge&logo=flask)
![Machine Learning](https://img.shields.io/badge/Machine_Learning-Random_Forest-green?style=for-the-badge)
![OpenFoodFacts](https://img.shields.io/badge/API-OpenFoodFacts-orange?style=for-the-badge)


**Nutri-Score AI Predictor** is a machine learning-powered health application that helps users evaluate food products based on their nutritional values.

The application predicts a **Nutri-Score grade (A–E)** and provides **personalized health warnings** for users with conditions like:

- Diabetes
- High Blood Pressure
- Heart Disease
- Kidney Disease

Users can either:

✅ Enter nutrition values manually  
✅ Scan/enter product barcodes  
✅ Get instant nutritional grading  
✅ Receive disease-specific dietary warnings

---

## ✨ Features

### 🤖 AI-Powered Nutri-Score Prediction
Uses a trained **Random Forest Machine Learning model** to predict nutritional quality based on food composition.

### 🏷️ Barcode Product Lookup
Fetches product nutrition data instantly using the **OpenFoodFacts API**.

### ❤️ Personalized Health Recommendations
Generates warnings tailored to medical conditions:

- Diabetes
- Heart Disease
- Kidney Disease
- High Blood Pressure

### 📊 Multiple ML Model Comparisons
The project experiments with:

- Logistic Regression
- Support Vector Machine (Linear, Polynomial, RBF)
- Decision Tree
- Random Forest (Best Performer)

### 📈 Data Visualization
Includes:

- Feature importance analysis
- Decision tree visualization
- PCA-based decision boundaries
- Confusion matrices
- Nutritional safe-range graphs

---

## 🛠️ Tech Stack

### Backend
- Python
- Flask

### Machine Learning
- Scikit-learn
- Random Forest
- Logistic Regression
- SVM
- Decision Tree

### Data Processing
- Pandas
- NumPy

### Visualization
- Matplotlib
- Seaborn

### APIs
- OpenFoodFacts API

---

## 🧠 Machine Learning Workflow

The ML pipeline includes:

1. **Data Collection** from OpenFoodFacts dataset  
2. **Feature Selection & Cleaning**  
3. **Missing Value Handling**  
4. **Model Training & Evaluation**  
5. **Performance Comparison**  
6. **Final Model Deployment**

### Input Features Used

- Energy (kcal)
- Sugars
- Saturated Fat
- Fiber
- Proteins
- Salt
- Carbohydrates
- Fruits/Vegetables/Nuts %

### Output

Predicted **Nutri-Score Grade**:

🟢 A → Excellent nutritional quality  
🟡 B → Good nutritional quality  
🟠 C → Average nutritional quality  
🟠 D → Poor nutritional quality  
🔴 E → Bad nutritional quality

