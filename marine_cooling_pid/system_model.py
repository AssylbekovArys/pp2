"""
Marine Diesel Engine Cooling System - Plant Model Definition
=============================================================

Based on: "Simulation Modelling of Marine Diesel Engine Cooling System"
(ResearchGate, 2021)

The two-circuit cooling system consists of:
  - HTC (High Temperature Circuit): Engine jacket water cooling
    * G1 = 0.015/(s+1) — Cylinder liner heat exchange
    * G2 = 0.1/(s+1)   — Engine jacket cooler
  - LTC (Low Temperature Circuit): Sea water / auxiliary cooling
    * G3 = 0.1/(s+1)   — Charge air cooler
    * G4 = 0.1/(s+1)   — Lubricating oil cooler

Setpoint: 80°C (engine jacket water temperature)

Block diagram structure:
  Setpoint → [Σ] → [PID(s)] → ┬→ [G1] ─┐
              ↑                 ├→ [G2] ─┤→ [Σ_HTC]──┐
              │                 ├→ [G3] ─┐              ├→ [Σ_total] → Output
              │                 └→ [G4] ─┤→ [Σ_LTC]──┘      │
              └──────────────────────────────────────────────┘
"""

import numpy as np
import control as ctrl


# =============================================================================
# System Parameters
# =============================================================================

SETPOINT = 80.0  # Target temperature [°C]

# Transfer function gains
K1 = 0.015   # Cylinder liner heat exchange gain
K2 = 0.1     # Engine jacket cooler gain
K3 = 0.1     # Charge air cooler gain
K4 = 0.1     # Lubricating oil cooler gain

# Time constants [seconds]
TAU1 = 1.0   # Cylinder liner time constant
TAU2 = 1.0   # Engine jacket cooler time constant
TAU3 = 1.0   # Charge air cooler time constant
TAU4 = 1.0   # Lubricating oil cooler time constant

# Transport delays [seconds] — added for realism (physical heat transport)
DELAY1 = 0.1   # Cylinder liner delay
DELAY2 = 0.2   # Engine jacket cooler delay
DELAY3 = 0.15  # Charge air cooler delay
DELAY4 = 0.25  # Lubricating oil cooler delay

# Padé approximation order for delays
PADE_ORDER = 3


# =============================================================================
# Individual Component Transfer Functions (without delay)
# =============================================================================

def get_component_tf_no_delay(K, tau):
    """
    Create a first-order transfer function: G(s) = K / (tau*s + 1)
    """
    return ctrl.tf([K], [tau, 1])


def get_component_tf_with_delay(K, tau, delay, pade_order=PADE_ORDER):
    """
    Create a first-order transfer function with transport delay (Padé approx):
    G(s) = K * e^(-delay*s) / (tau*s + 1)
    """
    G_no_delay = ctrl.tf([K], [tau, 1])
    if delay > 0:
        num_pade, den_pade = ctrl.pade(delay, pade_order)
        G_delay = ctrl.tf(num_pade, den_pade)
        return G_no_delay * G_delay
    return G_no_delay


# =============================================================================
# Subsystem Transfer Functions
# =============================================================================

def get_htc_plant(with_delay=True):
    """
    HTC (High Temperature Circuit) plant transfer function.
    G_HTC(s) = G1(s) + G2(s)

    Without delay: G_HTC = (K1 + K2) / (tau*s + 1) = 0.115/(s+1)
    """
    if with_delay:
        G1 = get_component_tf_with_delay(K1, TAU1, DELAY1)
        G2 = get_component_tf_with_delay(K2, TAU2, DELAY2)
    else:
        G1 = get_component_tf_no_delay(K1, TAU1)
        G2 = get_component_tf_no_delay(K2, TAU2)
    return ctrl.parallel(G1, G2)


def get_ltc_plant(with_delay=True):
    """
    LTC (Low Temperature Circuit) plant transfer function.
    G_LTC(s) = G3(s) + G4(s)

    Without delay: G_LTC = (K3 + K4) / (tau*s + 1) = 0.2/(s+1)
    """
    if with_delay:
        G3 = get_component_tf_with_delay(K3, TAU3, DELAY3)
        G4 = get_component_tf_with_delay(K4, TAU4, DELAY4)
    else:
        G3 = get_component_tf_no_delay(K3, TAU3)
        G4 = get_component_tf_no_delay(K4, TAU4)
    return ctrl.parallel(G3, G4)


def get_combined_plant(with_delay=True):
    """
    Combined cooling system plant transfer function.
    G_total(s) = G_HTC(s) + G_LTC(s) = G1 + G2 + G3 + G4

    Without delay: G_total = 0.315/(s+1)
    With delay: Approximated as single FOPDT to avoid numerical issues
    from high-order parallel Padé systems.
    """
    if with_delay:
        # Use effective FOPDT to avoid numerical issues with 4 parallel Padé TFs
        K_eff = K1 + K2 + K3 + K4  # 0.315
        tau_eff = TAU1              # 1.0 (all same)
        theta_eff = (K1 * DELAY1 + K2 * DELAY2 + K3 * DELAY3 + K4 * DELAY4) / K_eff
        return get_component_tf_with_delay(K_eff, tau_eff, theta_eff, PADE_ORDER)
    else:
        G_HTC = get_htc_plant(False)
        G_LTC = get_ltc_plant(False)
        return ctrl.parallel(G_HTC, G_LTC)


# =============================================================================
# FOPDT (First Order Plus Dead Time) Approximation Parameters
# =============================================================================

def get_fopdt_params(subsystem='combined'):
    """
    Return FOPDT parameters (K, tau, theta) for the specified subsystem.
    These are used for analytical PID tuning methods.

    For the combined parallel subsystems, the effective FOPDT is approximated.
    """
    if subsystem == 'htc':
        K_eff = K1 + K2                        # 0.115
        tau_eff = TAU1                          # 1.0 (same time constants)
        theta_eff = (K1 * DELAY1 + K2 * DELAY2) / (K1 + K2)  # weighted avg delay
    elif subsystem == 'ltc':
        K_eff = K3 + K4                         # 0.2
        tau_eff = TAU3                           # 1.0
        theta_eff = (K3 * DELAY3 + K4 * DELAY4) / (K3 + K4)  # weighted avg delay
    elif subsystem == 'combined':
        K_eff = K1 + K2 + K3 + K4              # 0.315
        tau_eff = TAU1                           # 1.0
        theta_eff = (K1 * DELAY1 + K2 * DELAY2 + K3 * DELAY3 + K4 * DELAY4) / \
                    (K1 + K2 + K3 + K4)          # weighted avg delay
    else:
        raise ValueError(f"Unknown subsystem: {subsystem}")

    return K_eff, tau_eff, theta_eff


# =============================================================================
# PID Controller Transfer Function
# =============================================================================

def get_pid_tf(Kp, Ki, Kd, N=100):
    """
    Create a PID controller transfer function:
    C(s) = Kp + Ki/s + Kd*s / (1 + s/N)

    where N is the derivative filter coefficient.

    In standard form:
    C(s) = Kp * (1 + 1/(Ti*s) + Td*s/(1 + Td*s/N))
    where Ti = Kp/Ki, Td = Kd/Kp
    """
    # P term
    C_p = ctrl.tf([Kp], [1])

    # I term: Ki/s
    C_i = ctrl.tf([Ki], [1, 0])

    # D term with filter: Kd*N*s / (s + N)
    C_d = ctrl.tf([Kd * N, 0], [1, N])

    return C_p + C_i + C_d


# =============================================================================
# Closed-Loop System
# =============================================================================

def get_closed_loop(plant, Kp, Ki, Kd, N=100):
    """
    Create the closed-loop transfer function T(s) = C(s)*G(s) / (1 + C(s)*G(s))
    """
    C = get_pid_tf(Kp, Ki, Kd, N)
    open_loop = ctrl.series(C, plant)
    closed_loop = ctrl.feedback(open_loop, 1)
    return closed_loop


def get_closed_loop_with_controller(plant, controller):
    """
    Create the closed-loop using an existing controller transfer function.
    """
    open_loop = ctrl.series(controller, plant)
    closed_loop = ctrl.feedback(open_loop, 1)
    return closed_loop


# =============================================================================
# Display functions
# =============================================================================

def print_system_info():
    """Print system model information."""
    print("=" * 70)
    print("MARINE DIESEL ENGINE TWO-CIRCUIT COOLING SYSTEM")
    print("=" * 70)
    print()
    print("HTC (High Temperature Circuit):")
    print(f"  G1 = {K1}/({TAU1}s + 1)  [Cylinder liner, delay={DELAY1}s]")
    print(f"  G2 = {K2}/({TAU2}s + 1)  [Engine jacket cooler, delay={DELAY2}s]")
    print(f"  G_HTC = G1 + G2")
    print()
    print("LTC (Low Temperature Circuit):")
    print(f"  G3 = {K3}/({TAU3}s + 1)  [Charge air cooler, delay={DELAY3}s]")
    print(f"  G4 = {K4}/({TAU4}s + 1)  [Lube oil cooler, delay={DELAY4}s]")
    print(f"  G_LTC = G3 + G4")
    print()
    print(f"Combined plant: G_total = G_HTC + G_LTC")
    print(f"Setpoint: {SETPOINT}°C")
    print()

    for name in ['htc', 'ltc', 'combined']:
        K, tau, theta = get_fopdt_params(name)
        print(f"  {name.upper():10s} FOPDT: K={K:.4f}, tau={tau:.2f}s, theta={theta:.4f}s")

    print("=" * 70)


if __name__ == "__main__":
    print_system_info()

    # Print transfer functions
    print("\nHTC Plant (with delay):")
    print(get_htc_plant(with_delay=True))

    print("\nLTC Plant (with delay):")
    print(get_ltc_plant(with_delay=True))

    print("\nCombined Plant (with delay):")
    print(get_combined_plant(with_delay=True))
