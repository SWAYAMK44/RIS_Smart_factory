import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle

# ============================================================
# Factory Parameters
# ============================================================

factory_length = 40
factory_width = 20

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

# RIS 1
ris1_x, ris1_y = 38, 12

# RIS 2
ris2_x, ris2_y = 30, 3

# ============================================================
# Machines / Obstacles
# ============================================================

machines = [
    (15, 25, 6, 14),
    (10, 13, 2, 6),
    (28, 32, 10, 18)
]

# ============================================================
# Channel Parameters
# ============================================================

alpha = 2
C0 = 1e-3

# ============================================================
# Shadowing Model
# ============================================================

def shadow_loss(xu, yu):

    loss_dB = 0

    for (xmin, xmax, ymin, ymax) in machines:

        if xu > xmax and ymin <= yu <= ymax:

            depth = xu - xmax

            loss_dB += 12 + 0.8 * depth

    return loss_dB

# ============================================================
# Direct Path Power
# ============================================================

def compute_direct_power(xu, yu):

    d = np.sqrt((xu - ap_x)**2 + (yu - ap_y)**2) + 1e-3

    path_loss = C0 * (d ** -alpha)

    shadow_dB = shadow_loss(xu, yu)

    shadow_linear = 10 ** (-shadow_dB / 10)

    return Pt * path_loss * shadow_linear

# ============================================================
# RIS Reflected Power
# ============================================================

def compute_ris_power(xu, yu, ris_x, ris_y):

    # AP -> RIS

    d_AR = np.sqrt((ap_x - ris_x)**2 + (ap_y - ris_y)**2) + 1e-3

    G = C0 * (d_AR ** -alpha)

    # RIS -> User

    d_RU = np.sqrt((xu - ris_x)**2 + (yu - ris_y)**2) + 1e-3

    h_r = C0 * (d_RU ** -alpha)

    # RIS gain

    return Pt * (N ** 2) * G * h_r

# ============================================================
# Robot Trajectory
# ============================================================

path_x = np.linspace(5, 38, 220)

path_y = np.ones_like(path_x) * 5

# ============================================================
# Create Figure
# ============================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# ============================================================
# LEFT PLOT : FACTORY
# ============================================================

ax1.set_xlim(0, factory_length)
ax1.set_ylim(0, factory_width)

ax1.set_title("Factory Layout")

ax1.set_xlabel("x (meters)")
ax1.set_ylabel("y (meters)")

# AP

ax1.plot(ap_x, ap_y, 'ro', markersize=10, label='AP')

# RIS

ax1.plot(ris1_x, ris1_y, 'bs', markersize=8, label='RIS1')

ax1.plot(ris2_x, ris2_y, 'cs', markersize=8, label='RIS2')

# Machines

for (xmin, xmax, ymin, ymax) in machines:

    rect = Rectangle(
        (xmin, ymin),
        xmax - xmin,
        ymax - ymin,
        facecolor='gray',
        edgecolor='black',
        alpha=0.7
    )

    ax1.add_patch(rect)

# Robot trajectory line

ax1.plot(path_x, path_y, 'k--', alpha=0.5)

# Robot marker

robot_marker, = ax1.plot([], [], 'mo', markersize=10, label='Robot')

# Signal paths

line_direct, = ax1.plot([], [], 'r--', linewidth=2, label='Direct Path')

line_ris1a, = ax1.plot([], [], 'g-', linewidth=2)
line_ris1b, = ax1.plot([], [], 'g-', linewidth=2, label='RIS1 Path')

line_ris2a, = ax1.plot([], [], 'b-', linewidth=2)
line_ris2b, = ax1.plot([], [], 'b-', linewidth=2, label='RIS2 Path')

ax1.legend(loc='upper left')

# ============================================================
# RIGHT PLOT : SNR GRAPH
# ============================================================

ax2.set_xlim(path_x.min(), path_x.max())

ax2.set_ylim(0, 70)

ax2.set_title("Robot Trajectory SNR")

ax2.set_xlabel("Robot Position (meters)")

ax2.set_ylabel("SNR (dB)")

ax2.grid(True)

# Threshold

ax2.axhline(
    10,
    color='red',
    linestyle='--',
    label='Outage Threshold'
)

# Live SNR curve

snr_line, = ax2.plot(
    [],
    [],
    linewidth=2,
    color='blue',
    label='SNR'
)

# Current point

current_point, = ax2.plot([], [], 'ro', markersize=8)

ax2.legend()

# ============================================================
# Storage Arrays
# ============================================================

trajectory_positions = []

snr_values = []

# ============================================================
# Animation Update Function
# ============================================================

def update(frame):

    xu = path_x[frame]

    yu = path_y[frame]

    # --------------------------------------------------------
    # Robot position update
    # --------------------------------------------------------

    robot_marker.set_data([xu], [yu])

    # --------------------------------------------------------
    # Compute received powers
    # --------------------------------------------------------

    Pr_direct = compute_direct_power(xu, yu)

    Pr_ris1 = compute_ris_power(xu, yu, ris1_x, ris1_y)

    Pr_ris2 = compute_ris_power(xu, yu, ris2_x, ris2_y)

    total_power = Pr_direct + Pr_ris1 + Pr_ris2

    snr = 10 * np.log10(total_power / noise)

    # --------------------------------------------------------
    # Store values
    # --------------------------------------------------------

    trajectory_positions.append(xu)

    snr_values.append(snr)

    # --------------------------------------------------------
    # Update SNR graph
    # --------------------------------------------------------

    snr_line.set_data(
        trajectory_positions,
        snr_values
    )

    current_point.set_data([xu], [snr])

    # --------------------------------------------------------
    # Update signal paths
    # --------------------------------------------------------

    # Direct path

    line_direct.set_data(
        [ap_x, xu],
        [ap_y, yu]
    )

    # RIS1 path

    line_ris1a.set_data(
        [ap_x, ris1_x],
        [ap_y, ris1_y]
    )

    line_ris1b.set_data(
        [ris1_x, xu],
        [ris1_y, yu]
    )

    # RIS2 path

    line_ris2a.set_data(
        [ap_x, ris2_x],
        [ap_y, ris2_y]
    )

    line_ris2b.set_data(
        [ris2_x, xu],
        [ris2_y, yu]
    )

    return (
        robot_marker,
        snr_line,
        current_point,
        line_direct,
        line_ris1a,
        line_ris1b,
        line_ris2a,
        line_ris2b
    )

# ============================================================
# Run Animation
# ============================================================

ani = FuncAnimation(
    fig,
    update,
    frames=len(path_x),
    interval=80,
    repeat=False
)

plt.tight_layout()

plt.show()