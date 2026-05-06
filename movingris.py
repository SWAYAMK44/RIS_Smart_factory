import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# Factory Parameters
# ============================================================

factory_length = 40
factory_width = 20
grid_resolution = 0.5

x = np.arange(0, factory_length, grid_resolution)
y = np.arange(0, factory_width, grid_resolution)
X, Y = np.meshgrid(x, y)

# ============================================================
# AP Parameters
# ============================================================

ap_x, ap_y = 5, 10
Pt_dBm = 20
noise_dBm = -90

Pt = 10 ** ((Pt_dBm - 30) / 10)
noise = 10 ** ((noise_dBm - 30) / 10)

# ============================================================
# RIS Parameters
# ============================================================

N = 64

RIS_positions = [
    (38, 12),   # RIS1
    (30, 3)     # RIS2
]

# ============================================================
# Machines (blockages)
# ============================================================

machines = [
    (15, 25, 6, 14),
    (10, 13, 2, 6),
    (28, 32, 10, 18)
]

# ============================================================
# Channel Model
# ============================================================

alpha = 2
C0 = 1e-3

def shadow_loss(xu, yu):
    loss_dB = 0
    for (xmin, xmax, ymin, ymax) in machines:
        if xu > xmax and ymin <= yu <= ymax:
            depth = xu - xmax
            loss_dB += 12 + 0.8 * depth
    return loss_dB

def compute_direct_power(xu, yu):
    d = np.sqrt((xu - ap_x)**2 + (yu - ap_y)**2) + 1e-3
    path_loss = C0 * (d ** -alpha)
    shadow_dB = shadow_loss(xu, yu)
    shadow_linear = 10 ** (-shadow_dB / 10)
    return Pt * path_loss * shadow_linear

def compute_ris_power(xu, yu, ris_x, ris_y):
    d_AR = np.sqrt((ap_x - ris_x)**2 + (ap_y - ris_y)**2)
    G = C0 * (d_AR ** -alpha)

    d_RU = np.sqrt((xu - ris_x)**2 + (yu - ris_y)**2)
    h_r = C0 * (d_RU ** -alpha)

    return Pt * (N**2) * G * h_r

# ============================================================
# Compute Heatmaps
# ============================================================

SNR_noRIS = np.zeros_like(X)
SNR_1RIS = np.zeros_like(X)
SNR_2RIS = np.zeros_like(X)

ris1_x, ris1_y = RIS_positions[0]
ris2_x, ris2_y = RIS_positions[1]

for i in range(X.shape[0]):
    for j in range(X.shape[1]):

        xu = X[i, j]
        yu = Y[i, j]

        Pr_direct = compute_direct_power(xu, yu)

        Pr_ris1 = compute_ris_power(xu, yu, ris1_x, ris1_y)
        Pr_ris2 = compute_ris_power(xu, yu, ris2_x, ris2_y)

        SNR_noRIS[i, j] = 10 * np.log10(Pr_direct / noise)
        SNR_1RIS[i, j] = 10 * np.log10((Pr_direct + Pr_ris1) / noise)
        SNR_2RIS[i, j] = 10 * np.log10((Pr_direct + Pr_ris1 + Pr_ris2) / noise)

# clip for visualization
SNR_noRIS = np.clip(SNR_noRIS, -10, 80)
SNR_1RIS = np.clip(SNR_1RIS, -10, 80)
SNR_2RIS = np.clip(SNR_2RIS, -10, 80)

# ============================================================
# Plot Heatmaps
# ============================================================

def plot_map(SNR, title):

    plt.figure(figsize=(10,5))

    plt.imshow(
        SNR,
        extent=[0, factory_length, 0, factory_width],
        origin='lower',
        aspect='auto',
        cmap='viridis'
    )

    plt.colorbar(label="SNR (dB)")

    plt.plot(ap_x, ap_y, 'ro', label="AP")

    plt.plot(ris1_x, ris1_y, 'bs', label="RIS1")
    plt.plot(ris2_x, ris2_y, 'cs', label="RIS2")

    for (xmin, xmax, ymin, ymax) in machines:
        plt.gca().add_patch(
            plt.Rectangle(
                (xmin, ymin),
                xmax - xmin,
                ymax - ymin,
                facecolor='gray',
                edgecolor='black',
                alpha=0.7
            )
        )

    plt.xlabel("x (meters)")
    plt.ylabel("y (meters)")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()

plot_map(SNR_noRIS, "SNR Heatmap (No RIS)")
plot_map(SNR_1RIS, "SNR Heatmap (1 RIS)")
plot_map(SNR_2RIS, "SNR Heatmap (2 RIS)")

# ============================================================
# Robot Trajectory Analysis
# ============================================================

path_x = np.linspace(5, 38, 200)
path_y = np.ones_like(path_x) * 5

snr_noRIS = []
snr_1RIS = []
snr_2RIS = []

for xu, yu in zip(path_x, path_y):

    Pr_direct = compute_direct_power(xu, yu)

    Pr_ris1 = compute_ris_power(xu, yu, ris1_x, ris1_y)
    Pr_ris2 = compute_ris_power(xu, yu, ris2_x, ris2_y)

    snr_noRIS.append(10*np.log10(Pr_direct/noise))
    snr_1RIS.append(10*np.log10((Pr_direct+Pr_ris1)/noise))
    snr_2RIS.append(10*np.log10((Pr_direct+Pr_ris1+Pr_ris2)/noise))

# ============================================================
# Plot Robot Path SNR
# ============================================================

plt.figure(figsize=(10,5))

plt.plot(path_x, snr_noRIS, label="No RIS", linewidth=2)
plt.plot(path_x, snr_1RIS, label="1 RIS", linewidth=2)
plt.plot(path_x, snr_2RIS, label="2 RIS", linewidth=2)

plt.axhline(10, color='red', linestyle='--', label="Outage Threshold")

plt.xlabel("Robot Position (meters)")
plt.ylabel("SNR (dB)")
plt.title("Robot Trajectory SNR")
plt.legend()
plt.grid(True)

plt.show()
# ============================================================
# Coverage Probability Calculation
# ============================================================

SNR_threshold = 10

coverage_noRIS = np.mean(SNR_noRIS > SNR_threshold)
coverage_1RIS = np.mean(SNR_1RIS > SNR_threshold)
coverage_2RIS = np.mean(SNR_2RIS > SNR_threshold)

coverage_values = [
    coverage_noRIS,
    coverage_1RIS,
    coverage_2RIS
]

ris_counts = [0, 1, 2]

print("Coverage Results:")
print("No RIS:", coverage_noRIS*100, "%")
print("1 RIS:", coverage_1RIS*100, "%")
print("2 RIS:", coverage_2RIS*100, "%")

# ============================================================
# Plot Coverage vs RIS count
# ============================================================

plt.figure(figsize=(7,5))

plt.plot(
    ris_counts,
    np.array(coverage_values)*100,
    marker='o',
    linewidth=2
)

plt.xlabel("Number of RIS Panels")
plt.ylabel("Coverage Probability (%)")
plt.title("Factory Coverage vs RIS Deployment")
plt.grid(True)

plt.show()