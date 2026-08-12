Getting Started
===============

ReLife helps you go from raw failure-time data to a maintenance decision, in three steps:
model an asset's lifetime, turn it into a cost model for a maintenance policy, and compare
policies to pick the cheapest one. This page walks through the whole pipeline in brief,
on one of ReLife's built-in datasets. See the :doc:`user_guides/index` for the concepts and
:doc:`examples/index` for more worked cases.

1. Load some data
------------------

ReLife ships a few example datasets (see :doc:`user_guides/datasets`). Each one is a numpy
structured array with at least a ``time`` (observed lifetime), an ``event`` (was the failure
actually observed, or is the lifetime right-censored) and an ``entry`` (left-truncation) field.

>>> from relife.datasets import load_circuit_breaker
>>> dataset = load_circuit_breaker()
>>> dataset.dtype.names
('time', 'event', 'entry')

2. Fit a lifetime model
------------------------

Pick a parametric lifetime distribution and fit it on the data, accounting for the censoring
and truncation:

>>> from relife.lifetime_models import Weibull
>>> weibull = Weibull().fit(
...     dataset["time"], event=dataset["event"], entry=dataset["entry"]
... )
>>> weibull.get_params()
array([3.7267452 , 0.01232326])

The fitted model exposes the usual reliability functions (``sf``, ``hf``, ``cdf``, ...):

.. plot::
    :context: close-figs

    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> from relife.datasets import load_circuit_breaker
    >>> from relife.lifetime_models import Weibull
    >>> dataset = load_circuit_breaker()
    >>> weibull = Weibull().fit(
    ...     dataset["time"], event=dataset["event"], entry=dataset["entry"]
    ... )
    >>> timeline = np.arange(0, 100)
    >>> _ = weibull.plot("sf", timeline, label="Weibull survival function")
    >>> _ = plt.legend()
    >>> plt.show()

3. Turn the model into a maintenance decision
----------------------------------------------

A fitted lifetime model alone doesn't tell you *when* to replace an asset — for that, wrap it
in a maintenance policy with the relevant costs (see :doc:`user_guides/background/maintenance_policies/index`).
Replacing only on failure (run-to-failure) versus replacing preventively at a fixed age both have
an expected annual cost:

>>> from relife.policies import RunToFailurePolicy, AgeReplacementPolicy
>>> rtf = RunToFailurePolicy(weibull)
>>> rtf.asymptotic_expected_equivalent_annual_cost(cf=1500.)
np.float64(20.47481108112064)

>>> policy = AgeReplacementPolicy(weibull)
>>> ar_star = policy.compute_optimal_ar(cf=1500., cp=400.)
>>> ar_star
np.float64(47.438243830035425)
>>> policy.asymptotic_expected_equivalent_annual_cost(ar=ar_star, cf=1500., cp=400.)
np.float64(11.68744089432104)

Replacing the asset preventively at age ``ar_star`` roughly halves the expected annual cost
compared to only replacing on failure — this is the kind of trade-off ReLife is built to
quantify. :doc:`user_guides/background/maintenance_policies/cost_calculations` walks through
where these numbers come from.

Next steps
----------

- :doc:`user_guides/index` for the concepts (censoring and truncation, lifetime models,
  maintenance policies) behind the calls above.
- :doc:`examples/index` for complete, dataset-driven examples of each modeling approach.
- :doc:`api/index` for the full reference.
