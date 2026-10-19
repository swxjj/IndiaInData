import io
import base64
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Backend no interactivo para entornos de servidor
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from typing import List, Dict, Any, Optional, Tuple

# Paleta académica sobria (Journal of Economic Perspectives / NBER)
ACADEMIC_COLORS = [
    "#1B365D",  # Navy Blue
    "#8B263E",  # Crimson / Dark Red
    "#2E6F40",  # Forest Green
    "#4A5568",  # Slate Gray
    "#D97706",  # Amber / Dark Gold
    "#6B21A8",  # Deep Purple
    "#0E7490",  # Deep Cyan
    "#9A3412",  # Rust / Orange-Red
]

class AcademicChartRenderer:
    """Motor de renderizado determinista con estética académica estandarizada."""

    @staticmethod
    def setup_style():
        """Aplica estilos globales sobrios de matplotlib."""
        plt.rcParams.update({
            "font.family": "sans-serif",
            "font.sans-serif": ["Inter", "Helvetica", "Arial", "DejaVu Sans"],
            "font.size": 11,
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
            "axes.labelsize": 11,
            "axes.labelweight": "normal",
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 10.5,
            "figure.titlesize": 15,
            "figure.dpi": 300,
            "axes.edgecolor": "#718096",
            "axes.linewidth": 0.8,
            "grid.color": "#E2E8F0",
            "grid.linestyle": "--",
            "grid.linewidth": 0.6,
            "grid.alpha": 0.7,
        })

    @classmethod
    def render_chart(
        cls,
        df_wide: pd.DataFrame,
        indicator_cols: List[str],
        indicator_names: List[str],
        title: str,
        subtitle: Optional[str] = None,
        source_note: str = "Fuente: Banco Mundial (WDI). Elaboración propia para Desarrollo Económico (UNS).",
        units: Optional[str] = None,
        chart_type: str = "line",
        output_dir: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Genera un gráfico académico de alta calidad y lo exporta en PNG y SVG.
        """
        cls.setup_style()

        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
        countries = df_wide["pais"].unique()

        color_idx = 0

        # Filtrar solo columnas que existan en el DataFrame
        valid_cols = [c for c in indicator_cols if c in df_wide.columns]
        valid_names = [indicator_names[i] for i, c in enumerate(indicator_cols) if c in df_wide.columns]

        if not valid_cols:
            raise ValueError("Ninguna de las columnas solicitadas existe en el DataFrame descargado.")

        # Modo 1: Dispersión con línea de tendencia (Scatter Plot)
        if chart_type == "scatter" and len(valid_cols) >= 2:
            import numpy as np
            x_col = valid_cols[0]
            y_col = valid_cols[1]
            x_label = valid_names[0]
            y_label = valid_names[1]

            valid_df = df_wide.dropna(subset=[x_col, y_col])

            for country in countries:
                df_c = valid_df[valid_df["pais"] == country]
                if df_c.empty:
                    continue

                color = ACADEMIC_COLORS[color_idx % len(ACADEMIC_COLORS)]
                color_idx += 1

                ax.scatter(
                    df_c[x_col],
                    df_c[y_col],
                    label=country,
                    color=color,
                    s=55,
                    alpha=0.85,
                    edgecolors="white",
                    linewidth=0.8
                )

                # Anotar el punto más reciente de cada país
                last_row = df_c.sort_values("anio").iloc[-1]
                ax.annotate(
                    f"{country} ('{str(int(last_row['anio']))[-2:]})",
                    (last_row[x_col], last_row[y_col]),
                    xytext=(6, 4),
                    textcoords="offset points",
                    fontsize=8.5,
                    fontweight="500",
                    color="#2D3748"
                )

            # Calcular regresión lineal y R² si hay datos suficientes
            x_all = valid_df[x_col].values
            y_all = valid_df[y_col].values
            if len(x_all) >= 3:
                try:
                    slope, intercept = np.polyfit(x_all, y_all, 1)
                    r_mat = np.corrcoef(x_all, y_all)
                    r_sq = (r_mat[0, 1] ** 2) if r_mat.shape == (2, 2) else 0.0
                    x_seq = np.linspace(x_all.min(), x_all.max(), 100)
                    ax.plot(
                        x_seq,
                        slope * x_seq + intercept,
                        color="#8B263E",
                        linestyle="--",
                        linewidth=1.8,
                        label=f"Tendencia (R² = {r_sq:.2f})"
                    )
                except Exception as e:
                    print(f"No se pudo calcular la regresión: {e}")

            ax.set_xlabel(x_label, labelpad=8, color="#2D3748")
            ax.set_ylabel(y_label, labelpad=8, color="#2D3748")

        # Modo 2: Gráfico de barras comparativo (Bar Chart)
        elif chart_type == "bar":
            import numpy as np
            col = valid_cols[0]
            ind_name = valid_names[0]

            data_points = []
            for country in countries:
                df_c = df_wide[df_wide["pais"] == country].dropna(subset=[col])
                if not df_c.empty:
                    latest = df_c.sort_values("anio").iloc[-1]
                    data_points.append({
                        "pais": country,
                        "valor": latest[col],
                        "anio": int(latest["anio"])
                    })

            if data_points:
                df_bar = pd.DataFrame(data_points).sort_values(by="valor", ascending=True)
                y_pos = np.arange(len(df_bar))
                colors = [ACADEMIC_COLORS[i % len(ACADEMIC_COLORS)] for i in range(len(df_bar))]
                bars = ax.barh(y_pos, df_bar["valor"], color=colors, alpha=0.88, height=0.6)
                ax.set_yticks(y_pos)
                ax.set_yticklabels([f"{r['pais']} ({r['anio']})" for _, r in df_bar.iterrows()])
                ax.bar_label(bars, fmt="%.1f", padding=5, fontsize=9, color="#2D3748")
                ax.set_xlabel(units or ind_name, labelpad=8, color="#2D3748")

        # Modo 3: Áreas apiladas continuas (ej: sectores productivos para 1 país)
        elif chart_type == "stacked_area" and len(countries) == 1 and len(valid_cols) > 1:
            country = countries[0]
            df_c = df_wide[df_wide["pais"] == country].dropna(subset=valid_cols).sort_values("anio")
            if not df_c.empty:
                years = df_c["anio"].values
                y_series = [df_c[col].values for col in valid_cols]
                colors = [ACADEMIC_COLORS[i % len(ACADEMIC_COLORS)] for i in range(len(valid_cols))]
                ax.stackplot(years, *y_series, labels=valid_names, colors=colors, alpha=0.85)

        # Modo 4: Líneas con sombreado de área (Area / Line Fill)
        elif chart_type == "area":
            for country in countries:
                for idx, col in enumerate(valid_cols):
                    df_c = df_wide[df_wide["pais"] == country].dropna(subset=[col])
                    if df_c.empty:
                        continue

                    color = ACADEMIC_COLORS[color_idx % len(ACADEMIC_COLORS)]
                    color_idx += 1

                    name = valid_names[idx] if idx < len(valid_names) else col
                    label = f"{country} - {name}" if len(countries) > 1 else name

                    ax.plot(
                        df_c["anio"],
                        df_c[col],
                        label=label,
                        color=color,
                        linewidth=2.2
                    )
                    ax.fill_between(
                        df_c["anio"],
                        0,
                        df_c[col],
                        color=color,
                        alpha=0.22
                    )

        # Modo 5: Líneas estándar (Default Line Chart)
        else:
            if len(valid_cols) == 1:
                col = valid_cols[0]
                ind_name = valid_names[0] if valid_names else col

                for country in countries:
                    df_c = df_wide[df_wide["pais"] == country].dropna(subset=[col])
                    if df_c.empty:
                        continue

                    color = ACADEMIC_COLORS[color_idx % len(ACADEMIC_COLORS)]
                    color_idx += 1

                    ax.plot(
                        df_c["anio"],
                        df_c[col],
                        label=country,
                        color=color,
                        linewidth=2.2,
                        marker="o",
                        markersize=4,
                        markevery=max(1, len(df_c) // 12)
                    )
            else:
                for country in countries:
                    for idx, col in enumerate(valid_cols):
                        df_c = df_wide[df_wide["pais"] == country].dropna(subset=[col])
                        if df_c.empty:
                            continue

                        color = ACADEMIC_COLORS[color_idx % len(ACADEMIC_COLORS)]
                        color_idx += 1

                        name = valid_names[idx] if idx < len(valid_names) else col
                        label = f"{country} - {name}" if len(countries) > 1 else name

                        ax.plot(
                            df_c["anio"],
                            df_c[col],
                            label=label,
                            color=color,
                            linewidth=2.0,
                            linestyle="-" if idx % 2 == 0 else "--"
                        )

        # Despine (eliminar bordes superior y derecho)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#4A5568")
        ax.spines["bottom"].set_color("#4A5568")

        # Grilla horizontal sutil
        ax.grid(True, axis="y", linestyle="--", alpha=0.5, color="#CBD5E1")
        ax.grid(False, axis="x")

        # Formato de ejes para series de tiempo (solo años enteros)
        if chart_type not in ("scatter", "bar"):
            ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
            ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%d"))

        # Formato eje Y (comas/puntos de miles o porcentajes)
        if chart_type != "bar":
            ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.1f}" if units and "%" not in units else "{x:,.0f}"))
            if units:
                ax.set_ylabel(units, labelpad=8, color="#2D3748")

        # Título y Subtítulo en español
        fig.text(0.125, 0.96, title, fontsize=14, fontweight="bold", color="#1A202C")
        if subtitle:
            fig.text(0.125, 0.92, subtitle, fontsize=10.5, color="#4A5568")

        # Nota de fuente al pie
        fig.text(0.125, 0.02, source_note, fontsize=8.5, color="#718096", style="italic")

        # Leyenda sobria y limpia (solo si hay etiquetas para mostrar)
        handles, leg_labels = ax.get_legend_handles_labels()
        if leg_labels:
            ax.legend(
                frameon=True,
                facecolor="white",
                edgecolor="#E2E8F0",
                framealpha=0.9,
                loc="best"
            )

        plt.subplots_adjust(top=0.88, bottom=0.12, left=0.12, right=0.95)

        # Buffer para base64
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        buf.seek(0)
        png_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        buf.close()

        # Guardar archivos descargables si se especificó directorio
        png_path = None
        svg_path = None
        csv_path = None

        if output_dir and session_id:
            os.makedirs(output_dir, exist_ok=True)
            png_path = os.path.join(output_dir, f"chart_{session_id}.png")
            svg_path = os.path.join(output_dir, f"chart_{session_id}.svg")
            csv_path = os.path.join(output_dir, f"data_{session_id}.csv")

            plt.savefig(png_path, format="png", dpi=300, bbox_inches="tight")
            plt.savefig(svg_path, format="svg", bbox_inches="tight")

            # Guardar CSV en formato Panel Ancho
            df_wide.to_csv(csv_path, index=False, sep=",", decimal=".")

        plt.close(fig)

        return {
            "png_base64": png_base64,
            "png_path": png_path,
            "svg_path": svg_path,
            "csv_path": csv_path
        }
