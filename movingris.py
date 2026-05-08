import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# FACTORY PARAMETERS
# ============================================================

factory_length = 40
factory_width = 20
grid_resolution = 0.5

x = np.arange(0, factory_length, grid_resolution)
y = np.arange(0, factory_width, grid_resolution)

X, Y = np.meshgrid(x, y)

# ============================================================
# ACCESS POINT PARAMETERS
# ============================================================

ap_x = 5
ap_y = 10

Pt_dBm = 20
noise_dBm = -90

# Convert dBm to Watts

Pt = 10 ** ((Pt_dBm - 30) / 10)
noise = 10 ** ((noise_dBm - 30) / 10)

# ============================================================
# RIS PARAMETERS
# ============================================================

N = 64

# RIS 1 Position

ris1_x = 38
ris1_y = 12

# RIS 2 Position

ris2_x = 30
ris2_y = 3

# ============================================================
# CHANNEL PARAMETERS
# ============================================================

C0 = 1e-3

# Different path loss exponents

alpha_direct = 2.2
alpha_ris = 1.8

# ============================================================
# FACTORY MACHINES / BLOCKAGES
# ============================================================

machines = [
    (15, 25, 6, 14),
    (10, 13, 2, 6),
    (28, 32, 10, 18)
]

# ============================================================
# SHADOWING MODEL
# ============================================================

def shadow_loss(xu, yu):

    loss_dB = 0

    for (xmin, xmax, ymin, ymax) in machines:

        # user behind obstacle

        if xu > xmax and ymin <= yu <= ymax:

            depth = xu - xmax

            # gradual attenuation

            loss_dB += 6 + 0.3 * depth

    return loss_dB

# ============================================================
# DIRECT CHANNEL GAIN
# ============================================================

def compute_direct_gain(xu, yu):

    d = np.sqrt(
        (xu - ap_x)**2 +
        (yu - ap_y)**2
    ) + 1e-3

    path_loss = C0 * (d ** -alpha_direct)

    shadow_dB = shadow_loss(xu, yu)

    shadow_linear = 10 ** (-shadow_dB / 10)

    return path_loss * shadow_linear

# ============================================================
# RIS CHANNEL GAIN
# ============================================================

def compute_ris_gain(xu, yu, ris_x, ris_y):

    # AP -> RIS

    d_AR = np.sqrt(
        (ap_x - ris_x)**2 +
        (ap_y - ris_y)**2
    ) + 1e-3

    G = C0 * (d_AR ** -alpha_ris)

    # RIS -> USER

    d_RU = np.sqrt(
        (xu - ris_x)**2 +
        (yu - ris_y)**2
    ) + 1e-3

    h_r = C0 * (d_RU ** -alpha_ris)

    # RIS coherent gain

    return (N ** 2) * G * h_r

# ============================================================
# SNR ARRAYS
# ============================================================

SNR_noRIS = np.zeros_like(X)
SNR_1RIS = np.zeros_like(X)
SNR_2RIS = np.zeros_like(X)

# ============================================================
# COMPUTE SNR MAPS
# ============================================================

for i in range(X.shape[0]):

    for j in range(X.shape[1]):

        xu = X[i, j]
        yu = Y[i, j]

        # ----------------------------------------------------
        # Channel gains
        # ----------------------------------------------------

        h_d = compute_direct_gain(xu, yu)

        h_ris1 = compute_ris_gain(
            xu, yu,
            ris1_x, ris1_y
        )

        h_ris2 = compute_ris_gain(
            xu, yu,
            ris2_x, ris2_y
        )

        # ----------------------------------------------------
        # NO RIS
        # ----------------------------------------------------

        Pr_noRIS = Pt * h_d

        # ----------------------------------------------------
        # 1 RIS
        # coherent combining
        # ----------------------------------------------------

        H_1RIS = (
            np.sqrt(h_d) +
            np.sqrt(h_ris1)
        )

        Pr_1RIS = Pt * (H_1RIS ** 2)

        # ----------------------------------------------------
        # 2 RIS
        # ----------------------------------------------------

        H_2RIS = (
            np.sqrt(h_d) +
            np.sqrt(h_ris1) +
            np.sqrt(h_ris2)
        )

        Pr_2RIS = Pt * (H_2RIS ** 2)

        # ----------------------------------------------------
        # SNR
        # ----------------------------------------------------

        SNR_noRIS[i, j] = 10 * np.log10(
            Pr_noRIS / noise
        )

        SNR_1RIS[i, j] = 10 * np.log10(
            Pr_1RIS / noise
        )

        SNR_2RIS[i, j] = 10 * np.log10(
            Pr_2RIS / noise
        )

# ============================================================
# LIMIT VISUALIZATION RANGE
# ============================================================

SNR_noRIS = np.clip(SNR_noRIS, 0, 80)
SNR_1RIS = np.clip(SNR_1RIS, 0, 80)
SNR_2RIS = np.clip(SNR_2RIS, 0, 80)

# ============================================================
# PLOT FUNCTION
# ============================================================

def plot_map(SNR, title, ris_count):

    plt.figure(figsize=(10, 5))

    plt.imshow(
        SNR,
        extent=[0, factory_length, 0, factory_width],
        origin='lower',
        aspect='auto',
        cmap='viridis',
        vmin=0,
        vmax=80
    )

    plt.colorbar(label="SNR (dB)")

    # --------------------------------------------------------
    # AP
    # --------------------------------------------------------

    plt.plot(
        ap_x,
        ap_y,
        'ro',
        markersize=8,
        label='AP'
    )

    # --------------------------------------------------------
    # RIS
    # --------------------------------------------------------

    if ris_count >= 1:

        plt.plot(
            ris1_x,
            ris1_y,
            'bs',
            markersize=7,
            label='RIS1'
        )

    if ris_count >= 2:

        plt.plot(
            ris2_x,
            ris2_y,
            'cs',
            markersize=7,
            label='RIS2'
        )

    # --------------------------------------------------------
    # MACHINES
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # OUTAGE CONTOUR
    # --------------------------------------------------------

    plt.contour(
        X,
        Y,
        SNR,
        levels=[10],
        colors='red',
        linestyles='dashed'
    )

    plt.xlabel("x (meters)")
    plt.ylabel("y (meters)")

    plt.title(title)

    plt.legend()

    plt.tight_layout()

    plt.show()

# ============================================================
# HEATMAPS
# ============================================================

plot_map(
    SNR_noRIS,
    "SNR Heatmap (No RIS)",
    ris_count=0
)

plot_map(
    SNR_1RIS,
    "SNR Heatmap (1 RIS)",
    ris_count=1
)

plot_map(
    SNR_2RIS,
    "SNR Heatmap (2 RIS)",
    ris_count=2
)

# ============================================================
# ROBOT TRAJECTORY
# ============================================================

path_x = np.linspace(5, 38, 200)
path_y = np.ones_like(path_x) * 5

snr_noRIS = []
snr_1RIS = []
snr_2RIS = []

# ============================================================
# COMPUTE TRAJECTORY SNR
# ============================================================

for xu, yu in zip(path_x, path_y):

    h_d = compute_direct_gain(xu, yu)

    h_ris1 = compute_ris_gain(
        xu, yu,
        ris1_x, ris1_y
    )

    h_ris2 = compute_ris_gain(
        xu, yu,
        ris2_x, ris2_y
    )

    # --------------------------------------------------------
    # NO RIS
    # --------------------------------------------------------

    Pr_noRIS = Pt * h_d

    # --------------------------------------------------------
    # 1 RIS
    # --------------------------------------------------------

    H_1RIS = (
        np.sqrt(h_d) +
        np.sqrt(h_ris1)
    )

    Pr_1RIS = Pt * (H_1RIS ** 2)

    # --------------------------------------------------------
    # 2 RIS
    # --------------------------------------------------------

    H_2RIS = (
        np.sqrt(h_d) +
        np.sqrt(h_ris1) +
        np.sqrt(h_ris2)
    )

    Pr_2RIS = Pt * (H_2RIS ** 2)

    # --------------------------------------------------------
    # SNR
    # --------------------------------------------------------

    snr_noRIS.append(
        10 * np.log10(Pr_noRIS / noise)
    )

    snr_1RIS.append(
        10 * np.log10(Pr_1RIS / noise)
    )

    snr_2RIS.append(
        10 * np.log10(Pr_2RIS / noise)
    )

# ============================================================
# PLOT ROBOT TRAJECTORY SNR
# ============================================================

plt.figure(figsize=(10, 5))

plt.plot(
    path_x,
    snr_noRIS,
    linewidth=2,
    label='No RIS'
)

plt.plot(
    path_x,
    snr_1RIS,
    linewidth=2,
    label='1 RIS'
)

plt.plot(
    path_x,
    snr_2RIS,
    linewidth=2,
    label='2 RIS'
)

# outage threshold

plt.axhline(
    10,
    color='red',
    linestyle='--',
    label='Outage Threshold'
)

plt.xlabel("Robot Position (meters)")
plt.ylabel("SNR (dB)")

plt.title("Robot Trajectory SNR")

plt.grid(True)

plt.legend()

plt.tight_layout()

plt.show()

# ============================================================
# COVERAGE PROBABILITY
# ============================================================

SNR_threshold = 10

coverage_noRIS = np.mean(
    SNR_noRIS > SNR_threshold
)

coverage_1RIS = np.mean(
    SNR_1RIS > SNR_threshold
)

coverage_2RIS = np.mean(
    SNR_2RIS > SNR_threshold
)

coverage_values = [
    coverage_noRIS * 100,
    coverage_1RIS * 100,
    coverage_2RIS * 100
]

ris_counts = [0, 1, 2]

print("\nCoverage Results")
print("----------------------------")

print(f"No RIS : {coverage_values[0]:.2f}%")
print(f"1 RIS  : {coverage_values[1]:.2f}%")
print(f"2 RIS  : {coverage_values[2]:.2f}%")

# ============================================================
# PLOT COVERAGE PROBABILITY
# ============================================================

plt.figure(figsize=(7, 5))

plt.plot(
    ris_counts,
    coverage_values,
    marker='o',
    linewidth=2
)

plt.xlabel("Number of RIS Panels")
plt.ylabel("Coverage Probability (%)")

plt.title("Coverage Probability vs RIS Deployment")

plt.xticks([0, 1, 2])

plt.grid(True)

plt.tight_layout()

plt.show()
