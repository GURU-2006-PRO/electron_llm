"""
ML Models for Transaction Analysis
Train models on your data for specific predictions
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os

class TransactionMLModels:
    def __init__(self):
        self.fraud_model = None
        self.failure_model = None
        self.amount_predictor = None
        self.label_encoders = {}
        self.models_trained = False
    
    def train_on_data(self, df):
        """
        Train ML models on your transaction data
        
        Models trained:
        1. Fraud Detection (Classification)
        2. Transaction Failure Prediction (Classification)
        3. Amount Prediction (Regression)
        """
        print("Training ML models on your data...")
        
        # Prepare features
        X, encoders = self._prepare_features(df)
        self.label_encoders = encoders
        
        # Train fraud detection model
        if 'fraud_flag' in df.columns:
            self.fraud_model = self._train_fraud_model(X, df['fraud_flag'])
            print("[OK] Fraud detection model trained")
        
        # Train failure prediction model
        if 'status' in df.columns:
            self.failure_model = self._train_failure_model(X, df['status'])
            print("[OK] Failure prediction model trained")
        
        # Train amount predictor
        if 'amount_inr' in df.columns:
            self.amount_predictor = self._train_amount_predictor(X, df['amount_inr'])
            print("[OK] Amount prediction model trained")
        
        self.models_trained = True
        print("All models trained successfully!")
        
        return {
            "fraud_model": self.fraud_model is not None,
            "failure_model": self.failure_model is not None,
            "amount_predictor": self.amount_predictor is not None
        }
    
    def _prepare_features(self, df):
        """Prepare features for ML models"""
        features = df.copy()
        encoders = {}
        
        # Encode categorical columns
        categorical_cols = ['transaction_type', 'merchant_category', 
                          'payment_method', 'location', 'device_type',
                          'merchant_name', 'customer_gender', 'day_of_week']
        
        for col in categorical_cols:
            if col in features.columns:
                le = LabelEncoder()
                features[col] = le.fit_transform(features[col].astype(str))
                encoders[col] = le
        
        # Select numeric features
        numeric_cols = ['amount_inr', 'customer_age', 'transaction_hour']
        feature_cols = [col for col in categorical_cols + numeric_cols 
                       if col in features.columns]
        
        return features[feature_cols], encoders
    
    def _train_fraud_model(self, X, y):
        """Train fraud detection model"""
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train Random Forest
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # Evaluate
        accuracy = model.score(X_test, y_test)
        print(f"  Fraud model accuracy: {accuracy:.2%}")
        
        return model
    
    def _train_failure_model(self, X, y):
        """Train transaction failure prediction model"""
        # Convert status to binary (success/failure)
        y_binary = (y == 'FAILED').astype(int)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_binary, test_size=0.2, random_state=42
        )
        
        # Train model
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # Evaluate
        accuracy = model.score(X_test, y_test)
        print(f"  Failure model accuracy: {accuracy:.2%}")
        
        return model
    
    def _train_amount_predictor(self, X, y):
        """Train amount prediction model"""
        # Remove amount from features if present
        X_clean = X.drop('amount_inr', axis=1, errors='ignore')
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_clean, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        # Evaluate
        score = model.score(X_test, y_test)
        print(f"  Amount predictor R² score: {score:.2%}")
        
        return model
    
    def predict_fraud(self, transaction_data):
        """Predict if transaction is fraudulent"""
        if not self.fraud_model:
            return {"error": "Fraud model not trained"}
        
        # Prepare features
        features = self._encode_transaction(transaction_data)
        
        # Predict
        fraud_prob = self.fraud_model.predict_proba(features)[0][1]
        is_fraud = fraud_prob > 0.5
        
        return {
            "is_fraud": bool(is_fraud),
            "fraud_probability": float(fraud_prob),
            "risk_level": "HIGH" if fraud_prob > 0.7 else "MEDIUM" if fraud_prob > 0.3 else "LOW"
        }
    
    def predict_failure(self, transaction_data):
        """Predict if transaction will fail"""
        if not self.failure_model:
            return {"error": "Failure model not trained"}
        
        # Prepare features
        features = self._encode_transaction(transaction_data)
        
        # Predict
        failure_prob = self.failure_model.predict_proba(features)[0][1]
        will_fail = failure_prob > 0.5
        
        return {
            "will_fail": bool(will_fail),
            "failure_probability": float(failure_prob),
            "confidence": "HIGH" if abs(failure_prob - 0.5) > 0.3 else "MEDIUM"
        }
    
    def predict_amount(self, transaction_data):
        """Predict transaction amount"""
        if not self.amount_predictor:
            return {"error": "Amount predictor not trained"}
        
        # Prepare features
        features = self._encode_transaction(transaction_data)
        features = features.drop('amount_inr', axis=1, errors='ignore')
        
        # Predict
        predicted_amount = self.amount_predictor.predict(features)[0]
        
        return {
            "predicted_amount": float(predicted_amount),
            "currency": "INR"
        }
    
    def _encode_transaction(self, transaction_data):
        """Encode transaction data for prediction"""
        # Convert to DataFrame
        if isinstance(transaction_data, dict):
            df = pd.DataFrame([transaction_data])
        else:
            df = transaction_data.copy()
        
        # Encode categorical columns
        for col, encoder in self.label_encoders.items():
            if col in df.columns:
                df[col] = encoder.transform(df[col].astype(str))
        
        return df
    
    def save_models(self, path='models/'):
        """Save trained models to disk"""
        os.makedirs(path, exist_ok=True)
        
        if self.fraud_model:
            joblib.dump(self.fraud_model, f'{path}fraud_model.pkl')
        if self.failure_model:
            joblib.dump(self.failure_model, f'{path}failure_model.pkl')
        if self.amount_predictor:
            joblib.dump(self.amount_predictor, f'{path}amount_predictor.pkl')
        
        joblib.dump(self.label_encoders, f'{path}label_encoders.pkl')
        
        print(f"Models saved to {path}")
    
    def load_models(self, path='models/'):
        """Load trained models from disk"""
        try:
            self.fraud_model = joblib.load(f'{path}fraud_model.pkl')
            self.failure_model = joblib.load(f'{path}failure_model.pkl')
            self.amount_predictor = joblib.load(f'{path}amount_predictor.pkl')
            self.label_encoders = joblib.load(f'{path}label_encoders.pkl')
            self.models_trained = True
            print("Models loaded successfully")
            return True
        except Exception as e:
            print(f"Error loading models: {e}")
            return False
    
    def get_feature_importance(self, model_type='fraud'):
        """Get feature importance for interpretability"""
        model = None
        if model_type == 'fraud' and self.fraud_model:
            model = self.fraud_model
        elif model_type == 'failure' and self.failure_model:
            model = self.failure_model
        
        if not model:
            return {"error": "Model not available"}
        
        # Get feature importance
        importance = model.feature_importances_
        feature_names = list(self.label_encoders.keys())
        
        # Sort by importance
        indices = np.argsort(importance)[::-1]
        
        return {
            "features": [feature_names[i] for i in indices[:10]],
            "importance": [float(importance[i]) for i in indices[:10]]
        }
