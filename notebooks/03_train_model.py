# Databricks Notebook - Python

# Command 1
# Train
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
rf.fit(X_train, y_train)


# Command 2
import pandas as pd
df = spark.table("gold.ml_features").toPandas()


# Command 3
# Save model locally first
import joblib

joblib.dump(rf, '/Volumes/workspace/gold/ml-model/rf_model.pkl')
joblib.dump(df["programa_elegido"].unique().tolist(), '/Volumes/workspace/gold/ml-model/programas.pkl')

print("Model saved")

# Command 4
# Features
feature_cols = [
    "nota_normalizada", "edad", "creditos_ratio",
    "rama_ciencias", "rama_sociales", "rama_ingenieria",
    "es_murcia", "es_extranjero", "es_online"
]

# Command 5
# Evaluate
from sklearn.metrics import roc_auc_score, classification_report

y_pred_proba = rf.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, y_pred_proba)

print(f"AUC: {auc:.3f}")

fi = pd.DataFrame({
    'feature': feature_cols,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)

display(fi)



# Command 6
X = df[feature_cols]
y = df['exito_academico']

# Command 7
# Split
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


