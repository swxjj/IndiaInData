from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import pandas as pd

class BaseDataConnector(ABC):
    """Clase base abstracta para conectores de datos macroeconómicos oficiales."""

    @abstractmethod
    def fetch_series(
        self,
        indicators: List[Dict[str, str]],
        countries: List[str],
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Descarga y armoniza series temporales para indicadores y países especificados.

        Args:
            indicators: Lista de diccionarios con 'code' (código oficial) y 'name' (nombre en español).
            countries: Lista de códigos de país (ISO-3 o ISO-2).
            start_year: Año inicial opcional.
            end_year: Año final opcional.

        Returns:
            pd.DataFrame en formato Panel Ancho (Wide) ordenado por país y año.
        """
        pass

    @abstractmethod
    def search_indicator(self, query: str) -> List[Dict[str, str]]:
        """Busca indicadores disponibles según una consulta en lenguaje natural."""
        pass
