import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import pickle
import warnings
warnings.filterwarnings('ignore')

# Generate synthetic data
np.random.seed(42)
n_samples = 1000

data = {
    'claim_amount': np.random.normal(5000, 2000, n_samples),
    'policy_age': np.random.uniform(1, 10, n_samples),
    'customer_history': np.random.randint(0, 5, n_samples)
}

df = pd.DataFrame(data)
# Create fraud labels (imbalanced - 10% fraud cases)
df['fraud'] = np.random.choice([0, 1], size=n_samples, p=[0.9, 0.1])

# Prepare features and target
X = df[['claim_amount', 'policy_age', 'customer_history']]
y = df['fraud']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Handle imbalanced data using SMOTE
smote = SMOTE(random_state=42)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train_scaled, y_train)

# Train model
model = RandomForestClassifier(random_state=42)
model.fit(X_train_balanced, y_train_balanced)

# Evaluate model
cv_scores = cross_val_score(model, X_train_balanced, y_train_balanced, cv=5)
test_score = model.score(X_test_scaled, y_test)

# Feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print(f"Cross-validation scores: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
print(f"Test accuracy: {test_score:.3f}")
print("\nFeature Importance:")
print(feature_importance)

# Save the model and scaler
with open('fraud_model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)