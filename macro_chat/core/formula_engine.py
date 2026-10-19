"""
Motor de Evaluación Segura de Fórmulas Econométricas
Permite a los estudiantes generar variables derivadas (ej: salario real, tasas de crecimiento, índices)
utilizando validación estricta por AST (Abstract Syntax Tree).
"""
import ast
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Set

# Nodos AST estrictamente permitidos
ALLOWED_AST_NODES = {
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Call,
    ast.Name,
    ast.Constant,
    ast.Num,  # Compatibilidad versiones previas
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.USub,
    ast.UAdd,
    ast.Load,
}

# Funciones matemáticas y econométricas permitidas
ALLOWED_FUNCTIONS = {
    "log": "ln",
    "ln": "ln",
    "log10": "log10",
    "sqrt": "sqrt",
    "abs": "abs",
    "exp": "exp",
    "lag": "lag",
    "diff": "diff",
    "pct_change": "pct_change",
    "ma": "ma",
    "cagr": "cagr",
}

class FormulaSecurityError(Exception):
    """Excepción lanzada cuando una fórmula contiene operaciones o llamadas no permitidas."""
    pass

class FormulaEvaluationError(Exception):
    """Excepción lanzada durante el cómputo de la fórmula sobre los datos."""
    pass

class SafeFormulaValidator(ast.NodeVisitor):
    """Validador AST que garantiza que una expresión sea puramente matemática."""

    def __init__(self, allowed_variables: Set[str]):
        self.allowed_variables = allowed_variables
        self.used_variables: Set[str] = set()

    def generic_visit(self, node):
        if type(node) not in ALLOWED_AST_NODES:
            raise FormulaSecurityError(
                f"Operación no permitida en la fórmula: {type(node).__name__}"
            )
        super().generic_visit(node)

    def visit_Name(self, node):
        var_name = node.id
        if var_name.startswith("__"):
            raise FormulaSecurityError(f"Identificador reservado no permitido: {var_name}")
        if var_name not in ALLOWED_FUNCTIONS and var_name not in self.allowed_variables:
            # Puede ser una variable o una función no reconocida
            self.used_variables.add(var_name)
        elif var_name in self.allowed_variables:
            self.used_variables.add(var_name)
        self.generic_visit(node)

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            raise FormulaSecurityError("Solo se permiten llamadas directas a funciones matemáticas.")
        func_name = node.func.id
        if func_name not in ALLOWED_FUNCTIONS:
            raise FormulaSecurityError(
                f"Función no permitida: '{func_name}'. Funciones válidas: {', '.join(sorted(ALLOWED_FUNCTIONS.keys()))}"
            )
        self.generic_visit(node)


class FormulaEngine:
    """Motor de cálculo econométrico con soporte de series de tiempo panel por país."""

    @classmethod
    def validate_formula(cls, expression: str, available_columns: List[str]) -> Dict[str, Any]:
        """
        Valida sintaxis y seguridad de una fórmula sin evaluarla.
        Retorna un diccionario con estado y variables requeridas.
        """
        clean_expr = expression.strip()
        if not clean_expr:
            return {"valid": False, "error": "La expresión no puede estar vacía.", "variables": []}

        try:
            tree = ast.parse(clean_expr, mode="eval")
        except SyntaxError as e:
            return {"valid": False, "error": f"Error de sintaxis: {e.msg}", "variables": []}

        validator = SafeFormulaValidator(allowed_variables=set(available_columns))
        try:
            validator.visit(tree)
        except FormulaSecurityError as e:
            return {"valid": False, "error": str(e), "variables": []}

        missing = [v for v in validator.used_variables if v not in available_columns]
        if missing:
            return {
                "valid": False,
                "error": f"Variables no disponibles en el conjunto de datos: {', '.join(missing)}",
                "variables": list(validator.used_variables)
            }

        return {
            "valid": True,
            "error": None,
            "variables": list(validator.used_variables)
        }

    @classmethod
    def apply_formulas(cls, df: pd.DataFrame, formulas: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Aplica una lista de fórmulas secuencialmente sobre el DataFrame.
        Cada fórmula es un dict con:
          - 'name' / 'column': Identificador de la nueva columna (ej: 'salario_real')
          - 'expression': Expresión matemática (ej: 'salario_nominal / inflacion_ipc * 100')
          - 'label': Nombre legible opcional
        """
        if df.empty or not formulas:
            return df

        df_result = df.copy()

        # Asegurar ordenamiento temporal por país
        if "pais" in df_result.columns and "anio" in df_result.columns:
            df_result = df_result.sort_values(by=["pais", "anio"]).reset_index(drop=True)

        for f_spec in formulas:
            target_col = f_spec.get("column") or f_spec.get("name")
            expression = f_spec.get("expression", "").strip()

            if not target_col or not expression:
                continue

            # Sanitizar nombre de columna
            clean_target_col = target_col.strip().lower().replace(" ", "_")

            # Validar
            available_cols = list(df_result.columns)
            validation = cls.validate_formula(expression, available_cols)
            if not validation["valid"]:
                raise FormulaEvaluationError(
                    f"Fórmula '{clean_target_col}' inválida: {validation['error']}"
                )

            # Evaluar de forma segura
            try:
                computed_series = cls._evaluate_expression(df_result, expression)
                df_result[clean_target_col] = computed_series
            except Exception as e:
                raise FormulaEvaluationError(
                    f"Error al calcular '{clean_target_col}' ({expression}): {str(e)}"
                )

        return df_result

    @classmethod
    def _evaluate_expression(cls, df: pd.DataFrame, expression: str) -> pd.Series:
        """
        Evalúa la expresión sobre el DataFrame utilizando funciones vectorizadas
        y agrupadas por país para operaciones de panel.
        """
        has_panel = "pais" in df.columns

        # Construir entorno de ejecución seguro
        env: Dict[str, Any] = {
            "np": np,
            "ln": lambda s: np.log(s.replace(0, np.nan)),
            "log": lambda s: np.log(s.replace(0, np.nan)),
            "log10": lambda s: np.log10(s.replace(0, np.nan)),
            "sqrt": lambda s: np.sqrt(s.clip(lower=0)),
            "abs": lambda s: np.abs(s),
            "exp": lambda s: np.exp(s),
        }

        # Funciones que dependen de panel / series de tiempo
        if has_panel:
            env["lag"] = lambda s, n=1: df.groupby("pais")[s.name].shift(int(n))
            env["diff"] = lambda s, n=1: df.groupby("pais")[s.name].diff(int(n))
            env["pct_change"] = lambda s, n=1: df.groupby("pais")[s.name].pct_change(int(n)) * 100
            env["ma"] = lambda s, n=3: df.groupby("pais")[s.name].transform(
                lambda x: x.rolling(int(n), min_periods=1).mean()
            )
            env["cagr"] = lambda s, n=5: (
                (s / df.groupby("pais")[s.name].shift(int(n))) ** (1.0 / int(n)) - 1.0
            ) * 100
        else:
            env["lag"] = lambda s, n=1: s.shift(int(n))
            env["diff"] = lambda s, n=1: s.diff(int(n))
            env["pct_change"] = lambda s, n=1: s.pct_change(int(n)) * 100
            env["ma"] = lambda s, n=3: s.rolling(int(n), min_periods=1).mean()
            env["cagr"] = lambda s, n=5: ((s / s.shift(int(n))) ** (1.0 / int(n)) - 1.0) * 100

        # Cargar columnas del DataFrame en el entorno
        for col in df.columns:
            if col not in env:
                env[col] = df[col]

        # Evaluación con eval seguro (sin builtins)
        tree = ast.parse(expression, mode="eval")
        compiled = compile(tree, filename="<formula>", mode="eval")
        result = eval(compiled, {"__builtins__": {}}, env)

        if isinstance(result, (int, float)):
            return pd.Series([result] * len(df), index=df.index)
        elif isinstance(result, pd.Series):
            return result
        elif isinstance(result, np.ndarray):
            return pd.Series(result, index=df.index)
        else:
            return pd.Series(result, index=df.index)
