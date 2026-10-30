import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('dark_background')
fig = plt.figure(figsize=(16, 9), dpi=160)
fig.patch.set_facecolor('#0d130e')

# 3 Subplots: 
# Top Left: Model Accuracy & F1-Score
# Top Right: Max Drawdown Protection (Risk)
# Bottom: Confusion Matrix Heatmap
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.2], hspace=0.35, wspace=0.25)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[1, :])

ax1.set_facecolor('#131c14')
ax2.set_facecolor('#131c14')
ax3.set_facecolor('#131c14')

# 1. Bar Chart: Statistical Accuracy & F1-Score
models = ["Supervised ML\n(Random Forest)", "Linear Baseline\n(Logistic Reg)", "Rule-Based\n(Heuristik)", "Unsupervised\n(GMM Cluster)"]
accs = [98.9, 87.6, 58.5, 35.6]
f1s = [98.9, 87.4, 54.4, 21.2]
colors_acc = ["#10b981", "#38bdf8", "#f59e0b", "#94a3b8"]

x = np.arange(len(models))
width = 0.35

b1 = ax1.bar(x - width/2, accs, width, label='OOS Accuracy (%)', color=colors_acc, alpha=0.9, edgecolor='#ffffff', linewidth=0.5)
b2 = ax1.bar(x + width/2, f1s, width, label='Macro F1-Score (%)', color=colors_acc, hatch='//', alpha=0.7, edgecolor='#000000')

ax1.set_ylabel("Persentase (%)", fontsize=10, fontweight='bold', color='#a3b899')
ax1.set_title("Akurasi Prediksi Out-of-Sample (1981 - 2026)\nWalk-Forward Expanding Window", fontsize=11, fontweight='bold', color='#e5ede3')
ax1.set_xticks(x)
ax1.set_xticklabels(models, fontsize=8.5, color='#e5ede3')
ax1.set_ylim(0, 115)
ax1.grid(True, axis='y', color='#263828', linestyle='--', linewidth=0.5)
ax1.legend(loc='upper right', facecolor='#131c14', edgecolor='#344e37', fontsize=8)

for bar in b1:
    h = bar.get_height()
    ax1.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width()/2, h),
                 xytext=(0, 2), textcoords="offset points", ha='center', va='bottom',
                 fontsize=8, fontweight='bold', color='#ffffff')

# 2. Bar Chart: Max Drawdown (Risk Protection)
drawdowns = [-30.7, -30.7, -27.1, -32.2, -52.6]
strat_names = ["Random Forest", "Logistic Reg", "Heuristik", "GMM Cluster", "Benchmark (B&H)"]
dd_colors = ["#10b981", "#38bdf8", "#f59e0b", "#94a3b8", "#ef4444"]

b_dd = ax2.bar(strat_names, drawdowns, color=dd_colors, alpha=0.88, edgecolor='#ffffff', linewidth=0.5)
ax2.set_ylabel("Maximum Drawdown (%)", fontsize=10, fontweight='bold', color='#a3b899')
ax2.set_title("Perlindungan Risiko Modal: Maximum Drawdown (MDD)\nPenurunan Terparah Selama Krisis", fontsize=11, fontweight='bold', color='#e5ede3')
ax2.set_xticklabels(strat_names, fontsize=8.5, color='#e5ede3')
ax2.set_ylim(-60, 0)
ax2.grid(True, axis='y', color='#263828', linestyle='--', linewidth=0.5)

for bar in b_dd:
    h = bar.get_height()
    ax2.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width()/2, h),
                 xytext=(0, -11), textcoords="offset points", ha='center', va='bottom',
                 fontsize=8.5, fontweight='bold', color='#ffffff')

# 3. Heatmap Confusion Matrix: Random Forest
cm = np.array([
    [154,   1,   0,   0],
    [  0, 112,   0,   1],
    [  0,   0, 116,   2],
    [  0,   2,   0, 154]
])
cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

im = ax3.imshow(cm_norm, cmap='YlGn', vmin=0, vmax=1)
labels = ["Kuadran I (Reflasi)", "Kuadran II (Boom)", "Kuadran III (Stagflasi)", "Kuadran IV (Deflasi)"]

ax3.set_xticks(np.arange(len(labels)))
ax3.set_yticks(np.arange(len(labels)))
ax3.set_xticklabels([f"Prediksi:\n{l}" for l in labels], fontsize=9, fontweight='bold', color='#e5ede3')
ax3.set_yticklabels([f"Aktual:\n{l}" for l in labels], fontsize=9, fontweight='bold', color='#e5ede3')
ax3.set_title("Confusion Matrix Random Forest (542 Bulan Out-of-Sample Walk-Forward)\nNilai di dalam kotak: Jumlah Bulan Benar / Salah Klasifikasi", fontsize=11, fontweight='bold', color='#e5ede3', pad=10)

# Text inside cells
for i in range(len(labels)):
    for j in range(len(labels)):
        val = cm[i, j]
        pct = cm_norm[i, j] * 100
        text_color = "black" if cm_norm[i, j] > 0.5 else "white"
        ax3.text(j, i, f"{val} bln\n({pct:.1f}%)", ha="center", va="center",
                 color=text_color, fontsize=10, fontweight='bold')

cbar = fig.colorbar(im, ax=ax3, fraction=0.02, pad=0.03)
cbar.set_label("Rasio Akurasi", color='#a3b899', fontsize=9)

plt.suptitle("AUDIT KUANTITATIF & UJI AKURASI METODE REGIME DETECTION (1981 - 2026)\nPengujian Statistik Klasifikasi vs Kinerja Perlindungan Risiko Portofolio", 
             fontsize=13, fontweight='bold', color='#facc15', y=0.98)

out_png = "d:/SAHAM/chart/regime_accuracy_comparison.png"
plt.savefig(out_png, facecolor=fig.get_facecolor(), edgecolor='none', dpi=180)
print(f"Comparison chart saved: {out_png}")
