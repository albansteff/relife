Preventive age replacement policy
====================================

Instead of always waiting for failure, an asset can be replaced preventively once it
reaches a fixed age ``ar``, at a (usually lower) cost ``cp``; it is still replaced
at cost ``cf`` if it fails before reaching ``ar`` [1]_. Choosing ``ar``
trades off the risk of an expensive failure against replacing an asset that still had useful
life left.

**Assumptions**

* the asset ages, i.e. its hazard rate :math:`h` is increasing;
* it is replaced either preventively at age ``ar`` at cost ``cp``, or on failure before that
  age at cost ``cf`` > ``cp``;
* it is replaced by an identical asset over successive cycles (no obsolescence);

**Objective**: determine the replacement age ``ar`` minimizing the asymptotic cost per unit
of time.

>>> from relife.datasets import load_circuit_breaker
>>> from relife.lifetime_models import Weibull
>>> from relife.policies import AgeReplacementPolicy
>>> dataset = load_circuit_breaker()
>>> weibull = Weibull().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])
>>> policy = AgeReplacementPolicy(weibull)

The expected annual cost depends on the chosen replacement age, and evaluating it at a few
candidate ages already shows there's a sweet spot:

>>> [round(float(policy.asymptotic_expected_equivalent_annual_cost(ar=ar, cf=1500., cp=400.)), 2) for ar in (25., 40., 60.)]
[16.59, 12.08, 12.54]

Rather than scanning candidate ages by hand, ``compute_optimal_ar`` solves for the
cost-minimizing age directly [2]_:

>>> ar_star = policy.compute_optimal_ar(cf=1500., cp=400.)
>>> round(float(ar_star), 2)
47.44
>>> round(float(policy.asymptotic_expected_equivalent_annual_cost(ar=ar_star, cf=1500., cp=400.)), 2)
11.69

Replacing preventively at age 47.4 costs about 11.69 per unit of time in the long run,
against 20.47 for :doc:`run_to_failure` on the same fitted model and failure cost; see
:doc:`cost_calculations` for where these numbers come from mechanically.

Stopping after one cycle
--------------------------

Like :doc:`run_to_failure`, this policy has a one-cycle counterpart for decisions that only
concern the asset currently in service. ``OneCycleAgeReplacementPolicy`` charges ``cp`` if
the asset reaches ``ar`` and ``cf`` if it fails before, then stops; there is no renewal, so
the expected cost of the cycle is simply the two costs weighted by their probabilities:

>>> from relife.policies import OneCycleAgeReplacementPolicy
>>> one_cycle = OneCycleAgeReplacementPolicy(weibull)
>>> round(float(one_cycle.asymptotic_expected_net_present_value(ar=ar_star, cf=1500., cp=400.)), 2)
539.15

Because the criterion being minimized is not the same, the optimal age isn't either:

>>> one_cycle_ar_star = one_cycle.compute_optimal_ar(cf=1500., cp=400.)
>>> round(float(one_cycle_ar_star), 2)
43.46
>>> round(float(one_cycle.asymptotic_expected_equivalent_annual_cost(ar=one_cycle_ar_star, cf=1500., cp=400.)), 2)
12.77

Both optima sit in the same region: the lifetime model, not the horizon, does most of the
work. But the one-cycle optimum lands slightly earlier here, and its annualized cost (12.77)
is not directly comparable to the renewal policy's 11.69: the two numbers annualize over
different horizons (see :doc:`cost_calculations`). Use the one-cycle policies to rank options
for a single asset, and the renewal policies to plan a fleet over the long run.

.. [1] Mazzuchi, T. A., Van Noortwijk, J. M., & Kallen, M. J. (2007). Maintenance
    optimization. Encyclopedia of Statistics in Quality and Reliability, 1000-1008.
.. [2] Coolen-Schrijner, P., & Coolen, F. P. A. (2006). On optimality criteria for age
    replacement. Proceedings of the Institution of Mechanical Engineers, Part O: Journal
    of Risk and Reliability, 220(1), 21-29.
