import numpy as np
from sklearn.linear_model import LinearRegression


def generate_data(n, p, true_beta):
    X = np.random.normal(loc=0, scale=1, size=(n, p))
    true_beta = np.reshape(true_beta, (p, 1))

    noise = np.random.normal(loc=0, scale=1, size=(n, 1))
    y = np.dot(X, true_beta) + noise

    return X, y


n = 40
p = 5
true_beta = [-1.0, 0.0, 1.0, 1.5, 2.0]

X, y = generate_data(n, p, true_beta)

# Exercise 3: regression with sklearn
# Your code here
regressor = LinearRegression()
regressor.fit(X, y)
print(regressor.intercept_, regressor.coef_)

# Exercise 4: regression with normal equation
# Your code here
X_ = np.hstack([np.ones((X.shape[0], 1)), X])
normal_beta = np.linalg.inv(X_.T @ X_) @ X_.T @ y
print(normal_beta.reshape(normal_beta.shape[0]))

# Exercise 5: regression with gradient descent
grad_beta = np.random.random((X_.shape[1], 1))
lr = 1e-2
for i in range(10000):
    grad = -X_.T @ (y - X_ @ grad_beta)
    if np.linalg.norm(grad) < 1e-15:
        print(np.linalg.norm(grad))
        break
    grad_beta -= lr * grad
print(grad_beta.reshape(grad_beta.shape[0]))

# Your code here
