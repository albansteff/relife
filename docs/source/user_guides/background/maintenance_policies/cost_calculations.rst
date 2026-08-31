Cost calculations
===================

:doc:`run_to_failure` and :doc:`preventive_age_replacement` both expose
``asymptotic_expected_equivalent_annual_cost``, the long-run expected cost per unit of time
that a :doc:`renewal reward process <reward_framework>` converges to. For a run-to-failure
policy this number does not depend on any decision you make; for an age-replacement policy,
it is a function of the replacement age ``ar``, and that is the whole point: it lets you
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
:doc:`preventive_age_replacement`) locates the minimum of this curve.

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

The four cost methods
-----------------------

Every policy, renewal or one-cycle, run-to-failure or age-replacement, exposes the same four
methods. They are the reward methods of the underlying
:doc:`renewal reward process <reward_framework>`, renamed into maintenance vocabulary:

===============================================  ==============================================
policy                                           ``RenewalRewardProcess``
===============================================  ==============================================
``expected_net_present_value``                   ``expected_total_reward``
``asymptotic_expected_net_present_value``        ``asymptotic_expected_total_reward``
``expected_equivalent_annual_cost``              ``expected_equivalent_annual_worth``
``asymptotic_expected_equivalent_annual_cost``   ``asymptotic_expected_equivalent_annual_worth``
===============================================  ==============================================

The net present value is what the policy will have cost by a given date, counted in money of
today; the equivalent annual cost is that same amount rewritten as a constant yearly payment,
which is what makes two policies comparable. In each pair, the plain method works on an
explicit horizon and takes a final time ``tf`` and a number of points ``nb_steps``, returning
the timeline together with the values along it, while the ``asymptotic_`` one takes no
timeline and returns a single number.

>>> import numpy as np
>>> timeline, npv = policy.expected_net_present_value(200., 201, ar=47.44, cf=1500., cp=400.)
>>> np.round(npv[::50], 2)
array([   0.  ,  539.97, 1081.47, 1625.66, 2173.95])
>>> timeline, eeac = policy.expected_equivalent_annual_cost(200., 201, ar=47.44, cf=1500., cp=400.)
>>> np.round(eeac[::50], 2)
array([ 0.  , 10.8 , 10.81, 10.84, 10.87])
>>> round(float(policy.asymptotic_expected_equivalent_annual_cost(ar=47.44, cf=1500., cp=400.)), 2)
11.69

The age-replacement policies want both costs together, since ``ar`` describes no decision
without a ``cp`` to weigh against ``cf``:

>>> policy.asymptotic_expected_equivalent_annual_cost(ar=47.44, cf=1500.)
Traceback (most recent call last):
    ...
TypeError: Missing cf and cp values

Costs and ages are vectorized over assets: a 1d ``ar`` evaluates several candidate ages, or
several fleets each with its own costs, in a single call. This is how the curve plotted above
is best computed.

>>> np.round(policy.asymptotic_expected_equivalent_annual_cost(ar=np.array([40., 47.44, 60.]), cf=1500., cp=400.), 2)
array([12.08, 11.69, 12.54])

Counting the replacements behind the cost
--------------------------------------------

A cost figure says nothing about the workload that produces it. ``AgeReplacementPolicy``
projects the replacements themselves, year by year:

``annual_number_of_replacements(nb_years, *, ar, a0=None)``
    the expected number of replacements during each year, all causes together.

``annual_number_of_failures(nb_years, *, ar, a0=None)``
    the part of them caused by a failure. Subtract one from the other and you have the
    preventive workload.

Both return a timeline of whole years and one value per year, so they read directly as a
maintenance schedule. On a fleet of identical assets all commissioned on the same date, that
schedule is anything but flat:

>>> timeline, n_replacements = policy.annual_number_of_replacements(60, ar=47.44)
>>> timeline, n_failures = policy.annual_number_of_failures(60, ar=47.44)
>>> timeline[44:50]
array([45., 46., 47., 48., 49., 50.])
>>> np.round(n_replacements[44:50], 3)
array([0.008, 0.008, 0.009, 0.878, 0.   , 0.   ])
>>> np.round(n_failures[44:50], 3)
array([0.008, 0.008, 0.009, 0.004, 0.   , 0.   ])

Almost nothing happens for 47 years, then 88 % of the fleet is replaced in year 48, the year
in which every surviving asset crosses ``ar`` at once, and the years after that are empty
again. Barely 0.4 % of the fleet fails during that peak year: the rest is preventive work,
scheduled by the policy itself. This is exactly what a single annual cost figure smooths
away.

Over the whole projection, the two series say how the replacements split:

>>> round(float(n_replacements.sum()), 3)
1.004
>>> round(float(n_failures.sum()), 3)
0.129

Roughly one replacement per asset in 60 years, 13 % of them on failure. Those are the counts
that ``cf`` and ``cp`` get applied to.

The peak is an artefact of a perfectly homogeneous fleet. Give the assets different initial
ages through ``a0`` and each one gets its own column, which is how a real mixed-age fleet is
projected: four cohorts commissioned ten years apart produce four smaller peaks instead of
one.

>>> timeline, n_cohorts = policy.annual_number_of_replacements(60, ar=47.44, a0=np.array([0., 10., 20., 30.]))
>>> n_cohorts.shape
(60, 4)
>>> timeline[n_cohorts.argmax(axis=0)]
array([48., 38., 28., 18.])

These two methods are the year-by-year form of the counters ``expected_number_of_events`` and
``expected_number_of_preventive_renewals`` described in :doc:`reward_framework`, which report
the same information cumulated since time 0 over an arbitrary timeline rather than aggregated
per year.

What ``asymptotic`` means for a one-cycle policy
---------------------------------------------------

``OneCycleRunToFailurePolicy`` and ``OneCycleAgeReplacementPolicy`` expose exactly the same
four methods, so the two families are drop-in interchangeable. But the quantities they
return answer different questions, and mixing them up is the easy mistake to make here.

For a renewal policy, the ``asymptotic_`` prefix means *as the number of renewals grows*: the
net present value diverges without discounting, and the annual cost converges to a long-run
rate. For a one-cycle policy there is only ever one replacement, so the prefix simply means
*over the whole of that single cycle*, with no truncation at a finite horizon. Its net present
value is therefore finite even undiscounted, being the expected cost of one replacement, and
its annual cost is that expected cost annualized over the realized cycle duration rather than
a long-run rate.

Side by side on the same fleet, the same costs and the same replacement age:

>>> from relife.policies import OneCycleAgeReplacementPolicy
>>> one_cycle = OneCycleAgeReplacementPolicy(weibull)
>>> float(policy.asymptotic_expected_net_present_value(ar=47.44, cf=1500., cp=400.))
inf
>>> round(float(one_cycle.asymptotic_expected_net_present_value(ar=47.44, cf=1500., cp=400.)), 2)
539.17
>>> round(float(policy.asymptotic_expected_equivalent_annual_cost(ar=47.44, cf=1500., cp=400.)), 2)
11.69
>>> round(float(one_cycle.asymptotic_expected_equivalent_annual_cost(ar=47.44, cf=1500., cp=400.)), 2)
12.89

The 539.17 is the expected cost of a single replacement cycle, a perfectly readable figure
that the renewal policy simply cannot report undiscounted. The 12.89 and the 11.69 are not
the same quantity, and their difference means nothing: one annualizes a single cycle, the
other is a long-run rate. Compare ``asymptotic_`` values within one family only. The
finite-horizon ``expected_net_present_value`` and ``expected_equivalent_annual_cost`` remain
comparable across both, since they are evaluated on the same explicit timeline.
