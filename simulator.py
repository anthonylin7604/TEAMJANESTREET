import numpy as np

def simulate_growth_monte_carlo(
    current_wealth,
    monthly_investment,
    years,
    annual_return,
    annual_volatility=0.15,
    n_simulations=1000,
    inflation_rate=0.03,
    seed=None
):
    """
    Monte Carlo wealth simulation using geometric Brownian motion.

    Improvements over simple simulation:
    - Lognormal returns (more realistic market behavior)
    - Inflation-adjusted (real wealth projection)
    - Vectorized simulation for speed
    - Confidence interval outputs

    Parameters
    ----------
    current_wealth : float
        Starting portfolio value
    monthly_investment : float
        Monthly contributions
    years : int
        Investment horizon
    annual_return : float
        Expected annual return (e.g. 0.08 for 8%)
    annual_volatility : float
        Expected annual volatility
    n_simulations : int
        Number of Monte Carlo runs
    inflation_rate : float
        Annual inflation rate
    seed : int or None
        Random seed for reproducibility

    Returns
    -------
    median : np.array
        Median wealth path
    low : np.array
        10th percentile path
    high : np.array
        90th percentile path
    years_axis : np.array
        Time axis in years
    """

    if seed is not None:
        np.random.seed(seed)

    months = years * 12
    dt = 1 / 12

    # Convert to REAL return (inflation adjusted)
    real_return = annual_return - inflation_rate

    mu = real_return
    sigma = annual_volatility

    # Drift and diffusion for GBM
    drift = (mu - 0.5 * sigma**2) * dt
    diffusion = sigma * np.sqrt(dt)

    # Generate random shocks
    shocks = np.random.normal(0, 1, (n_simulations, months))

    # Calculate monthly growth factors
    growth_factors = np.exp(drift + diffusion * shocks)

    # Initialize simulation matrix
    simulations = np.zeros((n_simulations, months + 1))
    simulations[:, 0] = current_wealth

    # Run simulation
    for month in range(1, months + 1):
        simulations[:, month] = (
            simulations[:, month - 1] * growth_factors[:, month - 1]
            + monthly_investment
        )

    # Statistics
    median = np.median(simulations, axis=0)
    low = np.percentile(simulations, 10, axis=0)
    high = np.percentile(simulations, 90, axis=0)

    # Time axis in years
    years_axis = np.arange(months + 1) / 12

    return median, low, high, years_axis