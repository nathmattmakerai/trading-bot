"""
Error Analyzer: Analyse les erreurs passées pour améliorer les décisions futures.
Implémente le concept de "Learning from backtests".
"""

import pandas as pd
from typing import List, Dict

class ErrorAnalyzer:
    """
    Analyse les trades perdants pour identifier des 'Zones de Danger'
    basées sur le contexte (VIX, ATR Ratio, etc.).
    """
    
    def __init__(self, loss_pct_threshold: float = -1.5):
        self.loss_pct_threshold = loss_pct_threshold
        self.danger_zones = [] # Liste de conditions qui mènent souvent à des pertes
        
    def analyze_backtest_results(self, trades: List[dict]) -> dict:
        """
        Analyse une liste de trades fermés pour trouver des patterns d'échec.
        """
        if not trades:
            return {"status": "no_data"}
            
        df = pd.DataFrame(trades)
        
        # On ne garde que les métadonnées pour l'analyse
        if "metadata" not in df.columns:
            return {"status": "no_metadata"}
            
        # Expansion des métadonnées en colonnes
        meta_df = pd.json_normalize(df["metadata"])
        df = pd.concat([df.drop(columns=["metadata"]), meta_df], axis=1)
        
        # Analyse par VIX
        results = {}
        if "vix" in df.columns:
            vix_bins = [0, 15, 20, 25, 30, 100]
            df['vix_bucket'] = pd.cut(df['vix'], bins=vix_bins)
            vix_stats = df.groupby('vix_bucket')['pnl_pct_account'].agg(['mean', 'count'])
            results["vix_performance"] = vix_stats['mean'].to_dict()
            
            # Identifier les zones de danger (VIX où la moyenne est très négative ET assez de trades)
            for bin, row in vix_stats.iterrows():
                mean_pnl = row['mean']
                count = row['count']
                if count >= 3 and mean_pnl < self.loss_pct_threshold:
                    self.danger_zones.append({
                        "feature": "vix",
                        "min": bin.left,
                        "max": bin.right,
                        "avg_pnl": mean_pnl,
                        "count": int(count)
                    })

        # Analyse par ATR Ratio (Compression)
        if "atr_ratio" in df.columns:
            ratio_bins = [0, 0.5, 0.6, 0.7, 0.8, 1.0]
            df['ratio_bucket'] = pd.cut(df['atr_ratio'], bins=ratio_bins)
            ratio_stats = df.groupby('ratio_bucket')['pnl_pct_account'].agg(['mean', 'count'])
            results["ratio_performance"] = ratio_stats['mean'].to_dict()
            
            for bin, row in ratio_stats.iterrows():
                mean_pnl = row['mean']
                count = row['count']
                if count >= 3 and mean_pnl < self.loss_pct_threshold:
                    self.danger_zones.append({
                        "feature": "atr_ratio",
                        "min": bin.left,
                        "max": bin.right,
                        "avg_pnl": mean_pnl,
                        "count": int(count)
                    })

        return {
            "status": "success",
            "num_trades_analyzed": len(df),
            "danger_zones_identified": len(self.danger_zones),
            "details": results
        }

    def should_avoid_trade(self, current_metadata: dict) -> tuple:
        """
        Vérifie si les conditions actuelles correspondent à une zone de danger apprise.
        """
        for zone in self.danger_zones:
            val = current_metadata.get(zone["feature"])
            if val is not None:
                # Gestion des bins d'intervalles
                if isinstance(zone.get("min"), (int, float)) and isinstance(zone.get("max"), (int, float)):
                    if zone["min"] <= val < zone["max"]:
                        return True, f"Danger Zone: {zone['feature']} in range [{zone['min']}, {zone['max']}] (Avg loss: {zone['avg_pnl']:.2f}%)"
        
        return False, "Conditions appear safe based on past experience"

    def save_memory(self, filepath: str = "config/learning_memory.json"):
        """Sauvegarde les zones de danger apprises."""
        import json
        import os
        import numpy as np
        
        def numpy_encoder(obj):
            if isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
                return int(obj)
            if isinstance(obj, (np.float64, np.float32, np.float16)):
                # Gérer NaN et Infinity qui ne sont pas standard JSON
                if np.isnan(obj) or np.isinf(obj):
                    return None
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return str(obj)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        try:
            with open(filepath, 'w') as f:
                json.dump(self.danger_zones, f, indent=2, default=numpy_encoder)
        except Exception as e:
            print(f"[ErrorAnalyzer] Failed to save memory: {e}")

    def load_memory(self, filepath: str = "config/learning_memory.json"):
        """Charge les zones de danger apprises."""
        import json
        import os
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    if not content.strip():
                        return False
                    self.danger_zones = json.loads(content)
                return True
            except (json.JSONDecodeError, Exception) as e:
                print(f"[ErrorAnalyzer] Memory file corrupted, resetting: {e}")
                self.danger_zones = []
                # On peut optionnellement supprimer le fichier corrompu
                return False
        return False
