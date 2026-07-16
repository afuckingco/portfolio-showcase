import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import os

def load_hr_data():
    base = os.path.dirname(__file__)
    path = os.path.join(base, '..', 'data', 'hr_sample.csv')
    df = pd.read_csv(path)
    X = df[['absensi_pct', 'produktivitas_pct']]
    y = df['performance_label'].map({'Cukup':0, 'Baik':1, 'Sangat Baik':2})
    return X, y

def train_and_evaluate():
    X, y = load_hr_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    dt = DecisionTreeClassifier(max_depth=3, random_state=42)
    dt.fit(X_train, y_train)
    y_pred = dt.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f'HR Decision Tree Accuracy: {acc:.2f}')
    print(classification_report(y_test, y_pred, target_names=['Cukup','Baik','Sangat Baik']))
    return dt

if __name__ == '__main__':
    train_and_evaluate()