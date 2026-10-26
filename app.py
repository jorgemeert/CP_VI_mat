import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import chisquare

rng = np.random.default_rng(42)
D = np.arange(1, 10)
BENF = np.log10(1 + 1/D)

def first_digit(x):
    x = np.abs(np.asarray(x, dtype=float)); x = x[x > 0]
    return (x / 10**np.floor(np.log10(x))).astype(int)

def analyse(name, x):
    fd = first_digit(x); n = len(fd)
    obs = np.array([(fd == d).sum() for d in D]); freq = obs/n
    chi = chisquare(obs, BENF*n)
    mad = np.mean(np.abs(freq-BENF))
    verdict = ("conformidade proxima" if mad < .006 else "conformidade aceitavel" if mad < .012
               else "conformidade marginal" if mad < .015 else "nao conforme")
    return dict(nome=name, n=n, qui2=chi.statistic, p=chi.pvalue, MAD=mad, veredito=verdict), freq

n = 10000
random_sets = {
 "Aleatorio: uniforme (1 a 9999)": rng.integers(1, 10000, n),
 "Aleatorio: normal (media 1000, dp 200)": rng.normal(1000, 200, n),
 "Aleatorio: log-uniforme (1 a 1.000.000)": 10**rng.uniform(0, 6, n),
}
cities = pd.read_csv("cities_us.csv")["number"]
elec = pd.read_csv("election.csv"); elec = elec[elec.country == "US"]["number"]
wait = pd.read_csv("waitlist.csv")["number"]
real_sets = {
 "Real: populacao de cidades dos EUA": cities,
 "Real: votos por estado/candidato (EUA 2008)": elec,
 "Real: listas de espera de saude (Finlandia e Espanha)": wait,
}

rows = []
def plot(sets, fname, title):
    fig, axs = plt.subplots(1, len(sets), figsize=(5.2*len(sets), 4.2), sharey=True)
    for ax, (k, v) in zip(axs, sets.items()):
        r, f = analyse(k, v); rows.append(r)
        ax.bar(D, f, color="#4C78A8", label="Observado")
        ax.plot(D, BENF, "o-", color="#E45756", label="Benford")
        ax.set_xticks(D); ax.set_xlabel("Primeiro digito")
        ax.set_title(k.split(": ")[1] + f"\n(n={r['n']}, MAD={r['MAD']:.4f})", fontsize=9)
    axs[0].set_ylabel("Frequencia"); axs[0].legend()
    fig.suptitle(title); fig.tight_layout(); fig.savefig(fname, dpi=150); plt.close(fig)

plot(random_sets, "grafico_aleatorios.png", "Dados aleatorios gerados pelo computador")
plot(real_sets, "grafico_reais.png", "Dados reais")
df = pd.DataFrame(rows); pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
print(df.to_string(index=False, float_format=lambda v: f"{v:.4g}"))
df.to_csv("resultados.csv", index=False)
