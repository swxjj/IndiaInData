import os
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from adjustText import adjust_text

# -----------------------------------------------------------------------------
# 1. DATOS
# -----------------------------------------------------------------------------
data = [
    ("India", "Asia", 3.330379, 4.001694),
    ("Bangladesh", "Asia", 3.315925, 3.938357),
    ("Pakistán", "Asia", 3.505113, 3.749524),
    ("Filipinas", "Asia", 3.653643, 4.031309),
    ("Vietnam", "Asia", 3.392339, 4.189135),
    ("Argentina", "Latam", 4.230635, 4.444772),
    ("Brasil", "Latam", 4.101516, 4.301566),
    ("México", "Latam", 4.234760, 4.340681),
    ("Chile", "Latam", 4.039622, 4.489444),
    ("Colombia", "Latam", 3.999948, 4.273664),
    ("Kenia", "África", 3.620915, 3.777818),
    ("Marruecos", "África", 3.645291, 3.977514),
    ("Camerún", "África", 3.654910, 3.694250),
    ("Etiopía", "África", 2.941684, 3.490642),
    ("Sudáfrica", "África", 4.033872, 4.133285),
    ("EE.UU.", "Primer Mundo", 4.647228, 4.886103),
    ("Japón", "Primer Mundo", 4.557962, 4.683798),
    ("Unión Europea", "Primer Mundo", 4.524040, 4.741049),
    ("Canadá", "Primer Mundo", 4.607188, 4.763350),
    ("Noruega", "Primer Mundo", 4.752880, 4.978516)
]

df = pd.DataFrame(data, columns=["country", "region", "pib90", "pib25"])

# Tasa como resta directa de los logs sobre 35 años
df["tasa"] = (df["pib25"] - df["pib90"]) / 35

# -----------------------------------------------------------------------------
# 2. DIRECTORIOS
# -----------------------------------------------------------------------------
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fig_dir = os.path.join(base_dir, "output", "figures")
os.makedirs(fig_dir, exist_ok=True)

# -----------------------------------------------------------------------------
# 3. REGRESIONES
# -----------------------------------------------------------------------------
reg1 = stats.linregress(df["pib90"], df["pib25"])
reg2 = stats.linregress(df["pib90"], df["tasa"])

# -----------------------------------------------------------------------------
# 4. COLORES POR GRUPO
# -----------------------------------------------------------------------------
color_map = {
    "Primer Mundo": "#2563eb",  # Azul
    "Latam": "#7c3aed",         # Violeta
    "África": "#b45309",        # Marrón / Ocre
    "Asia": "#16a34a"           # Verde
}
india_color = "#ea580c"         # Naranja (único destacado)

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 10.5

x_line = np.linspace(2.8, 4.9, 100)

# =============================================================================
# GRÁFICO 1: DISPERSIÓN logpib1990 vs logpbi2025
# =============================================================================
fig1, ax1 = plt.subplots(figsize=(9.5, 7), dpi=300)

# Puntos por grupo
for group, color in color_map.items():
    sub = df[(df["region"] == group) & (df["country"] != "India")]
    ax1.scatter(sub["pib90"], sub["pib25"], c=color, s=75, alpha=0.85, edgecolors="white", linewidths=1.2, zorder=3)

# India destacada
india_row = df[df["country"] == "India"].iloc[0]
ax1.scatter(india_row["pib90"], india_row["pib25"], c=india_color, s=150, edgecolors="#7c2d12", linewidths=2.2, zorder=5)

# Recta de tendencia
y_trend1 = reg1.intercept + reg1.slope * x_line
ax1.plot(x_line, y_trend1, color="#dc2626", linewidth=2.0, zorder=4)

# Ecuación simple sin box
eq_text1 = f"y = {reg1.slope:.4f}x + {reg1.intercept:.4f}"
ax1.text(0.68, 0.12, eq_text1, transform=ax1.transAxes, fontsize=13, fontweight="bold", color="#dc2626")

# Nombres de países
texts1 = []
for _, row in df.iterrows():
    is_india = row["country"] == "India"
    txt = ax1.text(row["pib90"], row["pib25"], f" {row['country']}",
                   fontsize=9.5 if not is_india else 10.5,
                   fontweight="bold" if is_india else "normal",
                   color=india_color if is_india else "#1f2937")
    texts1.append(txt)

adjust_text(texts1, x=df["pib90"].values, y=df["pib25"].values, ax=ax1,
            arrowprops=dict(arrowstyle="-", color="#9ca3af", lw=0.6),
            expand=(1.15, 1.25))

ax1.set_title("PIB per cápita 1990 vs. PIB per cápita 2025", fontsize=13, fontweight="bold", pad=12)
ax1.set_xlabel("Log PIB per cápita (1990)", fontsize=11, fontweight="bold")
ax1.set_ylabel("Log PIB per cápita (2025)", fontsize=11, fontweight="bold")
ax1.set_xlim(2.8, 4.9)
ax1.set_ylim(3.35, 5.15)
fig1.tight_layout()

fig1_path = os.path.join(fig_dir, "grafico1_dispersion_logpib90_logpbi25.png")
fig1.savefig(fig1_path, dpi=300, bbox_inches="tight")
fig1.savefig(os.path.join(fig_dir, "grafico1_dispersion_logpib90_logpbi25.pdf"), bbox_inches="tight")
plt.close(fig1)

# =============================================================================
# GRÁFICO 2: DISPERSIÓN logpib1990 vs TASA PROMEDIO
# =============================================================================
fig2, ax2 = plt.subplots(figsize=(9.5, 7), dpi=300)

# Puntos por grupo
for group, color in color_map.items():
    sub = df[(df["region"] == group) & (df["country"] != "India")]
    ax2.scatter(sub["pib90"], sub["tasa"], c=color, s=75, alpha=0.85, edgecolors="white", linewidths=1.2, zorder=3)

# India destacada
ax2.scatter(india_row["pib90"], india_row["tasa"], c=india_color, s=150, edgecolors="#7c2d12", linewidths=2.2, zorder=5)

# Recta de tendencia
y_trend2 = reg2.intercept + reg2.slope * x_line
ax2.plot(x_line, y_trend2, color="#dc2626", linewidth=2.0, zorder=4)

# Ecuación simple sin box
eq_text2 = f"y = {reg2.slope:.4f}x + {reg2.intercept:.4f}"
ax2.text(0.68, 0.88, eq_text2, transform=ax2.transAxes, fontsize=13, fontweight="bold", color="#dc2626")

# Nombres de países
texts2 = []
for _, row in df.iterrows():
    is_india = row["country"] == "India"
    txt = ax2.text(row["pib90"], row["tasa"], f" {row['country']}",
                   fontsize=9.5 if not is_india else 10.5,
                   fontweight="bold" if is_india else "normal",
                   color=india_color if is_india else "#1f2937")
    texts2.append(txt)

adjust_text(texts2, x=df["pib90"].values, y=df["tasa"].values, ax=ax2,
            arrowprops=dict(arrowstyle="-", color="#9ca3af", lw=0.6),
            expand=(1.15, 1.25))

ax2.set_title("PIB per cápita 1990 vs. Tasa de crecimiento promedio", fontsize=13, fontweight="bold", pad=12)
ax2.set_xlabel("Log PIB per cápita (1990)", fontsize=11, fontweight="bold")
ax2.set_ylabel("Tasa de crecimiento promedio anual", fontsize=11, fontweight="bold")
ax2.set_xlim(2.8, 4.9)
ax2.set_ylim(-0.002, 0.026)
fig2.tight_layout()

fig2_path = os.path.join(fig_dir, "grafico2_dispersion_logpib90_tasa_promedio.png")
fig2.savefig(fig2_path, dpi=300, bbox_inches="tight")
fig2.savefig(os.path.join(fig_dir, "grafico2_dispersion_logpib90_tasa_promedio.pdf"), bbox_inches="tight")
plt.close(fig2)

# =============================================================================
# COPIAR A ARTIFACTS
# =============================================================================
artifact_dir = r"C:\Users\USER\.gemini\antigravity-ide\brain\fce23e34-19b1-4072-b485-54c2d0172897"
if os.path.isdir(artifact_dir):
    for f in ["grafico1_dispersion_logpib90_logpbi25.png", "grafico2_dispersion_logpib90_tasa_promedio.png"]:
        shutil.copy2(os.path.join(fig_dir, f), os.path.join(artifact_dir, f))

print("Archivos generados exitosamente sin box de leyenda y con ecuaciones directas.")
