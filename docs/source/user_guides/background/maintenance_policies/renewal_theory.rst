Renewal processes and the renewal equation
=============================================

Every maintenance policy in ReLife (:doc:`run_to_failure`, :doc:`preventive_age_replacement`)
is built on the same underlying model: a **renewal process**. Each time an asset is
replaced (whether on failure or preventively), the process "renews": a new asset starts
its own, statistically identical lifetime. ``RenewalProcess`` wraps a lifetime model this
way:

>>> from relife.datasets import load_circuit_breaker
>>> from relife.lifetime_models import Weibull
>>> from relife.stochastic_processes import RenewalProcess
>>> dataset = load_circuit_breaker()
>>> weibull = Weibull().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])
>>> renewal_process = RenewalProcess(weibull)

Each simulated asset lifetime is a random draw, so the number of renewals observed by time
:math:`t`, written :math:`N(t)`, is itself random and traces out a step function that jumps
by one at every replacement.

The quantity of interest for planning purposes isn't one random realization, but its
average across the whole fleet: the expected number of renewals up to time :math:`t`, the
**renewal function** :math:`m(t) = \mathbb{E}[N(t)]`. It's obtained by solving the renewal
equation

.. math::

    m(t) = F_1(t) + \int_0^t m(t-x) \mathrm{d}F(x)

where :math:`F` is the cumulative distribution function of the time between two renewals,
and :math:`F_1` is the cumulative distribution function of the *first* renewal (the two
differ if the process is "delayed", e.g. the first asset wasn't new when observation
started). Solving it numerically over a timeline:

>>> timeline, m = renewal_process.renewal_function(100., 5)
>>> timeline
array([  0.,  25.,  50.,  75., 100.])
>>> m
array([0.        , 0.01236231, 0.15251764, 0.53746995, 0.96142435])

After 100 time units, this fleet is expected to have gone through just under one full
replacement per asset on average, consistent with the Weibull fit's mean lifetime of about
73 time units (``weibull.mean()``), with the renewal function still below its long-run rate
of :math:`1/\mathbb{E}[X]` this early in the timeline.

This is the mechanism that everything else in the maintenance-policy layer is built on: a
policy replaces "renewal" with "renewal *and its cost*" (see :doc:`reward_framework`) to
go from "how many replacements do I expect" to "how much will they cost".

The one exception is the one-cycle policies (``OneCycleRunToFailurePolicy`` and
``OneCycleAgeReplacementPolicy``, see :doc:`run_to_failure` and
:doc:`preventive_age_replacement`). Since they stop at the first replacement, there is no
sequence of renewals to solve for: no renewal equation is involved, and their costs are
obtained by integrating the reward directly against the lifetime distribution of the single
cycle.
