Cost calculations
===================

:doc:`run_to_failure` and :doc:`preventive_age_replacement` both expose
``asymptotic_expected_equivalent_annual_cost`` — the long-run expected cost per unit of time
that a :doc:`renewal reward process <reward_framework>` converges to. For a run-to-failure
policy this number doesn't depend on any decision you make; for an age-replacement policy,
it's a function of the replacement age :math:`a_r`, and that's the whole point: it lets you
compare candidate ages, or let ReLife find the best one directly.

>>> from relife.datasets import load_circuit_breaker
>>> from relife.lifetime_models import Weibull
>>> from relife.policies import age_replacement_policy
>>> dataset = load_circuit_breaker()
>>> weibull = Weibull().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])
>>> policy = age_replacement_policy(weibull, {"cf": 1500., "cp": 400.})

Sweeping the replacement age over a range and reading off the cost traces out a curve with a
clear minimum:

.. plot::
    :context: close-figs

    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> from relife.datasets import load_circuit_breaker
    >>> from relife.lifetime_models import Weibull
    >>> from relife.policies import age_replacement_policy
    >>> dataset = load_circuit_breaker()
    >>> weibull = Weibull().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])
    >>> policy = age_replacement_policy(weibull, {"cf": 1500., "cp": 400.})
    >>> ar_range = np.arange(10., 90., 5.)
    >>> costs = [
    ...     float(policy.asymptotic_expected_equivalent_annual_cost(ar=ar)) for ar in ar_range
    ... ]
    >>> ar_star = policy.compute_optimal_ar()
    >>> _ = plt.plot(ar_range, costs, marker="o", label="expected annual cost")
    >>> _ = plt.axvline(float(ar_star), color="grey", linestyle="--", label="optimal $a_r$")
    >>> _ = plt.xlabel("replacement age $a_r$")
    >>> _ = plt.ylabel("expected annual cost")
    >>> _ = plt.legend()
    >>> plt.show()

Replacing too early (small :math:`a_r`) wastes useful life and pays the preventive cost too
often; replacing too late drifts back towards the run-to-failure cost as more failures slip
through before the preventive replacement age is reached. ``compute_optimal_ar`` (see
:doc:`preventive_age_replacement`) locates the minimum of exactly this curve analytically
rather than by grid search.

The same shape shows up regardless of the underlying distribution — only how deep and how
sharp the minimum is changes:

.. figure:: /_static/figures/cost_ratio_optimal_age.png
    :alt: Ratio of the expected annual cost with preventive replacement over the run-to-failure cost, for a Weibull and a Gompertz model, each showing a minimum below 1 with the failure probability at the optimal age annotated.
    :width: 100%

    Expected annual cost of an age-replacement policy, divided by the run-to-failure cost, as
    a function of :math:`a_r`. Both curves dip below 1 (preventive replacement wins) before rising
    back towards it. :math:`F(a_r)` is the probability of failing *before* reaching the
    optimal age — the fraction of assets that will still cost :math:`c_f` even under the
    optimal policy, since not every asset can be caught in time.

The same cost structure also lets you compare policies directly for a given fleet and set of
costs — see :doc:`../../../examples/maintenance_policy_costs` for a complete comparison.
