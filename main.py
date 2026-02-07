import numpy as np
import matplotlib.pyplot as plt

class GBMMonteCarlo:
    def __init__(self, S0, mu, sigma, T, steps, n_sims):
        self.S0 = S0
        self.mu = mu
        self.sigma = sigma
        self.T = T
        self.steps = steps
        self.n_sims = n_sims
        self.dt = T / steps

    def simulate_paths(self):
        Z = np.random.standard_normal((self.steps, self.n_sims))
        drift = (self.mu - 0.5 * self.sigma**2) * self.dt
        diffusion = self.sigma * np.sqrt(self.dt) * Z
        daily_returns = np.exp(drift + diffusion)
        
        paths = np.zeros((self.steps + 1, self.n_sims))
        paths[0] = self.S0
        paths[1:] = self.S0 * np.cumprod(daily_returns, axis=0)
        return paths

    def run_analytics_suite(self, strike):
        paths = self.simulate_paths()
        ST = paths[-1]
        payoffs = np.maximum(ST - strike, 0)
        call_price = np.exp(-self.mu * self.T) * np.mean(payoffs)
        losses = self.S0 - ST
        var_95 = np.percentile(losses, 95)
        cvar_95 = losses[losses >= var_95].mean()

        plt.rcParams.update({'font.size': 12, 'font.family': 'sans-serif'})

        # 1. Price Paths
        plt.figure(figsize=(10, 6))
        plt.plot(paths[:, :100], alpha=0.5, lw=0.8)
        plt.title(f"GBM Paths Simulation (Price: {call_price:.2f})")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.savefig("01_price_paths.png", dpi=300)
        plt.close()

        # 2. Loss Distribution
        plt.figure(figsize=(10, 6))
        plt.hist(losses, bins=60, color='darkgrey', edgecolor='white', density=True)
        plt.axvline(var_95, color='black', linestyle='--', label=f'VaR 95%: {var_95:.2f}')
        plt.axvline(cvar_95, color='red', linestyle='-', label=f'CVaR 95%: {cvar_95:.2f}')
        plt.title("Terminal Loss Distribution (VaR & CVaR)")
        plt.legend()
        plt.savefig("02_loss_distribution.png", dpi=300)
        plt.close()

        # 3. Convergence
        plt.figure(figsize=(10, 6))
        running_mean = np.cumsum(payoffs) / np.arange(1, self.n_sims + 1)
        running_price = np.exp(-self.mu * self.T) * running_mean
        plt.plot(running_price, color='blue', lw=1.5)
        plt.axhline(call_price, color='red', linestyle=':', alpha=0.7)
        plt.title("Monte Carlo Price Convergence")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.savefig("03_convergence.png", dpi=300)
        plt.close()

        # 4. Drawdown
        plt.figure(figsize=(10, 6))
        path = paths[:, 0]
        peak = np.maximum.accumulate(path)
        dd = (path - peak) / peak
        plt.fill_between(range(self.steps + 1), dd, 0, color='red', alpha=0.2)
        plt.plot(dd, color='red', lw=1)
        plt.title(f"Max Drawdown Profile: {np.min(dd):.2%}")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.savefig("04_max_drawdown.png", dpi=300)
        plt.close()

if __name__ == "__main__":
    model = GBMMonteCarlo(100, 0.05, 0.2, 1.0, 252, 100000)
    model.run_analytics_suite(strike=105)
