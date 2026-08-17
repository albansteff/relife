Run-to-failure policy
=======================

The simplest maintenance policy: an asset is used until it fails, then replaced, at a cost
``cf`` per failure [1]_. There is no preventive action: it's the baseline every other
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
<renewal_theory>` where every renewal costs ``cf`` (see :doc:`reward_framework`). The
long-run expected cost per unit of time follows directly from that:

>>> policy.asymptotic_expected_equivalent_annual_cost(cf=1500.)
np.float64(20.47481108112064)

Since every renewal has the same cost regardless of when it happens, this only depends on
how often the asset needs replacing (i.e. on the fitted lifetime model), not on any
decision variable. Compare with :doc:`preventive_age_replacement`, where replacing *before*
failure can lower this expected cost.

Stopping after one cycle
--------------------------

``RunToFailurePolicy`` assumes the asset is replaced again and again, indefinitely. When the
decision only concerns the asset currently in service (one replacement, with no commitment
to what happens afterwards), ``OneCycleRunToFailurePolicy`` stops at the first failure
instead of renewing:

>>> from relife.policies import OneCycleRunToFailurePolicy
>>> one_cycle = OneCycleRunToFailurePolicy(weibull)
>>> round(float(one_cycle.asymptotic_expected_net_present_value(cf=1500.)), 2)
1500.0

A single cycle contains exactly one failure, so the expected undiscounted cost is just
``cf``. The annualized figure, however, is not the same as the renewal one:

>>> round(float(one_cycle.asymptotic_expected_equivalent_annual_cost(cf=1500.)), 2)
23.12

23.12 against 20.47 above. The one-cycle criterion spreads ``cf`` over the realized lifetime
of *this* asset and averages that ratio over the lifetime distribution; the renewal policy
divides by the mean lifetime of a whole sequence of assets. Short lifetimes weigh far more
heavily in the first quantity, so it comes out higher. The ``period_before_discounting``
constructor argument (1 by default) floors the duration used in that division, so an asset
failing almost immediately does not send the annualized cost to infinity.

.. [1] Van der Weide, J. A. M., & Van Noortwijk, J. M. (2008). Renewal theory with
    exponential and hyperbolic discounting. Probability in the Engineering and
    Informational Sciences, 22(1), 53-74.
