Comparing maintenance policies on cost
=========================================

This example compares :doc:`../user_guides/background/maintenance_policies/run_to_failure`
against :doc:`../user_guides/background/maintenance_policies/preventive_age_replacement` for
a fleet of circuit breakers (see :doc:`../user_guides/datasets`), and looks at how the
comparison changes with the cost structure.

>>> from relife.datasets import load_circuit_breaker
>>> from relife.lifetime_models import Weibull
>>> dataset = load_circuit_breaker()
>>> weibull = Weibull().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])

Baseline scenario: preventive replacement is much cheaper than failure
--------------------------------------------------------------------------

With a failure costing :math:`c_f = 1500` and a preventive replacement costing
:math:`c_p = 400`:

>>> from relife.policies import RunToFailurePolicy, AgeReplacementPolicy
>>> rtf = RunToFailurePolicy(weibull)
>>> round(float(rtf.asymptotic_expected_equivalent_annual_cost(cf=1500.)), 2)
20.47

>>> policy = AgeReplacementPolicy(weibull)
>>> ar_star = policy.compute_optimal_ar(cf=1500., cp=400.)
>>> round(float(ar_star), 2)
47.44
>>> round(float(policy.asymptotic_expected_equivalent_annual_cost(ar=ar_star, cf=1500., cp=400.)), 2)
11.69

Replacing preventively at age 47.4 costs 11.69 per unit of time against 20.47 for
run-to-failure — a clear win for preventive replacement here.

Sensitivity: what if preventive replacement isn't that much cheaper?
-------------------------------------------------------------------------

The size of that gap depends entirely on how much cheaper :math:`c_p` is than :math:`c_f`.
Raising the preventive cost from 400 to 1200 (still below the 1500 failure cost, but not by
much):

>>> policy_expensive = AgeReplacementPolicy(weibull)
>>> ar_star_expensive = policy_expensive.compute_optimal_ar(cf=1500., cp=1200.)
>>> round(float(ar_star_expensive), 2)
93.53
>>> round(float(policy_expensive.asymptotic_expected_equivalent_annual_cost(ar=ar_star_expensive, cf=1500., cp=1200.)), 2)
20.29

The optimal replacement age shifts much later (93.5 instead of 47.4), and the resulting cost
(20.29) is almost identical to run-to-failure's 20.47 — when preventive maintenance is
nearly as expensive as a failure, there's very little to gain from doing it early, and the
policy's own optimum reflects that automatically.

.. plot::
    :context: close-figs

    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> from relife.datasets import load_circuit_breaker
    >>> from relife.lifetime_models import Weibull
    >>> from relife.policies import RunToFailurePolicy, AgeReplacementPolicy
    >>> dataset = load_circuit_breaker()
    >>> weibull = Weibull().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])
    >>> rtf = RunToFailurePolicy(weibull)
    >>> ar_range = np.arange(10., 120., 5.)
    >>> for cp, label in ((400., "$c_p=400$"), (1200., "$c_p=1200$")):
    ...     policy = AgeReplacementPolicy(weibull)
    ...     costs = [
    ...         float(policy.asymptotic_expected_equivalent_annual_cost(ar=ar, cf=1500., cp=cp))
    ...         for ar in ar_range
    ...     ]
    ...     _ = plt.plot(ar_range, costs, marker="o", label=label)
    >>> _ = plt.axhline(float(rtf.asymptotic_expected_equivalent_annual_cost(cf=1500.)), color="grey", linestyle="--", label="run-to-failure")
    >>> _ = plt.xlabel("replacement age $a_r$")
    >>> _ = plt.ylabel("expected annual cost")
    >>> _ = plt.legend()
    >>> plt.show()

The cheaper-preventive-cost curve has a sharper, earlier minimum well below the
run-to-failure line; the more-expensive-preventive-cost curve is flatter and only barely
dips under it — the cost structure, not just the lifetime model, decides whether preventive
replacement is worth it.

The annual-cost curves above summarize the long-run rate, but a fleet manager also cares
about the cumulative cost trajectory over time:

.. figure:: /_static/figures/cost_comparison_paths.png
    :alt: Cumulative replacement cost over time for a run-to-failure policy versus the optimal age-replacement policy, for two lifetime models, each showing the optimal policy tracking noticeably below run-to-failure.
    :width: 100%

    Simulated cumulative cost trajectories, optimal age-replacement policy versus
    run-to-failure, for two lifetime models. The gap between the solid (optimal policy) and dashed
    (run-to-failure) lines widens steadily — exactly the kind of forecast that determines the
    budget and stock of spare parts to plan for over a given horizon.
