import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# np.random.seed(40)
n = 40

beta_0 = 1
beta_1 = 2

x = np.random.normal(loc=0, scale=1, size=n)
eps = np.random.normal(loc=0, scale=1, size=n)

y = beta_0 + beta_1 * x + eps

x = x.reshape((n, 1))
y = y.reshape((n, 1))

# Exercise 1: Linear regression with sklearn
regressor = LinearRegression()
regressor.fit(x, y)

print(regressor.intercept_.item(), regressor.coef_.item())

# Exercise 2: compute beta_0 and beta_1 without sklearn and without gradient descent
x = np.hstack([np.ones((x.shape[0], 1)), x])
sum_x_squared = 0
sum_x_y = 0
for i in range(x.shape[0]):
    x_ = x[i].reshape(-1, 1)
    sum_x_y += y[i] * x_
    sum_x_squared += x_ @ x_.T
beta = np.linalg.solve(sum_x_squared, sum_x_y)
print(beta)
