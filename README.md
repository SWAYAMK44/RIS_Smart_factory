# RIS-Assisted Smart Factory Communication Simulation

## Overview

This project demonstrates the use of **Reconfigurable Intelligent Surfaces (RIS)** to improve wireless communication reliability in a smart factory environment.

The simulation models:

* A smart factory layout
* Metallic machines causing shadowing and dead coverage zones
* Wireless signal propagation with path loss and Rician fading
* Mobile robot (AGV) communication
* RIS-assisted signal enhancement
* Multi-RIS deployment
* Coverage and outage analysis

The main goal of the project is to study how RIS can improve communication reliability for Industrial IoT (IIoT) and mobile robotic systems operating inside complex factory environments.

---

# Features

## Factory Environment Modeling

The simulation includes:

* Access Point (AP)
* Multiple metallic machines/obstacles
* One or more RIS panels
* A moving robot trajectory

The factory layout is modeled in 2D and includes realistic blockage effects caused by machinery.

---

## Wireless Channel Modeling

The project implements:

### Large-Scale Path Loss

Distance-dependent path loss:

[
L(d) = C_0 d^{-\alpha}
]

where:

* (d) = propagation distance
* (\alpha) = path loss exponent
* (C_0) = reference path loss constant

---

### Rician Fading

The wireless links are modeled using a Rician fading channel:

[
h = \sqrt{\frac{K}{K+1}} + \sqrt{\frac{1}{K+1}}g
]

where:

* (K) = Rician K-factor
* (g \sim \mathcal{CN}(0,1))

This allows the simulation to model:

* LOS propagation
* Reflections from industrial surfaces
* Random multipath fading

---

### Industrial Shadowing Model

Metallic machines introduce additional attenuation.

The simulation includes a cumulative shadowing model where signal attenuation increases deeper into blocked regions.

This creates:

* Dead coverage zones
* Gradual signal degradation
* Spatially varying connectivity

---

## RIS-Assisted Communication

The RIS is modeled as a passive reflective surface consisting of:

[
N = 64
]

reflecting elements.

The RIS creates an additional communication path:

[
\text{AP} \rightarrow \text{RIS} \rightarrow \text{User}
]

The reflected signal gain is modeled using coherent combining:

[
|h_{RIS}|^2 \propto N^2
]

The simulation supports:

* Single RIS deployment
* Multi-RIS deployment
* RIS-assisted coverage enhancement

---

# Simulations Included

The project generates:

## 1. SNR Heatmaps

Heatmaps showing signal quality across the factory floor:

* Without RIS
* With 1 RIS
* With 2 RISs

These plots visualize:

* Dead coverage zones
* Shadowing regions
* Coverage improvement due to RIS

---

## 2. Robot Trajectory SNR

A mobile robot moves through the factory.

The simulation computes:

[
SNR(x(t), y(t))
]

along the robot path.

This demonstrates:

* Signal degradation behind machinery
* RIS-assisted connectivity recovery
* Reliability improvement for AGVs

---

## 3. Coverage Probability Analysis

Coverage probability is computed using:

[
P(SNR > \gamma_{th})
]

where:

* (\gamma_{th}) = outage threshold

The project compares:

* No RIS
* Single RIS
* Multi-RIS

---

# Project Structure

```text
.
├── main.py
├── demo.py
├── README.md
```

---

# Files

## main.py

Runs the complete RIS simulation framework:

* Heatmaps
* Monte Carlo simulations
* Rician fading analysis
* Robot trajectory SNR
* Coverage probability analysis

---

## demo.py

Runs the animated demonstration.

The demo visualizes:

* Robot movement
* Signal propagation paths
* RIS-assisted reflected paths
* Live SNR updates

### To run the demo:

```bash
python demo.py
```

This animation is useful for:

* Project presentations
* Demonstrations
* Explaining RIS concepts visually

---

# Requirements

Install dependencies using:

```bash
pip install numpy matplotlib
```

---

# How to Run


## Run Animated Demo

```bash
python demo.py
```

---

# Example Results

The simulation produces:

* SNR heatmaps
* Coverage maps
* Outage contours
* Robot trajectory SNR plots
* Coverage probability comparisons

The results show:

* Metallic machines create severe dead zones
* RIS significantly improves coverage
* Multi-RIS deployment improves reliability further
* AGV communication reliability improves with RIS assistance

---

# Applications

This project is relevant for:

* Smart factories
* Industrial IoT (IIoT)
* Mobile robots and AGVs
* 6G communication systems
* RIS-assisted wireless networks
* Industrial wireless reliability studies

---

# Future Improvements

Possible future extensions include:

* RIS placement optimization
* Dynamic RIS phase adaptation
* Phase quantization
* Imperfect CSI analysis
* Multi-user communication
* OFDM channel modeling
* Real-time AGV trajectory adaptation
* Reinforcement learning-based RIS control

---

# Research Motivation

Industrial environments suffer from:

* Severe shadowing
* Signal blockage
* Connectivity dead zones
* Reliability challenges for mobile robots

RIS technology enables programmable wireless propagation and can significantly improve communication reliability in such environments.

This project investigates RIS-assisted communication enhancement for smart factory applications.

---

# Author
Harsh Modi and Swayam Kotecha IIIT Bangalore
Developed as part of a study on RIS-assisted Industrial IoT communication systems and smart factory wireless reliability.
