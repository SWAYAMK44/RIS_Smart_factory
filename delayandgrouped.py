import numpy as np
import matplotlib.pyplot as plt
from scipy.special import j0

# ==============================
# GLOBAL PARAMETERS
# ==============================
fc = 3e9
c = 3e8
Ts = 1e-3

N = 64
G = 8
Pt = 1
sigma2 = 1
K = 5

T = 200
MC = 150

Delta_list = [0, 1, 2, 5, 10]
v_list = [1, 3, 5]

# ==============================
# FUNCTIONS
# ==============================

def ar1(prev, rho):
    noise = (np.random.randn(len(prev)) + 1j*np.random.randn(len(prev))) / np.sqrt(2)
    return rho * prev + np.sqrt(1 - rho**2) * noise

def snr(H):
    return 10*np.log10(Pt * np.abs(H)**2 / sigma2)

# ==============================
# 1) SNR vs DELAY (MULTI VELOCITY)
# ==============================

results = {v: [] for v in v_list}

for v in v_list:

    fd = v * fc / c
    rho = j0(2*np.pi*fd*Ts)

    h_br = (np.random.randn(N) + 1j*np.random.randn(N)) / np.sqrt(2)

    for Delta in Delta_list:

        snr_runs = []

        for mc in range(MC):

            h_ru = (np.random.randn(N) + 1j*np.random.randn(N)) / np.sqrt(2)
            h_d = (np.random.randn() + 1j*np.random.randn()) / np.sqrt(2)

            h_hist = [h_ru]
            snr_t = []

            for t in range(T):

                h_ru = ar1(h_ru, rho)
                h_d = rho*h_d + np.sqrt(1-rho**2)*(np.random.randn()+1j*np.random.randn())/np.sqrt(2)

                h_hist.append(h_ru)

                if t >= Delta:
                    h_old = h_hist[t-Delta]
                else:
                    h_old = h_hist[0]

                theta = -np.angle(h_br * h_old)

                H = h_d + np.sum(h_br * h_ru * np.exp(1j*theta))

                snr_t.append(snr(H))

            snr_runs.append(np.mean(snr_t))

        results[v].append(np.mean(snr_runs))

# ==============================
# PLOT 1: SNR vs DELAY
# ==============================

plt.figure()
for v in v_list:
    plt.plot(Delta_list, results[v], marker='o', label=f'v={v} m/s')

plt.xlabel("Delay Δ")
plt.ylabel("Average SNR (dB)")
plt.title("SNR vs Delay")
plt.legend()
plt.grid()
plt.show()

# ==============================
# 2) THEORETICAL CORRELATION
# ==============================

plt.figure()
for v in v_list:
    fd = v * fc / c
    R = [j0(2*np.pi*fd*Ts*d) for d in Delta_list]
    plt.plot(Delta_list, R, marker='x', label=f'v={v}')

plt.xlabel("Delay Δ")
plt.ylabel("Correlation R[Δ]")
plt.title("Theoretical Channel Correlation (Bessel)")
plt.legend()
plt.grid()
plt.show()

# ==============================
# 3) FACTORY SCENARIO
# ==============================

v = 3
fd = v * fc / c
rho = j0(2*np.pi*fd*Ts)

BS_pos = np.array([0, 0])
RIS_pos = np.array([10, 0])

obs_x_min, obs_x_max = 4, 7
obs_y_min, obs_y_max = -2, 2

x_traj = np.linspace(0, 12, T)
y_traj = 2*np.sin(0.5 * x_traj)

def path_loss(d):
    return 10 ** (-(31.84 + 21.5*np.log10(d+1e-3) + 19*np.log10(fc/1e9))/10)

def is_blocked(x, y):
    return (obs_x_min <= x <= obs_x_max) and (obs_y_min <= y <= obs_y_max)

h_br = (np.random.randn(N) + 1j*np.random.randn(N)) / np.sqrt(2)

snr_no, snr_ideal, snr_delay, snr_group = [], [], [], []

h_ru = (np.random.randn(N) + 1j*np.random.randn(N)) / np.sqrt(2)
h_d = (np.random.randn() + 1j*np.random.randn()) / np.sqrt(2)

h_hist = [h_ru]
Delta = 3

for t in range(T):

    x, y = x_traj[t], y_traj[t]
    user_pos = np.array([x, y])

    d_bs = np.linalg.norm(user_pos - BS_pos)
    d_ris = np.linalg.norm(user_pos - RIS_pos)

    beta_bs = path_loss(d_bs)
    beta_ris = path_loss(d_ris)

    if is_blocked(x, y):
        beta_bs *= 0.01

    h_ru = ar1(h_ru, rho)
    h_d = rho*h_d + np.sqrt(1-rho**2)*(np.random.randn()+1j*np.random.randn())/np.sqrt(2)

    h_ru_s = np.sqrt(beta_ris) * h_ru
    h_d_s = np.sqrt(beta_bs) * h_d

    h_hist.append(h_ru_s)

    if t >= Delta:
        h_old = h_hist[t-Delta]
    else:
        h_old = h_hist[0]

    # No RIS
    H_no = h_d_s

    # Ideal RIS
    theta_i = -np.angle(h_br * h_ru_s)
    H_i = h_d_s + np.sum(h_br * h_ru_s * np.exp(1j*theta_i))

    # Delayed RIS
    theta_d = -np.angle(h_br * h_old)
    H_d = h_d_s + np.sum(h_br * h_ru_s * np.exp(1j*theta_d))

    # Grouped RIS
    group_size = N // G
    H_g = h_d_s

    for g in range(G):
        idx = slice(g*group_size, (g+1)*group_size)
        h_c = np.sum(h_br[idx] * h_ru_s[idx])
        h_o = np.sum(h_br[idx] * h_old[idx])
        phi = -np.angle(h_o)
        H_g += h_c * np.exp(1j*phi)

    snr_no.append(snr(H_no))
    snr_ideal.append(snr(H_i))
    snr_delay.append(snr(H_d))
    snr_group.append(snr(H_g))

# ==============================
# PLOT 3: FACTORY
# ==============================

plt.figure()

plt.plot(x_traj, snr_ideal, label='Ideal RIS')
plt.plot(x_traj, snr_delay, label='Delayed RIS')
plt.plot(x_traj, snr_group, label='Grouped RIS')
plt.plot(x_traj, snr_no, label='No RIS')

plt.axvspan(obs_x_min, obs_x_max, color='red', alpha=0.2, label='Blocked Region')

plt.xlabel("Robot X Position")
plt.ylabel("SNR (dB)")
plt.title("SNR vs Robot Position (Factory Scenario)")
plt.legend()
plt.grid()
plt.show()