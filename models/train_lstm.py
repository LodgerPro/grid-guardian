"""
LSTM Model Training for Grid Equipment Failure Prediction
Deep learning model for time-series sensor data
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, f1_score
import joblib
import os
import json
from datetime import datetime


class LSTMTrainer:
    """Train and evaluate LSTM model for failure prediction"""

    def __init__(self, data_path='data/processed/features.csv', sequence_length=24):
        self.data_path = data_path
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = StandardScaler()
        self.metrics = {}
        self.feature_names = None

    def load_and_prepare_sequences(self):
        """Load data and create sequences for LSTM"""
        print("Loading and preparing sequences...")
        df = pd.read_csv(self.data_path)

        # Sort by equipment and timestamp
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values(['equipment_id', 'timestamp'])

        # Select features - use only most important ones to reduce memory
        # Priority: sensor readings over engineered features
        priority_features = [
            'temperature_top', 'temperature_oil',
            'voltage_phase_a', 'voltage_phase_b', 'voltage_phase_c',
            'current_phase_a', 'current_phase_b', 'current_phase_c',
            'gas_h2', 'gas_ch4', 'gas_c2h2',
            'vibration_x', 'vibration_y', 'vibration_z',
            'humidity', 'load_percentage'
        ]

        # Use only features that exist in the dataframe
        feature_cols = [col for col in priority_features if col in df.columns]

        if len(feature_cols) == 0:
            # Fallback to all numeric columns (but limit to 20)
            all_features = [col for col in df.columns
                          if col not in ['failure', 'timestamp', 'equipment_id']]
            feature_cols = all_features[:20]

        self.feature_names = feature_cols
        print(f"  Using {len(feature_cols)} features (reduced for memory efficiency)")
        print(f"  Features: {feature_cols[:5]}...")

        # Create sequences
        X_sequences = []
        y_labels = []

        if 'equipment_id' in df.columns:
            # Group by equipment to maintain temporal continuity
            for equipment_id, group in df.groupby('equipment_id'):
                X_eq = group[feature_cols].values
                y_eq = group['failure'].values

                for i in range(len(X_eq) - self.sequence_length):
                    X_sequences.append(X_eq[i:i + self.sequence_length])
                    y_labels.append(y_eq[i + self.sequence_length])
        else:
            # No equipment grouping
            X = df[feature_cols].values
            y = df['failure'].values

            for i in range(len(X) - self.sequence_length):
                X_sequences.append(X[i:i + self.sequence_length])
                y_labels.append(y[i + self.sequence_length])

        X_sequences = np.array(X_sequences)
        y_labels = np.array(y_labels)

        print(f"Created {len(X_sequences)} sequences")
        print(f"Sequence shape: {X_sequences.shape}")

        # Scale features
        n_samples, n_steps, n_features = X_sequences.shape
        X_reshaped = X_sequences.reshape(-1, n_features)
        X_scaled = self.scaler.fit_transform(X_reshaped)
        X_sequences = X_scaled.reshape(n_samples, n_steps, n_features)

        return train_test_split(X_sequences, y_labels,
                              test_size=0.2, random_state=42, stratify=y_labels)

    def build_model(self, input_shape):
        """Build LSTM architecture"""
        print("Building LSTM model...")

        model = keras.Sequential([
            keras.layers.LSTM(128, return_sequences=True, input_shape=input_shape),
            keras.layers.Dropout(0.3),
            keras.layers.LSTM(64, return_sequences=True),
            keras.layers.Dropout(0.3),
            keras.layers.LSTM(32),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(1, activation='sigmoid')
        ])

        # Compile with class weights for imbalanced data
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.AUC(name='auc'),
                    keras.metrics.Precision(name='precision'),
                    keras.metrics.Recall(name='recall')]
        )

        print(model.summary())
        return model

    def train_model(self, X_train, y_train, X_val, y_val, epochs=50):
        """Train LSTM model"""
        print("Training LSTM model...")

        # Calculate class weights
        neg_count = np.sum(y_train == 0)
        pos_count = np.sum(y_train == 1)
        class_weight = {0: 1.0, 1: neg_count / pos_count}

        print(f"Class weights: {class_weight}")

        # Build model
        input_shape = (X_train.shape[1], X_train.shape[2])
        self.model = self.build_model(input_shape)

        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_auc',
                patience=10,
                restore_best_weights=True,
                mode='max'
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6
            )
        ]

        # Train
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=32,
            class_weight=class_weight,
            callbacks=callbacks,
            verbose=1
        )

        print("Training completed!")
        return history

    def evaluate_model(self, X_test, y_test):
        """Evaluate model performance"""
        print("\nEvaluating model...")

        # Predictions
        y_pred_proba = self.model.predict(X_test, verbose=0).flatten()
        y_pred = (y_pred_proba > 0.5).astype(int)

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

    def save_model(self, model_dir='models/saved'):
        """Save trained model and metadata"""
        os.makedirs(model_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_path = os.path.join(model_dir, f'lstm_model_{timestamp}.h5')
        scaler_path = os.path.join(model_dir, f'lstm_scaler_{timestamp}.pkl')
        metadata_path = os.path.join(model_dir, f'lstm_metadata_{timestamp}.json')

        # Save model
        self.model.save(model_path)

        # Save scaler
        joblib.dump(self.scaler, scaler_path)

        # Save metadata
        metadata = {
            'model_type': 'LSTM',
            'training_date': timestamp,
            'sequence_length': self.sequence_length,
            'feature_names': self.feature_names,
            'metrics': self.metrics
        }

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Also save as latest model
        latest_model_path = os.path.join(model_dir, 'lstm_model_latest.h5')
        latest_scaler_path = os.path.join(model_dir, 'lstm_scaler_latest.pkl')
        latest_metadata_path = os.path.join(model_dir, 'lstm_metadata_latest.json')

        self.model.save(latest_model_path)
        joblib.dump(self.scaler, latest_scaler_path)
        with open(latest_metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"\nModel saved to: {model_path}")
        print(f"Scaler saved to: {scaler_path}")
        print(f"Metadata saved to: {metadata_path}")


def main():
    """Main training pipeline"""
    print("=" * 70)
    print("Grid Guardian - LSTM Model Training")
    print("=" * 70)

    # Initialize trainer
    trainer = LSTMTrainer(
        data_path='data/processed/features.csv',
        sequence_length=24
    )

    # Load and prepare sequences
    X_train, X_test, y_train, y_test = trainer.load_and_prepare_sequences()
    print(f"\nTraining samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    print(f"Failure rate (train): {y_train.mean():.2%}")

    # Train model
    history = trainer.train_model(X_train, y_train, X_test, y_test, epochs=50)

    # Evaluate
    metrics = trainer.evaluate_model(X_test, y_test)

    # Save model
    trainer.save_model()

    print("\n" + "=" * 70)
    print("Training pipeline completed successfully!")
    print("=" * 70)


if __name__ == '__main__':
    main()
