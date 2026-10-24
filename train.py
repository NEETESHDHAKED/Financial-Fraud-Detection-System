import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

df = pd.read_csv("creditcard.csv",encoding='ISO-8859-1',engine='python',on_bad_lines='skip')
print(f"Data loaded: {df.shape}, Fraud: {df['Class'].sum()}")

X = df.drop('Class', axis=1)
y = df['Class']

model = RandomForestClassifier(n_estimators=100, class_weight='balanced', n_jobs=-1, random_state=42)
model.fit(X, y)

joblib.dump(model, "fraud_model.pkl")
print("✅ fraud_model.pkl ready!")
