"""
Feature Engineering Module
Creates advanced features from sensor data for improved predictions
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import os
import warnings

warnings.filterwarnings('ignore')


class FeatureEngineer:
    """Engineer features from preprocessed sensor data"""

    def __init__(self, data_path='data/processed/cleaned_data.csv'):
        self.data_path = data_path
        self.df = None

    def load_data(self):
        """Load preprocessed data"""
        print("Loading preprocessed data...")
        self.df = pd.read_csv(self.data_path)
        if 'timestamp' in self.df.columns:
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        print(f"Loaded {len(self.df)} records")

        # Create failure target variable if not present
        if 'failure' not in self.df.columns:
            print("Creating failure target variable from sensor data...")
            self.df = self.create_failure_labels()

        return self.df

    def create_failure_labels(self):
        """
        Create failure labels and risk levels based on critical sensor thresholds
        Uses DGA (Dissolved Gas Analysis) and other key indicators

        Risk levels:
        - 0: Low risk (normal operation)
        - 1: Medium risk (warning conditions)
        - 2: High risk (critical conditions, likely failure)
        """
        # Initialize columns
        self.df['failure'] = 0
        self.df['risk_level'] = 0  # 0=low, 1=medium, 2=high
        self.df['failure_probability'] = 0.0

        # Helper to safely get column
        def safe_get(col_name):
            return self.df[col_name] if col_name in self.df.columns else 0

        print(f"  Columns present: {list(self.df.columns[:15])}")

        # Calculate composite risk score (0-1 scale)
        risk_score = (
            (safe_get('gas_c2h2') / 200).clip(0, 1) * 0.25 +
            (safe_get('gas_h2') / 500).clip(0, 1) * 0.20 +
            (safe_get('gas_ch4') / 300).clip(0, 1) * 0.15 +
            (safe_get('temperature_top') / 150).clip(0, 1) * 0.20 +
            (safe_get('vibration_x') / 10).clip(0, 1) * 0.20
        )

        self.df['failure_probability'] = risk_score

        # HIGH RISK (top 5%) - Critical failures
        high_risk_conditions = (
            # Critical DGA values
            (safe_get('gas_c2h2') > 100) |
            (safe_get('gas_h2') > 300) |
            (safe_get('gas_ch4') > 200) |
            # Critical temperature
            (safe_get('temperature_top') > 100) |
            (safe_get('temperature_oil') > 90) |
            # Critical vibration
            (safe_get('vibration_x') > 8) |
            (safe_get('vibration_y') > 8) |
            # Combined critical conditions
            ((safe_get('gas_c2h2') > 50) & (safe_get('temperature_top') > 85)) |
            ((safe_get('gas_h2') > 150) & (safe_get('vibration_x') > 5))
        )

        # MEDIUM RISK (next 20%) - Warning conditions
        medium_risk_conditions = (
            # Elevated DGA values
            (safe_get('gas_c2h2') > 50) |
            (safe_get('gas_h2') > 150) |
            (safe_get('gas_ch4') > 100) |
            # Elevated temperature
            (safe_get('temperature_top') > 85) |
            (safe_get('temperature_oil') > 75) |
            # Elevated vibration
            (safe_get('vibration_x') > 5) |
            (safe_get('vibration_y') > 5) |
            # Combined warning conditions
            ((safe_get('gas_c2h2') > 25) & (safe_get('temperature_top') > 75))
        )

        # Apply risk levels
        self.df.loc[high_risk_conditions, 'risk_level'] = 2  # High risk
        self.df.loc[high_risk_conditions, 'failure'] = 1     # Mark as failure

        self.df.loc[medium_risk_conditions & (self.df['risk_level'] == 0), 'risk_level'] = 1  # Medium risk

        # If not enough variety, use quantiles
        high_count = (self.df['risk_level'] == 2).sum()
        medium_count = (self.df['risk_level'] == 1).sum()

        if high_count == 0:
            print("[INFO] Using risk score quantiles for classification...")
            high_threshold = risk_score.quantile(0.95)
            medium_threshold = risk_score.quantile(0.75)

            self.df.loc[risk_score >= high_threshold, 'risk_level'] = 2
            self.df.loc[risk_score >= high_threshold, 'failure'] = 1
            self.df.loc[(risk_score >= medium_threshold) & (risk_score < high_threshold), 'risk_level'] = 1

            high_count = (self.df['risk_level'] == 2).sum()
            medium_count = (self.df['risk_level'] == 1).sum()

        low_count = (self.df['risk_level'] == 0).sum()

        print(f"[OK] Risk distribution:")
        print(f"  Low risk (0): {low_count:,} ({low_count/len(self.df)*100:.1f}%)")
        print(f"  Medium risk (1): {medium_count:,} ({medium_count/len(self.df)*100:.1f}%)")
        print(f"  High risk (2): {high_count:,} ({high_count/len(self.df)*100:.1f}%)")
        print(f"  Failures marked: {self.df['failure'].sum():,} ({self.df['failure'].mean():.2%})")

        return self.df

    def create_temporal_features(self):
        """Create time-based features"""
        print("\nCreating temporal features...")

        if 'timestamp' not in self.df.columns:
            print("No timestamp column, skipping temporal features")
            return

        self.df['hour'] = self.df['timestamp'].dt.hour
        self.df['day_of_week'] = self.df['timestamp'].dt.dayofweek
        self.df['month'] = self.df['timestamp'].dt.month
        self.df['is_weekend'] = (self.df['day_of_week'] >= 5).astype(int)

        # Cyclical encoding for hour (24-hour cycle)
        self.df['hour_sin'] = np.sin(2 * np.pi * self.df['hour'] / 24)
        self.df['hour_cos'] = np.cos(2 * np.pi * self.df['hour'] / 24)

        # Cyclical encoding for day of week (7-day cycle)
        self.df['day_sin'] = np.sin(2 * np.pi * self.df['day_of_week'] / 7)
        self.df['day_cos'] = np.cos(2 * np.pi * self.df['day_of_week'] / 7)

        print("Temporal features created")

    def create_rolling_features(self, windows=[3, 6, 12, 24]):
        """Create rolling window statistics"""
        print(f"\nCreating rolling features with windows: {windows}...")

        sensor_cols = ['temperature', 'vibration', 'current', 'voltage',
                      'power_factor', 'oil_level', 'humidity']

        # Sort by equipment and timestamp
        if 'equipment_id' in self.df.columns and 'timestamp' in self.df.columns:
            self.df = self.df.sort_values(['equipment_id', 'timestamp'])

            for col in sensor_cols:
                if col not in self.df.columns:
                    continue

                for window in windows:
                    # Rolling mean
                    self.df[f'{col}_rolling_mean_{window}h'] = (
                        self.df.groupby('equipment_id')[col]
                        .transform(lambda x: x.rolling(window, min_periods=1).mean())
                    )

                    # Rolling std
                    self.df[f'{col}_rolling_std_{window}h'] = (
                        self.df.groupby('equipment_id')[col]
                        .transform(lambda x: x.rolling(window, min_periods=1).std())
                    )

                    # Rolling min/max
                    self.df[f'{col}_rolling_min_{window}h'] = (
                        self.df.groupby('equipment_id')[col]
                        .transform(lambda x: x.rolling(window, min_periods=1).min())
                    )

                    self.df[f'{col}_rolling_max_{window}h'] = (
                        self.df.groupby('equipment_id')[col]
                        .transform(lambda x: x.rolling(window, min_periods=1).max())
                    )

        print("Rolling features created")

    def create_lag_features(self, lags=[1, 3, 6, 12]):
        """Create lagged features"""
        print(f"\nCreating lag features: {lags}...")

        sensor_cols = ['temperature', 'vibration', 'current', 'voltage']

        if 'equipment_id' in self.df.columns:
            for col in sensor_cols:
                if col not in self.df.columns:
                    continue

                for lag in lags:
                    self.df[f'{col}_lag_{lag}'] = (
                        self.df.groupby('equipment_id')[col]
                        .shift(lag)
                    )

        # Fill NaN from lags with 0
        lag_cols = [col for col in self.df.columns if 'lag_' in col]
        self.df[lag_cols] = self.df[lag_cols].fillna(0)

        print("Lag features created")

    def create_rate_of_change(self):
        """Create rate of change features"""
        print("\nCreating rate of change features...")

        sensor_cols = ['temperature', 'vibration', 'current', 'voltage']

        if 'equipment_id' in self.df.columns:
            for col in sensor_cols:
                if col not in self.df.columns:
                    continue

                # Rate of change (difference from previous reading)
                self.df[f'{col}_roc'] = (
                    self.df.groupby('equipment_id')[col]
                    .diff()
                )

                # Acceleration (second derivative)
                self.df[f'{col}_acceleration'] = (
                    self.df.groupby('equipment_id')[f'{col}_roc']
                    .diff()
                )

        # Fill NaN with 0
        roc_cols = [col for col in self.df.columns if '_roc' in col or '_acceleration' in col]
        self.df[roc_cols] = self.df[roc_cols].fillna(0)

        print("Rate of change features created")

    def create_interaction_features(self):
        """Create interaction features between sensors"""
        print("\nCreating interaction features...")

        # Temperature-vibration interaction (often correlate in failures)
        if 'temperature' in self.df.columns and 'vibration' in self.df.columns:
            self.df['temp_vibration_interaction'] = (
                self.df['temperature'] * self.df['vibration']
            )

        # Current-voltage interaction (power-related)
        if 'current' in self.df.columns and 'voltage' in self.df.columns:
            self.df['current_voltage_interaction'] = (
                self.df['current'] * self.df['voltage']
            )

        # Temperature deviation from normal
        if 'temperature' in self.df.columns:
            self.df['temp_deviation'] = abs(self.df['temperature'] - 65)

        # Vibration severity score
        if 'vibration' in self.df.columns and 'age_years' in self.df.columns:
            self.df['vibration_age_risk'] = (
                self.df['vibration'] * (self.df['age_years'] / 10)
            )

        print("Interaction features created")

    def create_domain_features(self):
        """Create domain-specific features based on power grid knowledge"""
        print("\nCreating domain-specific features...")

        # Equipment health score (inverse of age and maintenance)
        if 'age_years' in self.df.columns and 'maintenance_days_ago' in self.df.columns:
            self.df['health_score'] = 100 - (
                (self.df['age_years'] / 30 * 50) +
                (self.df['maintenance_days_ago'] / 365 * 50)
            )

        # Temperature risk (above 85°C is concerning)
        if 'temperature' in self.df.columns:
            self.df['temp_risk'] = (self.df['temperature'] > 85).astype(int)
            self.df['temp_critical'] = (self.df['temperature'] > 100).astype(int)

        # Vibration risk (above 5 mm/s is concerning)
        if 'vibration' in self.df.columns:
            self.df['vibration_risk'] = (self.df['vibration'] > 5).astype(int)
            self.df['vibration_critical'] = (self.df['vibration'] > 8).astype(int)

        # Oil level risk (below 60% is concerning)
        if 'oil_level' in self.df.columns:
            self.df['oil_risk'] = (self.df['oil_level'] < 60).astype(int)

        # Power factor risk (below 0.85 is poor)
        if 'power_factor' in self.df.columns:
            self.df['power_factor_risk'] = (self.df['power_factor'] < 0.85).astype(int)

        # Combined risk score
        risk_cols = [col for col in self.df.columns if '_risk' in col or '_critical' in col]
        if risk_cols:
            self.df['total_risk_score'] = self.df[risk_cols].sum(axis=1)

        print("Domain features created")

    def create_statistical_features(self):
        """Create statistical aggregation features"""
        print("\nCreating statistical features...")

        sensor_cols = ['temperature', 'vibration', 'current', 'voltage']

        if 'equipment_id' in self.df.columns:
            for col in sensor_cols:
                if col not in self.df.columns:
                    continue

                # Equipment-level statistics
                self.df[f'{col}_equipment_mean'] = (
                    self.df.groupby('equipment_id')[col]
                    .transform('mean')
                )

                self.df[f'{col}_equipment_std'] = (
                    self.df.groupby('equipment_id')[col]
                    .transform('std')
                )

                # Deviation from equipment average
                self.df[f'{col}_deviation_from_mean'] = (
                    self.df[col] - self.df[f'{col}_equipment_mean']
                )

        print("Statistical features created")

    def encode_categorical_features(self):
        """Encode categorical variables"""
        print("\nEncoding categorical features...")

        if 'equipment_id' in self.df.columns:
            # One-hot encode equipment_id
            equipment_dummies = pd.get_dummies(self.df['equipment_id'], prefix='equipment')
            self.df = pd.concat([self.df, equipment_dummies], axis=1)
            print(f"Created {len(equipment_dummies.columns)} equipment dummy variables")

    def save_features(self, output_path='data/processed/features.csv'):
        """Save engineered features"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.df.to_csv(output_path, index=False)
        print(f"\nFeatures saved to: {output_path}")
        print(f"Total features: {len(self.df.columns)}")
        return output_path

    def get_feature_summary(self):
        """Print feature summary"""
        print("\n" + "=" * 70)
        print("Feature Engineering Summary")
        print("=" * 70)
        print(f"Total records: {len(self.df)}")
        print(f"Total features: {len(self.df.columns)}")
        print(f"\nFeature categories:")

        feature_types = {
            'Temporal': [col for col in self.df.columns if any(x in col for x in ['hour', 'day', 'month', 'weekend'])],
            'Rolling': [col for col in self.df.columns if 'rolling' in col],
            'Lag': [col for col in self.df.columns if 'lag' in col],
            'Rate of Change': [col for col in self.df.columns if 'roc' in col or 'acceleration' in col],
            'Interaction': [col for col in self.df.columns if 'interaction' in col or 'deviation' in col],
            'Domain': [col for col in self.df.columns if 'risk' in col or 'health' in col],
            'Statistical': [col for col in self.df.columns if 'equipment_mean' in col or 'equipment_std' in col]
        }

        for category, features in feature_types.items():
            print(f"  {category}: {len(features)} features")


def feature_engineering_pipeline(input_path='data/processed/cleaned_data.csv',
                                output_path='data/processed/features.csv'):
    """Complete feature engineering pipeline"""
    print("=" * 70)
    print("Grid Guardian - Feature Engineering Pipeline")
    print("=" * 70)

    # Initialize feature engineer
    engineer = FeatureEngineer(input_path)

    # Load data
    engineer.load_data()

    # Create features
    engineer.create_temporal_features()
    engineer.create_rolling_features(windows=[3, 6, 12, 24])
    engineer.create_lag_features(lags=[1, 3, 6, 12])
    engineer.create_rate_of_change()
    engineer.create_interaction_features()
    engineer.create_domain_features()
    engineer.create_statistical_features()
    engineer.encode_categorical_features()

    # Summary
    engineer.get_feature_summary()

    # Save
    engineer.save_features(output_path)

    print("\n" + "=" * 70)
    print("Feature engineering completed successfully!")
    print("=" * 70)

    return engineer.df


if __name__ == '__main__':
    # Run feature engineering pipeline
    df = feature_engineering_pipeline(
        input_path='data/processed/cleaned_data.csv',
        output_path='data/processed/features.csv'
    )
