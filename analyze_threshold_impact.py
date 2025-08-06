import pandas as pd
import numpy as np
import os

def analyze_impact(results_file='audit_results-53755.csv', performance_file='53755.csv'):
    """
    Analizuje wpływ filtrowania aplikacji na podstawie różnych progów
    prawdopodobieństwa bycia 'suspicious', włączając w to analizę CTR.
    """
    try:
        results_df = pd.read_csv(results_file)
        performance_df = pd.read_csv(performance_file)
    except FileNotFoundError as e:
        print(f"BŁĄD: Nie znaleziono pliku: {e.filename}")
        print("Upewnij się, że oba pliki ('audit_results-53755' i 'audit_input.csv') znajdują się w folderze.")
        return

    # Upewnij się, że kluczowe kolumny istnieją
    required_cols_perf = ['app_id', 'bid_responses', 'imps', 'spend_usd', 'clicks', 'conversions', 'conversions_orderpurchase']
    if not all(col in performance_df.columns for col in required_cols_perf):
        print(f"BŁĄD: Plik '{performance_file}' musi zawierać kolumny: {required_cols_perf}")
        return
        
    required_cols_results = ['app_id', 'final_suspicion_probability']
    if not all(col in results_df.columns for col in required_cols_results):
        print(f"BŁĄD: Plik '{results_file}' musi zawierać kolumny: {required_cols_results}")
        return

    # Połącz dane
    merged_df = pd.merge(performance_df, results_df[['app_id', 'final_suspicion_probability']], on='app_id', how='left')
    merged_df['final_suspicion_probability'].fillna(0, inplace=True)

    metric_columns = ['bid_responses', 'imps', 'spend_usd', 'clicks', 'conversions', 'conversions_orderpurchase']
    
    # --- Analiza PRZED filtrowaniem ---
    totals_before = merged_df[metric_columns].sum()
    
    # Oblicz wyjściowy CTR
    ctr_before = (totals_before['clicks'] / totals_before['imps'] * 100) if totals_before['imps'] > 0 else 0
    
    print("="*60)
    print("  SUMARYCZNE METRYKI PRZED FILTROWANIEM")
    print("="*60)
    print(totals_before.to_string())
    print(f"\nWyjściowy CTR: {ctr_before:.4f}%")
    print("\n")

    # --- Analiza PO filtrowaniu dla różnych progów ---
    thresholds = [0.25, 0.5, 0.6, 0.7, 0.75, 0.8, 0.9]
    analysis_results = []

    for threshold in thresholds:
        df_after = merged_df[merged_df['final_suspicion_probability'] < threshold]
        
        totals_after = df_after[metric_columns].sum()
        
        retained_percentage = (totals_after / totals_before * 100).fillna(100)
        
        apps_before_count = len(merged_df['app_id'].unique())
        apps_after_count = len(df_after['app_id'].unique())
        apps_filtered_count = apps_before_count - apps_after_count
        apps_filtered_percentage = (apps_filtered_count / apps_before_count) * 100
        
        # Oblicz CTR po filtracji i zmianę
        ctr_after = (totals_after['clicks'] / totals_after['imps'] * 100) if totals_after['imps'] > 0 else 0
        ctr_change = ctr_after - ctr_before

        result_row = {
            'Próg (Threshold)': f"< {threshold}",
            'Liczba odfiltrowanych appek': f"{apps_filtered_count} ({apps_filtered_percentage:.1f}%)",
            'Zachowany Spend (%)': f"{retained_percentage['spend_usd']:.2f}%",
            'Zachowane Konwersje (%)': f"{retained_percentage['conversions']:.2f}%",
            'CTR po filtracji (%)': f"{ctr_after:.4f}",
            'Zmiana CTR (p.p.)': f"{ctr_change:+.4f}",
        }
        analysis_results.append(result_row)

    summary_df = pd.DataFrame(analysis_results)
    print("="*80)
    print("         WPŁYW FILTROWANIA NA METRYKI DLA RÓŻNYCH PROGÓW (Z UWZGLĘDNIENIEM CTR)")
    print("="*80)
    print(summary_df.to_string(index=False))

if __name__ == "__main__":
    PERFORMANCE_FILE = '27136.csv'
    if os.path.exists(PERFORMANCE_FILE) and not os.path.exists('audit_input.csv'):
        try:
            os.rename(PERFORMANCE_FILE, 'audit_input.csv')
            print(f"Zmieniono nazwę pliku '{PERFORMANCE_FILE}' na 'audit_input.csv' dla spójności.")
        except Exception as e:
            print(f"Nie udało się zmienić nazwy pliku: {e}")
            print("Upewnij się, że plik z danymi biznesowymi nazywa się 'audit_input.csv'.")
    
    analyze_impact()