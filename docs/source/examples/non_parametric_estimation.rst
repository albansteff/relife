Non-parametric survival and hazard estimation
================================================

This example fits Kaplan-Meier and Nelson-Aalen on the circuit breaker dataset (see
:doc:`../user_guides/datasets`). See
:doc:`../user_guides/background/lifetime_modeling/non_parametric_models` for why these two
(and not the plain empirical CDF) are the right choice when most observations are
right-censored, as they are here.

>>> from relife.datasets import load_circuit_breaker
>>> dataset = load_circuit_breaker()
>>> dataset["event"].sum(), len(dataset)
(np.int64(204), 4204)

>>> from relife.lifetime_models import KaplanMeier, NelsonAalen
>>> km = KaplanMeier(dataset["time"], event=dataset["event"], entry=dataset["entry"])
>>> na = NelsonAalen(dataset["time"], event=dataset["event"], entry=dataset["entry"])

Reading off an estimate
--------------------------

``sf()``/``chf()`` return the whole estimated curve (timeline, values, and standard errors)
rather than a function you evaluate at an arbitrary time, so getting an estimate at a
specific time means locating it on the timeline:

>>> import numpy as np
>>> sf = km.sf()
>>> idx = np.searchsorted(sf.timeline, 40., side="right") - 1
>>> sf.timeline[idx]
np.float64(40.0)
>>> round(float(sf.values[idx]), 4), round(float(sf.se[idx]), 4)
(0.9312, 0.0082)

An estimated 93.1% of circuit breakers are still in service at 40 time units (standard
error 0.8%).

Comparing the two estimators
-------------------------------

.. plot::
    :context: close-figs

    >>> import matplotlib.pyplot as plt
    >>> from relife.datasets import load_circuit_breaker
    >>> from relife.lifetime_models import KaplanMeier, NelsonAalen
    >>> dataset = load_circuit_breaker()
    >>> km = KaplanMeier(dataset["time"], event=dataset["event"], entry=dataset["entry"])
    >>> na = NelsonAalen(dataset["time"], event=dataset["event"], entry=dataset["entry"])
    >>> fig, axs = plt.subplots(ncols=2, nrows=1, figsize=(10, 4))
    >>> _ = km.plot("sf", ax=axs[0])
    >>> _ = na.plot("chf", ax=axs[1])
    >>> _ = axs[0].set_title("Kaplan-Meier survival function")
    >>> _ = axs[1].set_title("Nelson-Aalen cumulative hazard")
    >>> plt.show()

Both curves are step functions that only move at observed failure times, a direct
consequence of only 204 of the 4204 circuit breakers ever being observed failing. Once
you've checked that a candidate parametric shape tracks these non-parametric estimates
reasonably well, see :doc:`distributions_fitting` for fitting one.
