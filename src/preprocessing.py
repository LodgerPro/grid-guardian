"""
Data Preprocessing Module
Handles cleaning, normalization, and preparation of grid sensor data
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler
import os
import warnings

warnings.filterwarnings('ignore')


class DataPreprocessor:
    """Preprocess raw sensor data for model training"""

    def __init__(self, raw_data_path='data/raw/grid_sensor_data.csv'):
        self.raw_data_path = raw_data_path
        self.scaler = None
        self.df = None

    def load_data(self):
        """Load raw sensor data"""
        print("Loading raw data...")
        if self.raw_data_path.endswith('.parquet'):
            self.df = pd.read_parquet(self.raw_data_path)
        else:
            self.df = pd.read_csv(self.raw_data_path)
        print(f"Loaded {len(self.df)} records")
        print(f"Columns: {list(self.df.columns)}")
        return self.df

    def handle_missing_values(self):
        """Handle missing values in dataset"""
        print("\nHandling missing values...")

        # Check for missing values
        missing = self.df.isnull().sum()
        if missing.sum() > 0:
            print("Missing values detected:")
            print(missing[missing > 0])

            # Forward fill for time-series continuity
            self.df = self.df.fillna(method='ffill')

            # Backward fill for any remaining
            self.df = self.df.fillna(method='bfill')

            # Fill any remaining with median
            for col in self.df.select_dtypes(include=[np.number]).columns:
                if self.df[col].isnull().any():
                    self.df[col].fillna(self.df[col].median(), inplace=True)
        else:
            print("No missing values found")

    def remove_outliers(self, method='iqr', threshold=3):
        """Remove or cap outliers"""
        print(f"\nHandling outliers using {method} method...")

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col != 'failure']

        initial_len = len(self.df)

        if method == 'iqr':
            # IQR method - cap rather than remove
            for col in numeric_cols:
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                # Cap values
                self.df[col] = self.df[col].clip(lower_bound, upper_bound)

        elif method == 'zscore':
            # Z-score method - cap at threshold standard deviations
            for col in numeric_cols:
                mean = self.df[col].mean()
                std = self.df[col].std()
                lower_bound = mean - threshold * std
                upper_bound = mean + threshold * std

                self.df[col] = self.df[col].clip(lower_bound, upper_bound)

        print(f"Outliers handled (records unchanged: {initial_len})")

    def parse_timestamps(self):
        """Parse and extract time features from timestamps"""
        print("\nParsing timestamps...")

        if 'timestamp' in self.df.columns:
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            print("Timestamps parsed successfully")
        else:
            print("No timestamp column found")

    def validate_data(self):
        """Validate data quality"""
        print("\nValidating data...")

        issues = []

        # Check for duplicates
        duplicates = self.df.duplicated().sum()
        if duplicates > 0:
            print(f"Warning: {duplicates} duplicate rows found")
            issues.append(f"Duplicates: {duplicates}")
            self.df = self.df.drop_duplicates()

        # Check for negative values where they shouldn't exist
        positive_cols = ['temperature', 'vibration', 'current', 'voltage',
                        'power_factor', 'oil_level', 'humidity', 'age_years']

        for col in positive_cols:
            if col in self.df.columns:
                negative_count = (self.df[col] < 0).sum()
                if negative_count > 0:
                    print(f"Warning: {negative_count} negative values in {col}")
                    self.df.loc[self.df[col] < 0, col] = 0

        # Check target variable distribution
        if 'failure' in self.df.columns:
            failure_rate = self.df['failure'].mean()
            print(f"Failure rate: {failure_rate:.2%}")
            if failure_rate < 0.01:
                print("Warning: Very low failure rate may cause training issues")
                issues.append(f"Low failure rate: {failure_rate:.2%}")

        if not issues:
            print("Data validation passed!")

        return issues

    def balance_dataset(self, method='none', ratio=0.3):
        """Balance dataset if needed"""
        print(f"\nBalancing dataset using method: {method}")

        if 'failure' not in self.df.columns:
            print("No failure column found, skipping balancing")
            return

        failure_count = self.df['failure'].sum()
        non_failure_count = len(self.df) - failure_count

        print(f"Before balancing - Failures: {failure_count}, Non-failures: {non_failure_count}")

        if method == 'undersample':
            # Undersample majority class
            df_failure = self.df[self.df['failure'] == 1]
            df_non_failure = self.df[self.df['failure'] == 0]

            target_non_failure = int(len(df_failure) / ratio)
            df_non_failure_sampled = df_non_failure.sample(n=min(target_non_failure, len(df_non_failure)),
                                                           random_state=42)

            self.df = pd.concat([df_failure, df_non_failure_sampled])
            self.df = self.df.sample(frac=1, random_state=42).reset_index(drop=True)

        elif method == 'oversample':
            # Simple oversampling of minority class
            df_failure = self.df[self.df['failure'] == 1]
            df_non_failure = self.df[self.df['failure'] == 0]

            target_failure = int(len(df_non_failure) * ratio)
            oversample_factor = target_failure // len(df_failure)

            df_failure_oversampled = pd.concat([df_failure] * oversample_factor, ignore_index=True)
            self.df = pd.concat([df_non_failure, df_failure_oversampled])
            self.df = self.df.sample(frac=1, random_state=42).reset_index(drop=True)

        print(f"After balancing: {len(self.df)} records, failure rate: {self.df['failure'].mean():.2%}")

    def save_processed_data(self, output_path='data/processed/cleaned_data.csv'):
        """Save preprocessed data"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.df.to_csv(output_path, index=False)
        print(f"\nProcessed data saved to: {output_path}")
        return output_path

    def get_data_summary(self):
        """Get summary statistics"""
        print("\n" + "=" * 70)
        print("Data Summary")
        print("=" * 70)
        print(self.df.describe())
        print("\nData types:")
        print(self.df.dtypes)
        print(f"\nTotal records: {len(self.df)}")
        print(f"Total features: {len(self.df.columns)}")


def preprocess_pipeline(input_path='data/raw/grid_sensor_data.csv',
                       output_path='data/processed/cleaned_data.csv',
                       balance_method='none'):
    """Complete preprocessing pipeline"""
    print("=" * 70)
    print("Grid Guardian - Data Preprocessing Pipeline")
    print("=" * 70)

    # Initialize preprocessor
    preprocessor = DataPreprocessor(input_path)

    # Load data
    preprocessor.load_data()

    # Preprocessing steps
    preprocessor.handle_missing_values()
    preprocessor.parse_timestamps()
    preprocessor.remove_outliers(method='iqr')
    preprocessor.validate_data()
    preprocessor.balance_dataset(method=balance_method)

    # Summary
    preprocessor.get_data_summary()

    # Save
    preprocessor.save_processed_data(output_path)

    print("\n" + "=" * 70)
    print("Preprocessing completed successfully!")
    print("=" * 70)

    return preprocessor.df


if __name__ == '__main__':
    # Run preprocessing pipeline
    df = preprocess_pipeline(
        input_path='data/raw/grid_telemetry_data.parquet',
        output_path='data/processed/cleaned_data.csv',
        balance_method='none'
    )
