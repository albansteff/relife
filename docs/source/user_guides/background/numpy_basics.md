# About NumPy

ReLife is built using [NumPy](https://numpy.org/), a fundamental Python library for numerical computing.
While you don't need to be a NumPy expert, understanding its basics will help since ReLife often requires data input of `np.ndarray` type.

There are 3 standard representations of data in ReLife:

- If you want to pass a scalar value, use `float` built-in type (`np.float64` is accepted but not required).
- If you want to pass a vector of \(\mathbb{R}^n\), e.g. \(n\) values for one asset, use a `np.ndarray` of shape `(n,)`.
- If you want to pass a matrix of \(\mathbb{R}^{m\times n}\), i.e. \(n\) values for \(m\) assets, use a `np.ndarray` of shape `(m, n)`

**Broadcasting examples**

```python
>>> from relife.lifetime_models import Weibull
>>> weibull = Weibull(3.47, 0.012)
>>> round(weibull.sf(40.), 6)
np.float64(0.924663)

```

The output has the same number of dimension than the input.
To compute \(P(T > 40)\), but also \(P(T > 50)\) and \(P(T > 60)\), we can benefit from [broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html) and compute three survival function evaluations in parallel.

```python
>>> import numpy as np
>>> weibull.sf(np.array([40., 50., 60.])) # 1d array of shape (3,)
array([0.92466275, 0.84375201, 0.72625935])

```

This logic is extended **until two dimensions**. For instance, it is sometimes usefull to pass several values per assets.

```python
>>> weibull.sf(np.array([[40., 50., 60.], [42., 55., 68.]])) # 2d array of shape (2, 3)
array([[0.92466275, 0.84375201, 0.72625935],
       [0.91139796, 0.78939177, 0.61029328]])

```

Each row encodes a vector of values for each asset.
