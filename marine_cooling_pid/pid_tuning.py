"""
PID Tuning Methods for Marine Diesel Engine Cooling System
===========================================================

Implements two PID tuning methods as required by the assignment:
  Method 1: SIMC (Skogestad Internal Model Control) — autotuning / analytical
  Method 2: Ziegler-Nichols — classical empirical method

Also includes:
  - Cohen-Coon method
  - Optimization-based tuning (ITAE minimization)
"""

import numpy as np
from scipy.optimize import minimize
from scipy.signal import lti, step
import control as ctrl

from system_model import get_fopdt_params, get_pid_tf


# =============================================================================
# Method 1: SIMC (Skogestad Internal Model Control) — Autotuning
# =============================================================================

def tune_simc(subsystem='combined', tau_c=None, verbose=True):
    """
    SIMC (Skogestad Internal Model Control) PID tuning.

    For FOPDT model: G(s) = K * e^(-theta*s) / (tau*s + 1)

    PI controller:
        Kp = tau / (K * (tau_c + theta))
        Ti = min(tau, 4*(tau_c + theta))

    PID controller:
        Kp = tau / (K * (tau_c + theta))
        Ti = min(tau, 4*(tau_c + theta))
        Td = 0.5 * theta   (only if theta > 0)

    tau_c: desired closed-loop time constant (default: max(theta, 0.1*tau))

    Reference: Skogestad, S. (2003). "Simple analytic rules for model reduction
    and PID controller tuning." J. Process Control, 13(4), 291-309.
    """
    K, tau, theta = get_fopdt_params(subsystem)

    # Default closed-loop time constant
    if tau_c is None:
        tau_c = max(theta, 0.1 * tau)

    # PID parameters
    Kp = tau / (K * (tau_c + theta))
    Ti = min(tau, 4 * (tau_c + theta))
    Ki = Kp / Ti if Ti > 0 else 0
    Td = 0.5 * theta if theta > 0 else 0
    Kd = Kp * Td

    if verbose:
        print(f"\n{'='*60}")
        print(f"SIMC (Autotuning) — {subsystem.upper()} subsystem")
        print(f"{'='*60}")
        print(f"FOPDT parameters: K={K:.4f}, tau={tau:.2f}s, theta={theta:.4f}s")
        print(f"Desired closed-loop time constant: tau_c={tau_c:.4f}s")
        print(f"PID coefficients:")
        print(f"  Kp = {Kp:.4f}")
        print(f"  Ki = {Ki:.4f}  (Ti = {Ti:.4f}s)")
        print(f"  Kd = {Kd:.6f}  (Td = {Td:.4f}s)")
        print(f"{'='*60}")

    return Kp, Ki, Kd


# =============================================================================
# Method 2: Ziegler-Nichols
# =============================================================================

def tune_ziegler_nichols_step(subsystem='combined', verbose=True):
    """
    Ziegler-Nichols Step Response Method for FOPDT systems.

    For FOPDT: G(s) = K * e^(-L*s) / (T*s + 1)

    PID parameters:
        Kp = 1.2 * T / (K * L)
        Ti = 2 * L
        Td = 0.5 * L
        Ki = Kp / Ti
        Kd = Kp * Td

    Note: This method requires a non-zero delay L > 0.
    """
    K, tau, theta = get_fopdt_params(subsystem)

    if theta <= 0:
        # Add minimal delay for the method to work
        theta = 0.05 * tau

    # Ziegler-Nichols PID from step response
    Kp = 1.2 * tau / (K * theta)
    Ti = 2.0 * theta
    Td = 0.5 * theta
    Ki = Kp / Ti if Ti > 0 else 0
    Kd = Kp * Td

    if verbose:
        print(f"\n{'='*60}")
        print(f"Ziegler-Nichols (Step Response) — {subsystem.upper()} subsystem")
        print(f"{'='*60}")
        print(f"FOPDT parameters: K={K:.4f}, T={tau:.2f}s, L={theta:.4f}s")
        print(f"PID coefficients:")
        print(f"  Kp = {Kp:.4f}")
        print(f"  Ki = {Ki:.4f}  (Ti = {Ti:.4f}s)")
        print(f"  Kd = {Kd:.6f}  (Td = {Td:.4f}s)")
        print(f"{'='*60}")

    return Kp, Ki, Kd


def tune_ziegler_nichols_ultimate(plant_tf, verbose=True, label=''):
    """
    Ziegler-Nichols Ultimate Gain Method.

    1. Increase proportional gain Kp until the system oscillates
       with constant amplitude (marginal stability).
    2. Record Ku (ultimate gain) and Tu (ultimate period).
    3. Calculate PID parameters:
        Kp = 0.6 * Ku
        Ti = 0.5 * Tu
        Td = 0.125 * Tu

    Uses frequency response analysis to find the ultimate gain.
    """
    # Find the gain crossover frequency and phase margin
    # At the ultimate frequency, the phase is -180°
    # So we need: angle(G(j*w_u)) = -180°

    # Get frequency response
    omega = np.logspace(-3, 3, 10000)
    mag, phase, freq = ctrl.frequency_response(plant_tf, omega)

    # Find frequency where phase crosses -180 degrees
    phase_deg = np.degrees(phase)

    # Find crossing of -180 degrees
    crossings = []
    for i in range(len(phase_deg) - 1):
        if (phase_deg[i] > -180 and phase_deg[i+1] <= -180) or \
           (phase_deg[i] < -180 and phase_deg[i+1] >= -180):
            # Linear interpolation
            w_cross = freq[i] + (freq[i+1] - freq[i]) * \
                      (-180 - phase_deg[i]) / (phase_deg[i+1] - phase_deg[i])
            crossings.append(w_cross)

    if not crossings:
        if verbose:
            print(f"WARNING: No phase crossover found for {label}.")
            print("  System may not have sufficient phase lag for ZN ultimate method.")
            print("  Falling back to ZN step response method.")
        return None, None, None

    # Use the first crossing (lowest frequency)
    w_u = crossings[0]

    # Ultimate gain: Ku = 1 / |G(j*w_u)|
    mag_at_wu = np.interp(w_u, freq, mag)
    Ku = 1.0 / mag_at_wu

    # Ultimate period
    Tu = 2 * np.pi / w_u

    # Ziegler-Nichols PID from ultimate gain
    Kp = 0.6 * Ku
    Ti = 0.5 * Tu
    Td = 0.125 * Tu
    Ki = Kp / Ti if Ti > 0 else 0
    Kd = Kp * Td

    if verbose:
        print(f"\n{'='*60}")
        print(f"Ziegler-Nichols (Ultimate Gain) — {label}")
        print(f"{'='*60}")
        print(f"Ultimate gain:   Ku = {Ku:.4f}")
        print(f"Ultimate period: Tu = {Tu:.4f}s")
        print(f"PID coefficients:")
        print(f"  Kp = {Kp:.4f}")
        print(f"  Ki = {Ki:.4f}  (Ti = {Ti:.4f}s)")
        print(f"  Kd = {Kd:.6f}  (Td = {Td:.4f}s)")
        print(f"{'='*60}")

    return Kp, Ki, Kd


# =============================================================================
# Cohen-Coon Method (Bonus)
# =============================================================================

def tune_cohen_coon(subsystem='combined', verbose=True):
    """
    Cohen-Coon PID tuning method for FOPDT systems.

    For FOPDT: G(s) = K * e^(-theta*s) / (tau*s + 1)

    PID parameters:
        r = theta / tau  (delay ratio)
        Kp = (1/(K*r)) * (4/3 + r/4)
        Ti = theta * (32 + 6*r) / (13 + 8*r)
        Td = theta * 4 / (11 + 2*r)
    """
    K, tau, theta = get_fopdt_params(subsystem)

    if theta <= 0:
        theta = 0.05 * tau

    r = theta / tau

    Kp = (1.0 / (K * r)) * (4.0 / 3.0 + r / 4.0)
    Ti = theta * (32.0 + 6.0 * r) / (13.0 + 8.0 * r)
    Td = theta * 4.0 / (11.0 + 2.0 * r)
    Ki = Kp / Ti if Ti > 0 else 0
    Kd = Kp * Td

    if verbose:
        print(f"\n{'='*60}")
        print(f"Cohen-Coon — {subsystem.upper()} subsystem")
        print(f"{'='*60}")
        print(f"FOPDT parameters: K={K:.4f}, tau={tau:.2f}s, theta={theta:.4f}s")
        print(f"Delay ratio: r = theta/tau = {r:.4f}")
        print(f"PID coefficients:")
        print(f"  Kp = {Kp:.4f}")
        print(f"  Ki = {Ki:.4f}  (Ti = {Ti:.4f}s)")
        print(f"  Kd = {Kd:.6f}  (Td = {Td:.4f}s)")
        print(f"{'='*60}")

    return Kp, Ki, Kd


# =============================================================================
# Optimization-Based Tuning (ITAE Minimization)
# =============================================================================

def tune_optimization(plant_tf, setpoint=1.0, t_sim=20.0, verbose=True, label=''):
    """
    Optimization-based PID tuning using ITAE criterion minimization.

    ITAE = ∫₀^T t * |e(t)| dt

    Uses scipy.optimize to find optimal Kp, Ki, Kd that minimize ITAE.
    """
    t = np.linspace(0, t_sim, 2000)

    def cost_function(params):
        Kp, Ki, Kd = params
        if Kp < 0 or Ki < 0 or Kd < 0:
            return 1e10
        try:
            C = get_pid_tf(Kp, Ki, Kd)
            T_cl = ctrl.feedback(ctrl.series(C, plant_tf), 1)
            t_out, y = ctrl.step_response(T_cl, t)

            error = setpoint - y
            itae = np.trapz(t_out * np.abs(error), t_out)

            # Penalize excessive overshoot
            overshoot = (np.max(y) - setpoint) / setpoint * 100
            if overshoot > 30:
                itae += overshoot * 10

            # Penalize instability
            if np.any(np.abs(y) > 10 * setpoint):
                return 1e10

            return itae
        except Exception:
            return 1e10

    # Get a reasonable initial guess from SIMC
    from system_model import get_fopdt_params
    try:
        K_plant, tau_plant, theta_plant = get_fopdt_params('combined')
        tau_c_init = max(theta_plant, 0.1 * tau_plant)
        Kp_init = tau_plant / (K_plant * (tau_c_init + theta_plant))
        Ki_init = Kp_init / tau_plant
        Kd_init = Kp_init * 0.5 * theta_plant
        x0 = [Kp_init, Ki_init, max(Kd_init, 0.01)]
    except Exception:
        x0 = [5.0, 3.0, 0.1]

    result = minimize(cost_function, x0, method='Nelder-Mead',
                      options={'maxiter': 3000, 'xatol': 1e-4, 'fatol': 1e-4})

    Kp, Ki, Kd = result.x

    if verbose:
        print(f"\n{'='*60}")
        print(f"Optimization (ITAE) — {label}")
        print(f"{'='*60}")
        print(f"Optimal PID coefficients:")
        print(f"  Kp = {Kp:.4f}")
        print(f"  Ki = {Ki:.4f}")
        print(f"  Kd = {Kd:.6f}")
        print(f"  ITAE = {result.fun:.6f}")
        print(f"{'='*60}")

    return Kp, Ki, Kd


# =============================================================================
# Summary of all tuning methods
# =============================================================================

def get_all_tuning_results(subsystem='combined', plant_tf=None):
    """
    Run all tuning methods and return results as a dictionary.
    """
    results = {}

    # Method 1: SIMC (Autotuning)
    Kp, Ki, Kd = tune_simc(subsystem, verbose=True)
    results['SIMC (Autotuning)'] = {'Kp': Kp, 'Ki': Ki, 'Kd': Kd}

    # Method 2a: Ziegler-Nichols (Step Response)
    Kp, Ki, Kd = tune_ziegler_nichols_step(subsystem, verbose=True)
    results['ZN (Step Response)'] = {'Kp': Kp, 'Ki': Ki, 'Kd': Kd}

    # Method 2b: Ziegler-Nichols (Ultimate Gain) — requires plant TF
    if plant_tf is not None:
        Kp, Ki, Kd = tune_ziegler_nichols_ultimate(
            plant_tf, verbose=True, label=f'{subsystem.upper()} subsystem'
        )
        if Kp is not None:
            results['ZN (Ultimate Gain)'] = {'Kp': Kp, 'Ki': Ki, 'Kd': Kd}

    # Cohen-Coon
    Kp, Ki, Kd = tune_cohen_coon(subsystem, verbose=True)
    results['Cohen-Coon'] = {'Kp': Kp, 'Ki': Ki, 'Kd': Kd}

    # Optimization-based
    if plant_tf is not None:
        Kp, Ki, Kd = tune_optimization(
            plant_tf, verbose=True, label=f'{subsystem.upper()} subsystem'
        )
        results['ITAE Optimization'] = {'Kp': Kp, 'Ki': Ki, 'Kd': Kd}

    return results


if __name__ == "__main__":
    from system_model import get_combined_plant, get_htc_plant, get_ltc_plant

    print("=" * 70)
    print("PID TUNING FOR COMBINED COOLING SYSTEM")
    print("=" * 70)

    plant = get_combined_plant(with_delay=True)
    results = get_all_tuning_results('combined', plant)

    print("\n\nSUMMARY TABLE:")
    print("-" * 60)
    print(f"{'Method':<25s} {'Kp':>10s} {'Ki':>10s} {'Kd':>10s}")
    print("-" * 60)
    for method, params in results.items():
        print(f"{method:<25s} {params['Kp']:10.4f} {params['Ki']:10.4f} {params['Kd']:10.6f}")
    print("-" * 60)
