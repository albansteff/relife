Preventive age replacement policy
====================================

Instead of always waiting for failure, an asset can be replaced preventively once it
reaches a fixed age :math:`a_r`, at a (usually lower) cost :math:`c_p`; it is still replaced
at cost :math:`c_f` if it fails before reaching :math:`a_r` [1]_. Choosing :math:`a_r`
trades off the risk of an expensive failure against replacing an asset that still had useful
life left.

>>> from relife.datasets import load_circuit_breaker
>>> from relife.lifetime_models import Weibull
>>> from relife.policies import AgeReplacementPolicy
>>> dataset = load_circuit_breaker()
>>> weibull = Weibull().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])
>>> policy = AgeReplacementPolicy(weibull)

The expected annual cost depends on the chosen replacement age — evaluating it at a few
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
against 20.47 for :doc:`run_to_failure` on the same fitted model and failure cost — see
:doc:`cost_calculations` for where these numbers come from mechanically, and
:doc:`../../../examples/maintenance_policy_costs` for a fuller worked example.

.. [1] Mazzuchi, T. A., Van Noortwijk, J. M., & Kallen, M. J. (2007). Maintenance
    optimization. Encyclopedia of Statistics in Quality and Reliability, 1000-1008.
.. [2] Coolen-Schrijner, P., & Coolen, F. P. A. (2006). On optimality criteria for age
    replacement. Proceedings of the Institution of Mechanical Engineers, Part O: Journal
    of Risk and Reliability, 220(1), 21-29.
