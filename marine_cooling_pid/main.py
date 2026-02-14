#!/usr/bin/env python3
"""
=============================================================================
PID Controller for Marine Diesel Engine Two-Circuit Cooling System
=============================================================================

Course Project: Regulator Synthesis (SIS 3)

Based on: "Simulation Modelling of Marine Diesel Engine Cooling System"
https://www.researchgate.net/publication/351042446

System Description:
  Two-circuit cooling system with HTC and LTC loops:
  - HTC (High Temperature Circuit): maintains engine jacket water at 80°C
  - LTC (Low Temperature Circuit): sea water auxiliary cooling

  Block diagram (from assignment):
    80 → [Σ] → [PID(s)] → ┬→ [0.015/(s+1)] → [Σ] ─┐
          ↑                 ├→ [0.1/(s+1)]  ──→↗     ├→ [Σ] → Output
          │                 ├→ [0.1/(s+1)]  → [Σ] ─┘
          │                 └→ [0.1/(s+1)]  ──→↗      │
          └────────────────────────────────────────────┘

Report Structure:
  1. PID Control Law Description
  2. System Parameters Specification
  3. Mathematical Model (Python equivalent of MATLAB/Simulink)
  4. PID Tuning:
     4.1 Desired dynamics identification
     4.2 Method 1: SIMC Autotuning
     4.2 Method 2: Ziegler-Nichols
     4.3 Coefficients table
  5. Results plots with dynamics analysis
  6. Comparison of different controller coefficients
  7. Best solution identification
  8. Conclusion

Author: Marine Engineering Student
Date: February 2026
=============================================================================
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving plots
import matplotlib.pyplot as plt
import control as ctrl

# Import project modules
from system_model import (
    SETPOINT, get_htc_plant, get_ltc_plant, get_combined_plant,
    get_pid_tf, get_closed_loop, print_system_info, get_fopdt_params,
    K1, K2, K3, K4, TAU1, TAU2, TAU3, TAU4, DELAY1, DELAY2, DELAY3, DELAY4
)
from pid_tuning import (
    tune_simc, tune_ziegler_nichols_step, tune_ziegler_nichols_ultimate,
    tune_cohen_coon, tune_optimization
)
from performance import (
    calculate_metrics, print_metrics, print_metrics_table
)


# Output directory for plots
PLOT_DIR = os.path.join(os.path.dirname(__file__), 'plots')
os.makedirs(PLOT_DIR, exist_ok=True)

# Simulation parameters
T_SIM = 30.0    # Simulation time [s]
N_POINTS = 3000  # Number of time points


def save_fig(fig, filename):
    """Save figure to the plots directory."""
    filepath = os.path.join(PLOT_DIR, filename)
    fig.savefig(filepath, dpi=150, bbox_inches='tight')
    print(f"  [Saved] {filepath}")
    plt.close(fig)


# =============================================================================
# SECTION 1: PID Control Law Description
# =============================================================================

def section_1_control_law():
    """
    Describe the PID control law with formulas.
    """
    print("\n" + "=" * 70)
    print("SECTION 1: PID CONTROL LAW DESCRIPTION")
    print("=" * 70)
    print("""
PID (Proportional-Integral-Derivative) Controller

The PID control law in the time domain:

    u(t) = Kp * e(t) + Ki * ∫e(τ)dτ + Kd * de(t)/dt

where:
    e(t) = r(t) - y(t)  — tracking error
    r(t) — reference (setpoint = 80°C)
    y(t) — measured output (coolant temperature)
    u(t) — control signal (coolant valve position)

In the Laplace domain (transfer function form):

    C(s) = Kp + Ki/s + Kd*s/(1 + s/N)

    where N = 100 (derivative filter coefficient)

Standard (ISA) form:

    C(s) = Kp * [1 + 1/(Ti*s) + Td*s/(1 + Td*s/N)]

    where:
        Ti = Kp/Ki  — integral time constant
        Td = Kd/Kp  — derivative time constant

Influence of Each PID Component:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  P (Proportional): Reduces rise time, but cannot eliminate steady-state
                     error alone. Increasing Kp → faster response but
                     larger overshoot and potential instability.

  I (Integral):     Eliminates steady-state error by accumulating error
                     over time. Increasing Ki → faster error elimination
                     but may increase overshoot and settling time.

  D (Derivative):   Improves transient response by anticipating future
                     error. Reduces overshoot and settling time.
                     Increasing Kd → better damping but amplifies noise.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PID Effect Summary Table:
┌──────────────┬───────────┬───────────┬──────────────┬─────────────────┐
│ Parameter ↑  │ Rise time │ Overshoot │ Settling time│ Steady-st. error│
├──────────────┼───────────┼───────────┼──────────────┼─────────────────┤
│ Kp increase  │    ↓      │    ↑      │ Small change │       ↓         │
│ Ki increase  │    ↓      │    ↑      │      ↑       │   Eliminates    │
│ Kd increase  │ Sm.change │    ↓      │      ↓       │   Small change  │
└──────────────┴───────────┴───────────┴──────────────┴─────────────────┘
""")


# =============================================================================
# SECTION 2: System Parameters
# =============================================================================

def section_2_parameters():
    """
    Specify and calculate system parameters.
    """
    print("\n" + "=" * 70)
    print("SECTION 2: SYSTEM PARAMETERS SPECIFICATION")
    print("=" * 70)
    print_system_info()

    print("\nPlant Transfer Functions (individual components):")
    print(f"  G1(s) = {K1} / ({TAU1}s + 1) * e^(-{DELAY1}s)  [Cylinder liner]")
    print(f"  G2(s) = {K2} / ({TAU2}s + 1) * e^(-{DELAY2}s)  [Engine jacket cooler]")
    print(f"  G3(s) = {K3} / ({TAU3}s + 1) * e^(-{DELAY3}s)  [Charge air cooler]")
    print(f"  G4(s) = {K4} / ({TAU4}s + 1) * e^(-{DELAY4}s)  [Lube oil cooler]")

    print("\nSubsystem Transfer Functions:")
    K_htc, tau_htc, theta_htc = get_fopdt_params('htc')
    K_ltc, tau_ltc, theta_ltc = get_fopdt_params('ltc')
    K_comb, tau_comb, theta_comb = get_fopdt_params('combined')

    print(f"  HTC:      G_HTC(s)  ≈ {K_htc:.4f} / ({tau_htc}s + 1) * e^(-{theta_htc:.4f}s)")
    print(f"  LTC:      G_LTC(s)  ≈ {K_ltc:.4f} / ({tau_ltc}s + 1) * e^(-{theta_ltc:.4f}s)")
    print(f"  Combined: G_total(s)≈ {K_comb:.4f} / ({tau_comb}s + 1) * e^(-{theta_comb:.4f}s)")


# =============================================================================
# SECTION 3: Open-Loop System Analysis
# =============================================================================

def section_3_open_loop():
    """
    Analyze the open-loop system behavior (without controller).
    """
    print("\n" + "=" * 70)
    print("SECTION 3: OPEN-LOOP SYSTEM ANALYSIS (Without Controller)")
    print("=" * 70)

    t = np.linspace(0, T_SIM, N_POINTS)

    # Get plants
    G_htc = get_htc_plant(with_delay=True)
    G_ltc = get_ltc_plant(with_delay=True)
    G_combined = get_combined_plant(with_delay=True)

    # Step response of each subsystem
    t_htc, y_htc = ctrl.step_response(G_htc, t)
    t_ltc, y_ltc = ctrl.step_response(G_ltc, t)
    t_comb, y_comb = ctrl.step_response(G_combined, t)

    # Scale by setpoint for physical interpretation
    y_htc_scaled = y_htc * SETPOINT
    y_ltc_scaled = y_ltc * SETPOINT
    y_comb_scaled = y_comb * SETPOINT

    # Plot open-loop step responses
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Open-Loop Step Response — Marine Diesel Engine Cooling System',
                 fontsize=14, fontweight='bold')

    # Individual components step response
    ax = axes[0, 0]
    for K, tau, delay, label, color in [
        (K1, TAU1, DELAY1, f'G1: Cylinder liner (K={K1})', 'blue'),
        (K2, TAU2, DELAY2, f'G2: Jacket cooler (K={K2})', 'red'),
        (K3, TAU3, DELAY3, f'G3: Charge air cooler (K={K3})', 'green'),
        (K4, TAU4, DELAY4, f'G4: Lube oil cooler (K={K4})', 'orange'),
    ]:
        from system_model import get_component_tf_with_delay
        G = get_component_tf_with_delay(K, tau, delay)
        t_comp, y_comp = ctrl.step_response(G, t)
        ax.plot(t_comp, y_comp, label=label, color=color, linewidth=1.5)
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Output')
    ax.set_title('Individual Component Step Responses')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # HTC step response
    ax = axes[0, 1]
    ax.plot(t_htc, y_htc, 'b-', linewidth=2, label='HTC (G1 + G2)')
    ax.axhline(y=K1 + K2, color='b', linestyle='--', alpha=0.5,
               label=f'Steady state = {K1+K2:.3f}')
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Output')
    ax.set_title('HTC Subsystem Step Response')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # LTC step response
    ax = axes[1, 0]
    ax.plot(t_ltc, y_ltc, 'r-', linewidth=2, label='LTC (G3 + G4)')
    ax.axhline(y=K3 + K4, color='r', linestyle='--', alpha=0.5,
               label=f'Steady state = {K3+K4:.3f}')
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Output')
    ax.set_title('LTC Subsystem Step Response')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Combined step response
    ax = axes[1, 1]
    ax.plot(t_comb, y_comb, 'k-', linewidth=2, label='Combined (HTC + LTC)')
    ax.axhline(y=K1+K2+K3+K4, color='k', linestyle='--', alpha=0.5,
               label=f'Steady state = {K1+K2+K3+K4:.3f}')
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Output')
    ax.set_title('Combined System Step Response')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    save_fig(fig, '01_open_loop_step_responses.png')

    # Open-loop Bode plot
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle('Open-Loop Bode Diagram — Combined Plant', fontsize=14, fontweight='bold')

    omega = np.logspace(-2, 2, 1000)
    mag, phase, freq = ctrl.frequency_response(G_combined, omega)

    axes[0].semilogx(freq, 20 * np.log10(mag), 'b-', linewidth=2)
    axes[0].set_ylabel('Magnitude [dB]')
    axes[0].set_title('Magnitude')
    axes[0].grid(True, alpha=0.3, which='both')

    axes[1].semilogx(freq, np.degrees(phase), 'r-', linewidth=2)
    axes[1].set_ylabel('Phase [degrees]')
    axes[1].set_xlabel('Frequency [rad/s]')
    axes[1].set_title('Phase')
    axes[1].grid(True, alpha=0.3, which='both')
    axes[1].axhline(y=-180, color='k', linestyle='--', alpha=0.5)

    plt.tight_layout()
    save_fig(fig, '02_open_loop_bode.png')

    print("\nOpen-loop steady-state values (for unit step input):")
    print(f"  HTC:      {K1+K2:.4f}")
    print(f"  LTC:      {K3+K4:.4f}")
    print(f"  Combined: {K1+K2+K3+K4:.4f}")
    print("\nNote: Without a controller, the system cannot reach setpoint of 80°C.")
    print(f"      Open-loop gain = {K1+K2+K3+K4:.4f} << 1")
    print("      PID controller is REQUIRED to achieve the desired temperature.")


# =============================================================================
# SECTION 4: PID Controller Tuning
# =============================================================================

def section_4_pid_tuning():
    """
    PID tuning using two methods + comparison.
    Returns tuning results for all subsystems.
    """
    print("\n" + "=" * 70)
    print("SECTION 4: PID CONTROLLER TUNING")
    print("=" * 70)

    results = {}

    for subsystem_name, get_plant in [
        ('HTC', get_htc_plant),
        ('LTC', get_ltc_plant),
        ('Combined', get_combined_plant),
    ]:
        print(f"\n{'*' * 60}")
        print(f"  Tuning PID for: {subsystem_name} subsystem")
        print(f"{'*' * 60}")

        plant = get_plant(with_delay=True)
        sub_key = subsystem_name.lower()

        sub_results = {}

        # Method 1: SIMC (Autotuning)
        print(f"\n--- Method 1: SIMC Autotuning ---")
        Kp, Ki, Kd = tune_simc(sub_key, verbose=True)
        sub_results['SIMC (Autotuning)'] = {'Kp': Kp, 'Ki': Ki, 'Kd': Kd}

        # Method 2: Ziegler-Nichols (Step Response)
        print(f"\n--- Method 2: Ziegler-Nichols ---")
        Kp, Ki, Kd = tune_ziegler_nichols_step(sub_key, verbose=True)
        sub_results['Ziegler-Nichols'] = {'Kp': Kp, 'Ki': Ki, 'Kd': Kd}

        # Additional: Ziegler-Nichols Ultimate Gain
        Kp, Ki, Kd = tune_ziegler_nichols_ultimate(plant, verbose=True, label=subsystem_name)
        if Kp is not None:
            sub_results['ZN (Ultimate)'] = {'Kp': Kp, 'Ki': Ki, 'Kd': Kd}

        # Additional: Cohen-Coon
        Kp, Ki, Kd = tune_cohen_coon(sub_key, verbose=True)
        sub_results['Cohen-Coon'] = {'Kp': Kp, 'Ki': Ki, 'Kd': Kd}

        # Additional: ITAE Optimization
        print(f"\n--- ITAE Optimization (finding optimal coefficients) ---")
        Kp, Ki, Kd = tune_optimization(plant, verbose=True, label=subsystem_name)
        sub_results['ITAE Optimal'] = {'Kp': Kp, 'Ki': Ki, 'Kd': Kd}

        results[subsystem_name] = sub_results

        # Print coefficients table
        print(f"\n{'='*65}")
        print(f"  PID Coefficients Table — {subsystem_name}")
        print(f"{'='*65}")
        print(f"  {'Method':<25s} {'Kp':>10s} {'Ki':>10s} {'Kd':>10s}")
        print(f"  {'-'*55}")
        for method, params in sub_results.items():
            print(f"  {method:<25s} {params['Kp']:10.4f} {params['Ki']:10.4f} {params['Kd']:10.6f}")
        print(f"  {'='*55}")

    return results


# =============================================================================
# SECTION 5: Closed-Loop Simulation & Results
# =============================================================================

def section_5_simulation(tuning_results):
    """
    Simulate closed-loop system with all tuning methods.
    Generate plots and performance tables.
    """
    print("\n" + "=" * 70)
    print("SECTION 5: CLOSED-LOOP SIMULATION RESULTS")
    print("=" * 70)

    t = np.linspace(0, T_SIM, N_POINTS)
    all_metrics = {}

    for subsystem_name, get_plant in [
        ('HTC', get_htc_plant),
        ('LTC', get_ltc_plant),
        ('Combined', get_combined_plant),
    ]:
        print(f"\n{'*' * 60}")
        print(f"  Simulating: {subsystem_name} subsystem")
        print(f"{'*' * 60}")

        plant = get_plant(with_delay=True)
        sub_results = tuning_results[subsystem_name]
        sub_metrics = {}

        # Create figure for this subsystem
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Closed-Loop Step Response — {subsystem_name} Subsystem\n'
                     f'(Setpoint = {SETPOINT}°C)',
                     fontsize=14, fontweight='bold')

        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']

        # --- Plot 1: All methods on one graph ---
        ax = axes[0, 0]
        for idx, (method, params) in enumerate(sub_results.items()):
            try:
                T_cl = get_closed_loop(plant, params['Kp'], params['Ki'], params['Kd'])
                t_out, y_out = ctrl.step_response(T_cl, t)
                y_scaled = y_out * SETPOINT

                ax.plot(t_out, y_scaled, color=colors[idx % len(colors)],
                        linewidth=1.5, label=method)

                # Calculate metrics
                metrics = calculate_metrics(t_out, y_out, setpoint=1.0)
                sub_metrics[method] = metrics
                print_metrics(metrics, f"{subsystem_name} — {method}")

            except Exception as e:
                print(f"  WARNING: Simulation failed for {method}: {e}")

        ax.axhline(y=SETPOINT, color='k', linestyle='--', alpha=0.5, label='Setpoint')
        ax.fill_between(t, SETPOINT * 0.98, SETPOINT * 1.02, alpha=0.1, color='green',
                        label='±2% band')
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Temperature [°C]')
        ax.set_title('Comparison of All Tuning Methods')
        ax.legend(fontsize=7, loc='lower right')
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, T_SIM])

        # --- Plot 2: Desired dynamics (best method) ---
        ax = axes[0, 1]
        if sub_metrics:
            # Find method with lowest ITAE
            best_method = min(sub_metrics, key=lambda m: sub_metrics[m]['itae'])
            best_params = sub_results[best_method]
            T_cl = get_closed_loop(plant, best_params['Kp'], best_params['Ki'],
                                   best_params['Kd'])
            t_out, y_out = ctrl.step_response(T_cl, t)
            y_scaled = y_out * SETPOINT
            best_m = sub_metrics[best_method]

            ax.plot(t_out, y_scaled, 'b-', linewidth=2, label=f'Best: {best_method}')
            ax.axhline(y=SETPOINT, color='k', linestyle='--', alpha=0.5, label='Setpoint')

            # Annotate key characteristics
            # Rise time
            if best_m['rise_time'] < T_SIM:
                ax.axvline(x=best_m['rise_time'], color='g', linestyle=':', alpha=0.7)
                ax.annotate(f"Rise time\n{best_m['rise_time']:.2f}s",
                            xy=(best_m['rise_time'], SETPOINT * 0.5),
                            fontsize=8, color='green')

            # Peak / Overshoot
            if best_m['overshoot'] > 0.1:
                ax.annotate(f"Overshoot\n{best_m['overshoot']:.1f}%",
                            xy=(best_m['peak_time'], best_m['y_max'] * SETPOINT),
                            xytext=(best_m['peak_time'] + 1, best_m['y_max'] * SETPOINT + 2),
                            arrowprops=dict(arrowstyle='->', color='red'),
                            fontsize=8, color='red')

            # Settling time
            if best_m['settling_time'] < T_SIM:
                ax.axvline(x=best_m['settling_time'], color='orange', linestyle=':', alpha=0.7)
                ax.annotate(f"Settling time\n{best_m['settling_time']:.2f}s",
                            xy=(best_m['settling_time'], SETPOINT * 0.95),
                            fontsize=8, color='orange')

            # 2% band
            ax.fill_between(t, SETPOINT * 0.98, SETPOINT * 1.02, alpha=0.1, color='green')

            ax.set_xlabel('Time [s]')
            ax.set_ylabel('Temperature [°C]')
            ax.set_title(f'Desired Dynamics — Best Method: {best_method}')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
            ax.set_xlim([0, T_SIM])

        # --- Plot 3: Error signal ---
        ax = axes[1, 0]
        for idx, (method, params) in enumerate(sub_results.items()):
            try:
                T_cl = get_closed_loop(plant, params['Kp'], params['Ki'], params['Kd'])
                t_out, y_out = ctrl.step_response(T_cl, t)
                error = (1.0 - y_out) * SETPOINT  # Error in °C

                ax.plot(t_out, error, color=colors[idx % len(colors)],
                        linewidth=1.2, label=method)
            except Exception:
                pass

        ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Error [°C]')
        ax.set_title('Tracking Error e(t) = r(t) - y(t)')
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, T_SIM])

        # --- Plot 4: Control signal ---
        ax = axes[1, 1]
        for idx, (method, params) in enumerate(sub_results.items()):
            try:
                C = get_pid_tf(params['Kp'], params['Ki'], params['Kd'])
                # Control effort: C(s) / (1 + C(s)*G(s)) * R(s)
                sensitivity = ctrl.feedback(C, plant)
                t_out, u_out = ctrl.step_response(sensitivity, t)

                ax.plot(t_out, u_out, color=colors[idx % len(colors)],
                        linewidth=1.2, label=method)
            except Exception:
                pass

        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Control Signal u(t)')
        ax.set_title('Controller Output (Control Effort)')
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, T_SIM])

        plt.tight_layout()
        save_fig(fig, f'03_{subsystem_name.lower()}_closed_loop.png')

        all_metrics[subsystem_name] = sub_metrics

        # Print metrics table for this subsystem
        print_metrics_table(sub_metrics)

    return all_metrics


# =============================================================================
# SECTION 6: Comparison of Different Controller Coefficients
# =============================================================================

def section_6_comparison(tuning_results, all_metrics):
    """
    Compare system dynamics with different controller coefficients.
    Show the effect of P, I, D components.
    """
    print("\n" + "=" * 70)
    print("SECTION 6: COMPARISON OF DIFFERENT CONTROLLER COEFFICIENTS")
    print("=" * 70)

    t = np.linspace(0, T_SIM, N_POINTS)

    # --- 6.1: Effect of Kp variation ---
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Effect of Individual PID Parameters on Combined System Response',
                 fontsize=14, fontweight='bold')

    plant = get_combined_plant(with_delay=True)

    # Get baseline from SIMC
    Kp_base, Ki_base, Kd_base = tune_simc('combined', verbose=False)

    # Effect of Kp
    ax = axes[0]
    kp_values = [Kp_base * 0.3, Kp_base * 0.6, Kp_base, Kp_base * 1.5, Kp_base * 2.5]
    for Kp_val in kp_values:
        try:
            T_cl = get_closed_loop(plant, Kp_val, Ki_base, Kd_base)
            t_out, y_out = ctrl.step_response(T_cl, t)
            if np.any(np.abs(y_out) > 100):
                continue
            ax.plot(t_out, y_out * SETPOINT, linewidth=1.5,
                    label=f'Kp={Kp_val:.1f}')
        except Exception:
            pass

    ax.axhline(y=SETPOINT, color='k', linestyle='--', alpha=0.5)
    ax.fill_between(t, SETPOINT * 0.98, SETPOINT * 1.02, alpha=0.1, color='green')
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Temperature [°C]')
    ax.set_title(f'Effect of Kp (Ki={Ki_base:.2f}, Kd={Kd_base:.4f})')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, T_SIM])

    # Effect of Ki
    ax = axes[1]
    ki_values = [Ki_base * 0.2, Ki_base * 0.5, Ki_base, Ki_base * 2.0, Ki_base * 4.0]
    for Ki_val in ki_values:
        try:
            T_cl = get_closed_loop(plant, Kp_base, Ki_val, Kd_base)
            t_out, y_out = ctrl.step_response(T_cl, t)
            if np.any(np.abs(y_out) > 100):
                continue
            ax.plot(t_out, y_out * SETPOINT, linewidth=1.5,
                    label=f'Ki={Ki_val:.2f}')
        except Exception:
            pass

    ax.axhline(y=SETPOINT, color='k', linestyle='--', alpha=0.5)
    ax.fill_between(t, SETPOINT * 0.98, SETPOINT * 1.02, alpha=0.1, color='green')
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Temperature [°C]')
    ax.set_title(f'Effect of Ki (Kp={Kp_base:.2f}, Kd={Kd_base:.4f})')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, T_SIM])

    # Effect of Kd
    ax = axes[2]
    kd_values = [0, Kd_base * 0.3, Kd_base, Kd_base * 1.5, Kd_base * 2.5]
    for Kd_val in kd_values:
        try:
            T_cl = get_closed_loop(plant, Kp_base, Ki_base, Kd_val)
            t_out, y_out = ctrl.step_response(T_cl, t)
            # Skip unstable responses
            if np.any(np.abs(y_out) > 100):
                continue
            ax.plot(t_out, y_out * SETPOINT, linewidth=1.5,
                    label=f'Kd={Kd_val:.4f}')
        except Exception:
            pass

    ax.axhline(y=SETPOINT, color='k', linestyle='--', alpha=0.5)
    ax.fill_between(t, SETPOINT * 0.98, SETPOINT * 1.02, alpha=0.1, color='green')
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Temperature [°C]')
    ax.set_title(f'Effect of Kd (Kp={Kp_base:.2f}, Ki={Ki_base:.2f})')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, T_SIM])

    plt.tight_layout()
    save_fig(fig, '04_pid_parameter_effects.png')

    # --- 6.2: All subsystems with best controllers on one plot ---
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    ax.set_title('Closed-Loop Response: HTC vs LTC vs Combined System\n'
                 '(Each with its best PID controller)',
                 fontsize=14, fontweight='bold')

    for subsystem_name, get_plant, color, ls in [
        ('HTC', get_htc_plant, 'blue', '-'),
        ('LTC', get_ltc_plant, 'red', '-'),
        ('Combined', get_combined_plant, 'black', '-'),
    ]:
        plant_tf = get_plant(with_delay=True)
        sub_key = subsystem_name.lower()

        # Use SIMC for comparison
        Kp, Ki, Kd = tune_simc(sub_key, verbose=False)
        T_cl = get_closed_loop(plant_tf, Kp, Ki, Kd)
        t_out, y_out = ctrl.step_response(T_cl, t)

        ax.plot(t_out, y_out * SETPOINT, color=color, linestyle=ls,
                linewidth=2, label=f'{subsystem_name} (SIMC)')

        # Also show ZN
        Kp, Ki, Kd = tune_ziegler_nichols_step(sub_key, verbose=False)
        T_cl = get_closed_loop(plant_tf, Kp, Ki, Kd)
        t_out, y_out = ctrl.step_response(T_cl, t)

        ax.plot(t_out, y_out * SETPOINT, color=color, linestyle='--',
                linewidth=1.5, label=f'{subsystem_name} (ZN)')

    ax.axhline(y=SETPOINT, color='gray', linestyle=':', alpha=0.5, label='Setpoint = 80°C')
    ax.fill_between(t, SETPOINT * 0.98, SETPOINT * 1.02, alpha=0.08, color='green',
                    label='±2% band')
    ax.set_xlabel('Time [s]', fontsize=12)
    ax.set_ylabel('Temperature [°C]', fontsize=12)
    ax.legend(fontsize=9, loc='lower right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, T_SIM])
    ax.set_ylim([0, SETPOINT * 1.6])

    plt.tight_layout()
    save_fig(fig, '05_all_subsystems_comparison.png')

    # --- 6.3: P-only, PI, PID comparison ---
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    ax.set_title('Controller Type Comparison: P vs PI vs PID\n'
                 '(Combined System)',
                 fontsize=14, fontweight='bold')

    plant = get_combined_plant(with_delay=True)
    Kp, Ki, Kd = tune_simc('combined', verbose=False)

    # P-only
    T_cl_p = get_closed_loop(plant, Kp, 0, 0)
    t_out, y_p = ctrl.step_response(T_cl_p, t)
    ax.plot(t_out, y_p * SETPOINT, 'b-', linewidth=2, label=f'P only (Kp={Kp:.2f})')

    # PI
    T_cl_pi = get_closed_loop(plant, Kp, Ki, 0)
    t_out, y_pi = ctrl.step_response(T_cl_pi, t)
    ax.plot(t_out, y_pi * SETPOINT, 'r-', linewidth=2,
            label=f'PI (Kp={Kp:.2f}, Ki={Ki:.2f})')

    # PID
    T_cl_pid = get_closed_loop(plant, Kp, Ki, Kd)
    t_out, y_pid = ctrl.step_response(T_cl_pid, t)
    ax.plot(t_out, y_pid * SETPOINT, 'g-', linewidth=2,
            label=f'PID (Kp={Kp:.2f}, Ki={Ki:.2f}, Kd={Kd:.4f})')

    ax.axhline(y=SETPOINT, color='k', linestyle='--', alpha=0.5, label='Setpoint = 80°C')
    ax.fill_between(t, SETPOINT * 0.98, SETPOINT * 1.02, alpha=0.1, color='green')
    ax.set_xlabel('Time [s]', fontsize=12)
    ax.set_ylabel('Temperature [°C]', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, T_SIM])

    plt.tight_layout()
    save_fig(fig, '06_p_pi_pid_comparison.png')

    # Print P, PI, PID metrics
    print("\nP vs PI vs PID comparison (Combined System):")
    controller_metrics = {}
    for label, y_data in [('P only', y_p), ('PI', y_pi), ('PID', y_pid)]:
        m = calculate_metrics(t_out, y_data, setpoint=1.0)
        controller_metrics[label] = m
    print_metrics_table(controller_metrics)


# =============================================================================
# SECTION 7: Find Best Solution
# =============================================================================

def section_7_best_solution(tuning_results, all_metrics):
    """
    Identify the best PID tuning method for each subsystem.
    """
    print("\n" + "=" * 70)
    print("SECTION 7: BEST SOLUTION IDENTIFICATION")
    print("=" * 70)

    for subsystem_name in ['HTC', 'LTC', 'Combined']:
        sub_metrics = all_metrics.get(subsystem_name, {})
        if not sub_metrics:
            continue

        print(f"\n--- {subsystem_name} Subsystem ---")

        # Find best by different criteria
        best_itae = min(sub_metrics, key=lambda m: sub_metrics[m]['itae'])
        best_overshoot = min(sub_metrics, key=lambda m: sub_metrics[m]['overshoot'])
        best_settling = min(sub_metrics, key=lambda m: sub_metrics[m]['settling_time'])
        best_rise = min(sub_metrics, key=lambda m: sub_metrics[m]['rise_time'])

        print(f"  Best by ITAE:          {best_itae} (ITAE = {sub_metrics[best_itae]['itae']:.4f})")
        print(f"  Best by Overshoot:     {best_overshoot} ({sub_metrics[best_overshoot]['overshoot']:.2f}%)")
        print(f"  Best by Settling time: {best_settling} ({sub_metrics[best_settling]['settling_time']:.4f}s)")
        print(f"  Best by Rise time:     {best_rise} ({sub_metrics[best_rise]['rise_time']:.4f}s)")

        # Overall best (weighted score)
        # Normalize each metric and compute weighted sum
        if len(sub_metrics) > 1:
            scores = {}
            metrics_keys = ['itae', 'overshoot', 'settling_time', 'rise_time']
            weights = [0.4, 0.3, 0.2, 0.1]  # ITAE most important

            for method in sub_metrics:
                score = 0
                for mk, w in zip(metrics_keys, weights):
                    vals = [sub_metrics[m][mk] for m in sub_metrics]
                    min_val, max_val = min(vals), max(vals)
                    if max_val > min_val:
                        normalized = (sub_metrics[method][mk] - min_val) / (max_val - min_val)
                    else:
                        normalized = 0
                    score += w * normalized
                scores[method] = score

            overall_best = min(scores, key=scores.get)
            print(f"\n  >>> OVERALL BEST: {overall_best} <<<")
            best_params = tuning_results[subsystem_name][overall_best]
            print(f"      Kp = {best_params['Kp']:.4f}")
            print(f"      Ki = {best_params['Ki']:.4f}")
            print(f"      Kd = {best_params['Kd']:.6f}")

    # Generate best solutions comparison plot
    t = np.linspace(0, T_SIM, N_POINTS)
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    ax.set_title('Best PID Controllers for Each Subsystem\n'
                 '(Selected by ITAE optimization)',
                 fontsize=14, fontweight='bold')

    for subsystem_name, get_plant, color in [
        ('HTC', get_htc_plant, 'blue'),
        ('LTC', get_ltc_plant, 'red'),
        ('Combined', get_combined_plant, 'black'),
    ]:
        sub_metrics = all_metrics.get(subsystem_name, {})
        if not sub_metrics:
            continue

        best_method = min(sub_metrics, key=lambda m: sub_metrics[m]['itae'])
        best_params = tuning_results[subsystem_name][best_method]

        plant = get_plant(with_delay=True)
        T_cl = get_closed_loop(plant, best_params['Kp'], best_params['Ki'],
                               best_params['Kd'])
        t_out, y_out = ctrl.step_response(T_cl, t)

        ax.plot(t_out, y_out * SETPOINT, color=color, linewidth=2.5,
                label=f'{subsystem_name}: {best_method}\n'
                      f'  Kp={best_params["Kp"]:.2f}, '
                      f'Ki={best_params["Ki"]:.2f}, '
                      f'Kd={best_params["Kd"]:.4f}')

    ax.axhline(y=SETPOINT, color='gray', linestyle='--', alpha=0.5, label='Setpoint = 80°C')
    ax.fill_between(t, SETPOINT * 0.98, SETPOINT * 1.02, alpha=0.08, color='green',
                    label='±2% band')
    ax.set_xlabel('Time [s]', fontsize=12)
    ax.set_ylabel('Temperature [°C]', fontsize=12)
    ax.legend(fontsize=9, loc='lower right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, T_SIM])
    ax.set_ylim([0, SETPOINT * 1.5])

    plt.tight_layout()
    save_fig(fig, '07_best_solutions.png')


# =============================================================================
# SECTION 8: Conclusion
# =============================================================================

def section_8_conclusion(tuning_results, all_metrics):
    """
    Print conclusion summarizing the results.
    """
    print("\n" + "=" * 70)
    print("SECTION 8: CONCLUSION")
    print("=" * 70)

    print("""
This study implemented and compared PID controllers for a marine diesel
engine two-circuit cooling system consisting of:
  - HTC (High Temperature Circuit): Cylinder liner + Engine jacket cooler
  - LTC (Low Temperature Circuit):  Charge air cooler + Lubricating oil cooler

Key findings:

1. SYSTEM MODEL: The two-circuit cooling system was modeled as parallel
   first-order transfer functions with transport delays, based on the
   reference paper's Simulink model. The combined plant has a steady-state
   gain of 0.315 and a time constant of 1.0s.

2. PID TUNING METHODS: Five different tuning methods were compared:
   - SIMC (Skogestad Internal Model Control) — analytical autotuning
   - Ziegler-Nichols Step Response — classical empirical method
   - Ziegler-Nichols Ultimate Gain — frequency-based method
   - Cohen-Coon — improved empirical method
   - ITAE Optimization — numerical optimization

3. CONTROLLER PERFORMANCE:""")

    for subsystem_name in ['HTC', 'LTC', 'Combined']:
        sub_metrics = all_metrics.get(subsystem_name, {})
        if not sub_metrics:
            continue

        best_method = min(sub_metrics, key=lambda m: sub_metrics[m]['itae'])
        best_m = sub_metrics[best_method]
        best_p = tuning_results[subsystem_name][best_method]

        print(f"\n   {subsystem_name} Subsystem — Best: {best_method}")
        print(f"     Kp={best_p['Kp']:.4f}, Ki={best_p['Ki']:.4f}, Kd={best_p['Kd']:.6f}")
        print(f"     Rise time: {best_m['rise_time']:.4f}s, "
              f"Overshoot: {best_m['overshoot']:.2f}%, "
              f"Settling: {best_m['settling_time']:.4f}s")

    print("""
4. PID COMPONENT ANALYSIS:
   - P component provides fast response but cannot eliminate SSE
   - I component eliminates steady-state error (essential for temperature control)
   - D component reduces overshoot and improves settling time

5. RECOMMENDATION: For marine diesel engine cooling systems, the ITAE-optimized
   PID controller provides the best balance between response speed, overshoot
   limitation, and steady-state accuracy. The SIMC method provides a good
   analytical starting point that can be further refined.

References:
  [1] "Simulation Modelling of Marine Diesel Engine Cooling System" (2021)
      https://www.researchgate.net/publication/351042446
  [2] Skogestad, S. (2003). "Simple analytic rules for model reduction
      and PID controller tuning." J. Process Control, 13(4), 291-309.
  [3] Ziegler, J.G. & Nichols, N.B. (1942). "Optimum settings for
      automatic controllers." Trans. ASME, 64, 759-768.
  [4] Cohen, G.H. & Coon, G.A. (1953). "Theoretical consideration of
      retarded control." Trans. ASME, 75, 827-834.
""")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Run the complete PID controller analysis."""
    print("=" * 70)
    print("  MARINE DIESEL ENGINE COOLING SYSTEM — PID CONTROLLER ANALYSIS")
    print("  Two-Circuit System: HTC + LTC")
    print("=" * 70)

    # Section 1: Control law description
    section_1_control_law()

    # Section 2: System parameters
    section_2_parameters()

    # Section 3: Open-loop analysis
    section_3_open_loop()

    # Section 4: PID tuning (two methods + extras)
    tuning_results = section_4_pid_tuning()

    # Section 5: Closed-loop simulation and results
    all_metrics = section_5_simulation(tuning_results)

    # Section 6: Comparison of different coefficients
    section_6_comparison(tuning_results, all_metrics)

    # Section 7: Best solution
    section_7_best_solution(tuning_results, all_metrics)

    # Section 8: Conclusion
    section_8_conclusion(tuning_results, all_metrics)

    print("\n" + "=" * 70)
    print("  ALL PLOTS SAVED TO: " + PLOT_DIR)
    print("=" * 70)
    print("\nGenerated files:")
    for f in sorted(os.listdir(PLOT_DIR)):
        filepath = os.path.join(PLOT_DIR, f)
        size_kb = os.path.getsize(filepath) / 1024
        print(f"  {f} ({size_kb:.1f} KB)")

    print("\n  Analysis complete!")


if __name__ == "__main__":
    main()
