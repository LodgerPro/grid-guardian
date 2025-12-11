"""
XGBoost Model Training for Grid Equipment Failure Prediction
Gradient boosting model for tabular sensor data
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, f1_score
import joblib
import os
import json
from datetime import datetime


class XGBoostTrainer:
    """Train and evaluate XGBoost model for failure prediction"""

    def __init__(self, data_path='data/processed/features.csv'):
        self.data_path = data_path
        self.model = None
        self.feature_names = None
        self.metrics = {}

    def load_data(self):
        """Load preprocessed features"""
        print("Loading data...")
        df = pd.read_csv(self.data_path)

        # Separate features and target
        X = df.drop(['failure', 'timestamp', 'equipment_id'], axis=1, errors='ignore')
        y = df['failure']

        self.feature_names = X.columns.tolist()

        return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    def train_model(self, X_train, y_train, hyperparameter_tuning=False):
        """Train XGBoost model with optional hyperparameter tuning"""
        print("Training XGBoost model...")

        if hyperparameter_tuning:
            print("Performing hyperparameter tuning...")
            param_grid = {
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.1, 0.3],
                'n_estimators': [100, 200, 300],
                'min_child_weight': [1, 3, 5],
                'subsample': [0.8, 1.0],
                'colsample_bytree': [0.8, 1.0]
            }

            xgb_model = xgb.XGBClassifier(
                objective='binary:logistic',
                random_state=42,
                eval_metric='auc'
            )

            grid_search = GridSearchCV(
                xgb_model,
                param_grid,
                cv=5,
                scoring='f1',
                n_jobs=-1,
                verbose=1
            )

            grid_search.fit(X_train, y_train)
            self.model = grid_search.best_estimator_
            print(f"Best parameters: {grid_search.best_params_}")

        else:
            # Use predefined good parameters
            # Calculate class weight (avoid division by zero)
            n_positive = len(y_train[y_train == 1])
            n_negative = len(y_train[y_train == 0])

            if n_positive == 0:
                print("WARNING: No positive samples (failures) in training data!")
                print("   Model will train but may not predict failures accurately.")
                scale_pos_weight = 1.0
            else:
                scale_pos_weight = n_negative / n_positive
                print(f"  Class balance: {n_positive:,} failures / {n_negative:,} normal")
                print(f"  Scale pos weight: {scale_pos_weight:.2f}")

            self.model = xgb.XGBClassifier(
                max_depth=5,
                learning_rate=0.1,
                n_estimators=200,
                min_child_weight=3,
                subsample=0.8,
                colsample_bytree=0.8,
                objective='binary:logistic',
                random_state=42,
                eval_metric='auc',
                scale_pos_weight=scale_pos_weight
            )

            self.model.fit(
                X_train, y_train,
                eval_set=[(X_train, y_train)],
                verbose=False
            )

        print("Training completed!")

    def evaluate_model(self, X_test, y_test):
        """Evaluate model performance"""
        print("\nEvaluating model...")

        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]

        # Calculate metrics
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        f1 = f1_score(y_test, y_pred)

        self.metrics = {
            'roc_auc': float(roc_auc),
            'f1_score': float(f1),
            'classification_report': classification_report(y_test, y_pred, output_dict=True),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }

        print(f"ROC-AUC Score: {roc_auc:.4f}")
        print(f"F1 Score: {f1:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))

        return self.metrics

    def get_feature_importance(self):
        """Extract feature importance"""
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        print("\nTop 10 Important Features:")
        print(importance_df.head(10))

        return importance_df

    def save_model(self, model_dir='models/saved'):
        """Save trained model and metadata"""
        os.makedirs(model_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_path = os.path.join(model_dir, f'xgboost_model_{timestamp}.pkl')
        metadata_path = os.path.join(model_dir, f'xgboost_metadata_{timestamp}.json')

        # Save model
        joblib.dump(self.model, model_path)

        # Save metadata
        metadata = {
            'model_type': 'XGBoost',
            'training_date': timestamp,
            'feature_names': self.feature_names,
            'metrics': self.metrics,
            'model_params': self.model.get_params()
        }

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Also save as latest model
        latest_model_path = os.path.join(model_dir, 'xgboost_model_latest.pkl')
        latest_metadata_path = os.path.join(model_dir, 'xgboost_metadata_latest.json')

        joblib.dump(self.model, latest_model_path)
        with open(latest_metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"\nModel saved to: {model_path}")
        print(f"Metadata saved to: {metadata_path}")
        print(f"Latest model: {latest_model_path}")


def main():
    """Main training pipeline"""
    print("=" * 70)
    print("Grid Guardian - XGBoost Model Training")
    print("=" * 70)

    # Initialize trainer
    trainer = XGBoostTrainer(data_path='data/processed/features.csv')

    # Load data
    X_train, X_test, y_train, y_test = trainer.load_data()
    print(f"\nTraining samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    print(f"Number of features: {X_train.shape[1]}")
    print(f"Failure rate (train): {y_train.mean():.2%}")

    # Train model
    trainer.train_model(X_train, y_train, hyperparameter_tuning=False)

    # Evaluate
    metrics = trainer.evaluate_model(X_test, y_test)

    # Feature importance
    importance_df = trainer.get_feature_importance()

    # Save model
    trainer.save_model()

    print("\n" + "=" * 70)
    print("Training pipeline completed successfully!")
    print("=" * 70)


if __name__ == '__main__':
    main()
