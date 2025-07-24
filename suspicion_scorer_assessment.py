# Zawartość pliku sprawdz_metryki.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, roc_auc_score

def evaluate_scorer(file_path='scored_app_dataset.csv', threshold=0.5):
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"BŁĄD: Nie znaleziono pliku '{file_path}'.")
        return

    df_eval = df[df['label'].isin(['suspicious', 'legitimate'])].copy()
    y_true = df_eval['label'].apply(lambda x: 1 if x == 'suspicious' else 0)
    y_prob = df_eval['suspicion_probability']
    y_pred = (y_prob >= threshold).astype(int)

    print("\n--- Raport Klasyfikacji ---\n")
    print(classification_report(y_true, y_pred, target_names=['Legitimate', 'Suspicious']))
    
    auc_score = roc_auc_score(y_true, y_prob)
    print(f"\n--- Wynik AUC: {auc_score:.4f} ---\n")

    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Macierz Pomyłek')
    plt.ylabel('Prawdziwa Etykieta')
    plt.xlabel('Przewidziana Etykieta')
    plt.savefig('confusion_matrix.png')
    plt.show()

    fpr, tpr, _ = roc_curve(y_true, y_prob)
    plt.figure()
    plt.plot(fpr, tpr, label=f'Krzywa ROC (AUC = {auc_score:.2f})')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.title('Krzywa ROC')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend(loc='lower right')
    plt.savefig('roc_curve.png')
    plt.show()

if __name__ == '__main__':
    evaluate_scorer()