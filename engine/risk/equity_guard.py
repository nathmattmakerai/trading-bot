"""
Equity Guard: Protection adaptative du capital.

Ce module surveille la performance récente de la stratégie.
Si la stratégie entre dans une phase perdante (Drawdown ou série de pertes),
l'Equity Guard conseille de passer en mode "Virtuel" (taille de position 0).

Le trading réel ne reprend que lorsque la stratégie montre des signes de reprise
(trades virtuels gagnants).
"""

import pandas as pd
from typing import List, Dict, Optional
from collections import deque


class EquityGuard:
    """
    Garde-fou basé sur la performance récente (Equity Curve Trading).
    """
    
    def __init__(
        self,
        window_size: int = 10,
        loss_threshold_pct: float = -2.0,  # Arrêter si perte > 2% sur la fenêtre
        consecutive_losses_threshold: int = 3,  # Arrêter après 3 pertes consécutives
        recovery_trades_required: int = 2,  # Reprendre après 2 trades gagnants (virtuels)
    ):
        """
        Args:
            window_size: Nombre de trades récents à analyser
            loss_threshold_pct: Seuil de perte cumulée sur la fenêtre pour désactiver
            consecutive_losses_threshold: Nombre de pertes consécutives pour désactiver
            recovery_trades_required: Nombre de trades gagnants (virtuels) pour réactiver
        """
        self.window_size = window_size
        self.loss_threshold_pct = loss_threshold_pct
        self.consecutive_losses_threshold = consecutive_losses_threshold
        self.recovery_trades_required = recovery_trades_required
        
        # État interne
        self.is_active = True  # True = Trading Réel, False = Trading Virtuel (Pause)
        self.consecutive_losses = 0
        self.virtual_consecutive_wins = 0
        self.recent_pnl_pct = deque(maxlen=window_size)
    
    def update_after_trade(self, pnl_pct: float) -> str:
        """
        Met à jour l'état après un trade (réel ou virtuel).
        
        Args:
            pnl_pct: Résultat du trade en % (ex: -1.5 pour -1.5%)
            
        Returns:
            Message décrivant le changement d'état (si applicable)
        """
        # Mettre à jour l'historique glissant
        self.recent_pnl_pct.append(pnl_pct)
        
        message = ""
        
        if pnl_pct < 0:
            self.consecutive_losses += 1
            self.virtual_consecutive_wins = 0
        elif pnl_pct > 0:
            self.consecutive_losses = 0
            if not self.is_active:
                self.virtual_consecutive_wins += 1
        
        # Logique de DÉSACTIVATION (Passage en Virtuel)
        if self.is_active:
            # 1. Vérifier pertes consécutives
            if self.consecutive_losses >= self.consecutive_losses_threshold:
                self.is_active = False
                message = f"🛑 PAUSE TRADING: {self.consecutive_losses} pertes consécutives. Passage en mode Virtuel."
            
            # 2. Vérifier drawdown sur la fenêtre glissante
            elif sum(self.recent_pnl_pct) <= self.loss_threshold_pct:
                current_dd = sum(self.recent_pnl_pct)
                self.is_active = False
                message = f"🛑 PAUSE TRADING: Drawdown récent ({current_dd:.2f}%) dépasse seuil ({self.loss_threshold_pct}%). Passage en mode Virtuel."
                
        # Logique de RÉACTIVATION (Retour au Réel)
        else:
            # Si on est en pause, on attend des signes de reprise (trades virtuels gagnants)
            if self.virtual_consecutive_wins >= self.recovery_trades_required:
                self.is_active = True
                self.consecutive_losses = 0  # Reset
                self.virtual_consecutive_wins = 0
                # On vide l'historique récent pour éviter de re-déclencher immédiatement
                self.recent_pnl_pct.clear()
                message = f"✅ REPRISE TRADING: {self.recovery_trades_required} trades virtuels gagnants. La stratégie semble synchronisée."
                
        return message
    
    def can_trade(self) -> bool:
        """Est-ce qu'on peut trader en réel ?"""
        return self.is_active
    
    def get_status(self) -> dict:
        """Retourne l'état actuel pour le dashboard."""
        return {
            "is_active": self.is_active,
            "consecutive_losses": self.consecutive_losses,
            "virtual_recovery_wins": self.virtual_consecutive_wins,
            "recent_performance_pct": sum(self.recent_pnl_pct)
        }
