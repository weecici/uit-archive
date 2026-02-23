import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

np.random.seed(2025)


def generate_data(n, p, true_beta):
    X = np.random.normal(loc=0, scale=1, size=(n, p))
    true_beta = np.reshape(true_beta, (p, 1))
    noise = np.random.normal(loc=0, scale=1, size=(n, 1))

    y = np.dot(X, true_beta) + noise

    return X, y


def run():
    n = 100
    p = 1
    true_beta = [0.0]
    X, y = generate_data(n, p, true_beta)

    # Your code here to compute p-value
    XtX_inv = np.linalg.inv(X.T @ X)
    beta_hat = XtX_inv @ X.T @ y
    beta_null = np.array([0]).reshape((1, 1))
    # H_0: beta_hat = 0
    z_stat = (beta_hat - beta_null) / np.sqrt(XtX_inv[0, 0])
    p_value = 2 * norm.sf(abs(z_stat))
    return p_value


if __name__ == "__main__":
    p_value = run().item()
    alpha = 0.05
    print(f"p_value: {p_value}")
    if p_value < alpha:
        print("Reject H_0: beta = 0")
    else:
        print("Do not reject H_0: beta = 0")
