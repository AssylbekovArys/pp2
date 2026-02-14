"""
Performance Metrics for Step Response Analysis
================================================

Calculates:
  - Rise time (10% → 90%)
  - Overshoot (%)
  - Settling time (2% band)
  - Steady-state error
  - ITAE (Integral Time Absolute Error)
  - ISE (Integral Squared Error)
"""

import numpy as np


def calculate_metrics(t, y, setpoint=1.0, settling_band=0.02):
    """
    Calculate step response performance metrics.

    Parameters
    ----------
    t : array-like
        Time vector
    y : array-like
        System output vector
    setpoint : float
        Desired setpoint value (default: 1.0 for unit step)
    settling_band : float
        Settling band percentage (default: 0.02 = 2%)

    Returns
    -------
    dict : Dictionary with all performance metrics
    """
    t = np.asarray(t)
    y = np.asarray(y)

    # Final value (steady-state)
    y_final = y[-1]
    y_ss = setpoint  # desired steady-state

    # Steady-state error
    sse = abs(y_ss - y_final)
    sse_percent = (sse / y_ss) * 100 if y_ss != 0 else float('inf')

    # Rise time (10% to 90% of setpoint)
    y_10 = 0.1 * y_ss
    y_90 = 0.9 * y_ss

    t_10 = None
    t_90 = None
    for i in range(len(y) - 1):
        if t_10 is None and y[i] <= y_10 and y[i + 1] >= y_10:
            # Linear interpolation
            t_10 = t[i] + (t[i + 1] - t[i]) * (y_10 - y[i]) / (y[i + 1] - y[i])
        if t_90 is None and y[i] <= y_90 and y[i + 1] >= y_90:
            t_90 = t[i] + (t[i + 1] - t[i]) * (y_90 - y[i]) / (y[i + 1] - y[i])

    rise_time = (t_90 - t_10) if (t_10 is not None and t_90 is not None) else float('inf')

    # Overshoot
    y_max = np.max(y)
    if y_ss != 0:
        overshoot = max(0, (y_max - y_ss) / y_ss * 100)
    else:
        overshoot = 0.0

    # Time to peak
    t_peak = t[np.argmax(y)]

    # Settling time (time to stay within settling_band of setpoint)
    settling_time = float('inf')
    band_upper = y_ss * (1 + settling_band)
    band_lower = y_ss * (1 - settling_band)

    # Find last time the signal exits the band
    for i in range(len(y) - 1, -1, -1):
        if y[i] > band_upper or y[i] < band_lower:
            if i < len(t) - 1:
                settling_time = t[i + 1]
            else:
                settling_time = t[i]
            break
    else:
        settling_time = 0.0  # Always within band

    # ITAE (Integral Time Absolute Error)
    error = y_ss - y
    itae = np.trapz(t * np.abs(error), t)

    # ISE (Integral Squared Error)
    ise = np.trapz(error ** 2, t)

    # IAE (Integral Absolute Error)
    iae = np.trapz(np.abs(error), t)

    return {
        'rise_time': rise_time,
        'overshoot': overshoot,
        'peak_time': t_peak,
        'settling_time': settling_time,
        'sse': sse,
        'sse_percent': sse_percent,
        'itae': itae,
        'ise': ise,
        'iae': iae,
        'y_final': y_final,
        'y_max': y_max,
    }


def print_metrics(metrics, label=''):
    """Pretty-print the performance metrics."""
    print(f"\n--- Performance Metrics: {label} ---")
    print(f"  Rise time (10-90%):  {metrics['rise_time']:.4f} s")
    print(f"  Overshoot:           {metrics['overshoot']:.2f} %")
    print(f"  Peak time:           {metrics['peak_time']:.4f} s")
    print(f"  Settling time (2%):  {metrics['settling_time']:.4f} s")
    print(f"  Steady-state error:  {metrics['sse']:.6f} ({metrics['sse_percent']:.4f}%)")
    print(f"  ITAE:                {metrics['itae']:.6f}")
    print(f"  ISE:                 {metrics['ise']:.6f}")
    print(f"  IAE:                 {metrics['iae']:.6f}")


def metrics_to_table_row(metrics, label=''):
    """Return metrics as a formatted table row string."""
    return (f"{label:<25s} "
            f"{metrics['rise_time']:>10.4f} "
            f"{metrics['overshoot']:>10.2f} "
            f"{metrics['settling_time']:>10.4f} "
            f"{metrics['sse']:>12.6f} "
            f"{metrics['itae']:>10.4f}")


def print_metrics_table(all_metrics):
    """
    Print a comparison table of metrics for multiple controllers.

    Parameters
    ----------
    all_metrics : dict
        {method_name: metrics_dict}
    """
    header = (f"{'Method':<25s} "
              f"{'Rise Time':>10s} "
              f"{'Overshoot%':>10s} "
              f"{'Settl.Time':>10s} "
              f"{'SSE':>12s} "
              f"{'ITAE':>10s}")

    print("\n" + "=" * 82)
    print("PERFORMANCE COMPARISON TABLE")
    print("=" * 82)
    print(header)
    print("-" * 82)
    for method, metrics in all_metrics.items():
        print(metrics_to_table_row(metrics, method))
    print("=" * 82)
