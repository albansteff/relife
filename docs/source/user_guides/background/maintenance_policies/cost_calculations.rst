Cost calculations
===================

:doc:`run_to_failure` and :doc:`preventive_age_replacement` both expose
``asymptotic_expected_equivalent_annual_cost``, the long-run expected cost per unit of time
that a :doc:`renewal reward process <reward_framework>` converges to. For a run-to-failure
policy this number doesn't depend on any decision you make; for an age-replacement policy,
it's a function of the replacement age ``ar``, and that's the whole point: it lets you
compare candidate ages, or let ReLife find the best one directly.

>>> from relife.datasets import load_circuit_breaker
>>> from relife.lifetime_models import Weibull
>>> from relife.policies import AgeReplacementPolicy
>>> dataset = load_circuit_breaker()
>>> weibull = Weibull().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])
>>> policy = AgeReplacementPolicy(weibull)

Sweeping the replacement age over a range and reading off the cost traces out a curve with a
clear minimum:

.. plot::
    :context: close-figs

    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> from relife.datasets import load_circuit_breaker
    >>> from relife.lifetime_models import Weibull
    >>> from relife.policies import AgeReplacementPolicy
    >>> dataset = load_circuit_breaker()
    >>> weibull = Weibull().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])
    >>> policy = AgeReplacementPolicy(weibull)
    >>> ar_range = np.arange(10., 90., 5.)
    >>> costs = [
    ...     float(policy.asymptotic_expected_equivalent_annual_cost(ar=ar, cf=1500., cp=400.))
    ...     for ar in ar_range
    ... ]
    >>> ar_star = policy.compute_optimal_ar(cf=1500., cp=400.)
    >>> _ = plt.plot(ar_range, costs, marker="o", label="expected annual cost")
    >>> _ = plt.axvline(float(ar_star), color="grey", linestyle="--", label="optimal ar")
    >>> _ = plt.xlabel("replacement age ar")
    >>> _ = plt.ylabel("expected annual cost")
    >>> _ = plt.legend()
    >>> plt.show()

Replacing too early (small ``ar``) wastes useful life and pays the preventive cost too
often; replacing too late drifts back towards the run-to-failure cost as more failures slip
through before the preventive replacement age is reached. ``compute_optimal_ar`` (see
:doc:`preventive_age_replacement`) locates the minimum of exactly this curve analytically
rather than by grid search.

The same shape shows up regardless of the underlying distribution; only how deep and how
sharp the minimum is changes:

.. figure:: /_static/figures/cost_ratio_optimal_age.png
    :alt: Ratio of the expected annual cost with preventive replacement over the run-to-failure cost, for a Weibull and a Gompertz model, each showing a minimum below 1 with the failure probability at the optimal age annotated.
    :width: 100%

    Expected annual cost of an age-replacement policy, divided by the run-to-failure cost, as
    a function of ``ar``. Both curves dip below 1 (preventive replacement wins) before rising
    back towards it. The annotated ``F(ar)`` is the probability of failing *before* reaching
    the optimal age: the fraction of assets that will still cost ``cf`` even under the
    optimal policy, since not every asset can be caught in time.

The same cost structure also lets you compare policies directly for a given fleet and set of
costs; see :doc:`../../../examples/maintenance_policy_costs` for a complete comparison.

What ``asymptotic`` means for a one-cycle policy
---------------------------------------------------

``OneCycleRunToFailurePolicy`` and ``OneCycleAgeReplacementPolicy`` expose exactly the same
four methods, so the two families are drop-in interchangeable — but the quantities they
return answer different questions, and mixing them up is the easy mistake to make here.

For a renewal policy, the ``asymptotic_`` prefix means *as the number of renewals grows*: the
net present value diverges without discounting, and the annual cost converges to a long-run
rate. For a one-cycle policy there is only ever one replacement, so the prefix simply means
*over the whole of that single cycle*, with no truncation at a finite horizon. Its net present
value is therefore finite even undiscounted (it is the expected cost of one replacement), and
its annual cost is the expected cost annualized over the realized cycle duration rather than
a long-run rate.

Two practical consequences: an undiscounted ``asymptotic_expected_net_present_value`` is
readable for a one-cycle policy and meaningless (infinite) for a renewal one, and
``asymptotic_expected_equivalent_annual_cost`` values should only ever be compared *within*
one family. The finite-horizon ``expected_net_present_value`` and
``expected_equivalent_annual_cost`` remain comparable across both, since they are evaluated on
the same explicit timeline.
