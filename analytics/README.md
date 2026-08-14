# Analytics Pipeline

This module uses the Titanic dataset loaded once through Seaborn.

## Dataset

The dataset was loaded using:

sns.load_dataset('titanic')

An offline fallback was saved as titanic.csv.

## Missing Values

Missing values were handled according to the required percentage thresholds:
- Under 5%: affected rows dropped.
- 5%–30%: median/mode imputation.
- High-missing categorical data: encoded as a Missing category.

## Modeling

Three classifiers were trained:
- Logistic Regression
- Decision Tree
- Random Forest

Preprocessing was performed using a ColumnTransformer and Pipeline, with preprocessing fitted only on training data.

## Imbalance

Baseline and class-weight-balanced approaches were compared. SMOTE was considered/applied only to the training data to avoid leakage.

## Hyperparameter Tuning

Random Forest was tuned using GridSearchCV for:
- n_estimators
- max_depth
- max_features

OOB score was reported.

## Regression

Linear regression was used to predict fare. MAE, RMSE, R² and Adjusted R² were calculated.

## Saved Model

The complete preprocessing and Random Forest pipeline was saved as:

model_pipeline.joblib

It can be reloaded with joblib.load() and used directly on raw input data.
