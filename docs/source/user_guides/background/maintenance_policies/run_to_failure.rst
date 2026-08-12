Run-to-failure policy
=======================

The simplest maintenance policy: an asset is used until it fails, then replaced, at a cost
:math:`c_f` per failure [1]_. There is no preventive action — it's the baseline every other
policy is compared against.

>>> from relife.datasets import load_circuit_breaker
>>> from relife.lifetime_models import Weibull
>>> from relife.policies import RunToFailurePolicy
>>> dataset = load_circuit_breaker()
>>> weibull = Weibull().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])
>>> policy = RunToFailurePolicy(weibull)
>>> type(policy).__name__
'RunToFailurePolicy'

Under the hood, this wraps the fitted lifetime model in a :doc:`renewal process
<renewal_theory>` where every renewal costs :math:`c_f` — see :doc:`reward_framework`. The
long-run expected cost per unit of time follows directly from that:

>>> policy.asymptotic_expected_equivalent_annual_cost(cf=1500.)
np.float64(20.47481108112064)

Since every renewal has the same cost regardless of when it happens, this only depends on
how often the asset needs replacing — i.e. on the fitted lifetime model — not on any
decision variable. Compare with :doc:`preventive_age_replacement`, where replacing *before*
failure can lower this expected cost.

.. [1] Van der Weide, J. A. M., & Van Noortwijk, J. M. (2008). Renewal theory with
    exponential and hyperbolic discounting. Probability in the Engineering and
    Informational Sciences, 22(1), 53-74.
