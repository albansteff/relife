Comparing maintenance policies on cost
=========================================

This is the step where a lifetime model becomes a decision: a replacement age, an annual
budget, and a defensible answer to "why not just run them to failure". It compares
:doc:`../user_guides/background/maintenance_policies/run_to_failure` against
:doc:`../user_guides/background/maintenance_policies/preventive_age_replacement` for the
fleet of 4204 circuit breakers (see :doc:`../user_guides/datasets`).

>>> from relife.datasets import load_circuit_breaker
>>> from relife.lifetime_models import Weibull
>>> dataset = load_circuit_breaker()
>>> weibull = Weibull().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])

Framing the costs
--------------------

``cf`` and ``cp`` are the hardest part of the study, and they are not maintenance invoices.
``cf`` is the total consequence of an in-service failure, which for grid equipment usually
means the replacement itself plus emergency mobilisation, unplanned outage and energy not
supplied, collateral damage to neighbouring equipment, and any regulatory or contractual
penalty. ``cp`` is the same replacement carried out on schedule: planned crew, planned
outage window, no collateral, and often a partially depreciated asset recovered rather than
destroyed.

Two properties make this tractable in practice:

- **Only the ratio matters** to the recommended age. Scaling both costs leaves the optimal
  replacement age untouched and scales the resulting cost figure by the same factor, so an
  incomplete but *consistent* costing still gives the right decision.
- The consequences that are hardest to price (outage duration, penalties) sit almost
  entirely in ``cf``, so the usual effect of under-costing is to understate the ratio, which
  biases the recommendation towards replacing too late.

Getting the ratio to within a factor of two is worth far more effort than getting either
figure exactly right.

Baseline scenario
--------------------

With a failure costing ``cf`` = 1500 and a planned replacement ``cp`` = 400 (any unit, as long
as both use the same one):

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

Replacing at 47.4 years costs 11.69 per breaker per year against 20.47 for run-to-failure: a
43% reduction, and the justification for the policy.

Sensitivity: what if preventive replacement isn't that much cheaper?
-------------------------------------------------------------------------

The size of that gap depends entirely on the ratio. Raising the preventive cost from 400 to
1200, still below the 1500 failure cost but not by much:

>>> ar_star_expensive = policy.compute_optimal_ar(cf=1500., cp=1200.)
>>> round(float(ar_star_expensive), 2)
93.53
>>> round(float(policy.asymptotic_expected_equivalent_annual_cost(ar=ar_star_expensive, cf=1500., cp=1200.)), 2)
20.29

The optimal age shifts to 93.5 and the cost (20.29) is within 1% of run-to-failure's 20.47.
The policy has effectively recommended doing nothing, which is the correct answer: when a
planned replacement costs nearly as much as a failure, there is nothing to buy by acting
early. A sensitivity sweep like this one is the honest way to present a recommendation, since
it shows the range of cost assumptions over which the conclusion survives.

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
    >>> for cp, label in ((400., "cp=400"), (1200., "cp=1200")):
    ...     policy = AgeReplacementPolicy(weibull)
    ...     costs = [
    ...         float(policy.asymptotic_expected_equivalent_annual_cost(ar=ar, cf=1500., cp=cp))
    ...         for ar in ar_range
    ...     ]
    ...     _ = plt.plot(ar_range, costs, marker="o", label=label)
    >>> _ = plt.axhline(float(rtf.asymptotic_expected_equivalent_annual_cost(cf=1500.)), color="grey", linestyle="--", label="run-to-failure")
    >>> _ = plt.xlabel("replacement age ar")
    >>> _ = plt.ylabel("expected annual cost")
    >>> _ = plt.legend()
    >>> plt.show()

The cheaper-preventive curve has a sharp minimum well below the run-to-failure line; the
expensive one is flat and barely dips under it. Flatness is itself useful information: where
the curve is flat, missing the optimal age by a few years costs almost nothing, and the
policy can be aligned with outage windows and crew availability instead.

What a data-handling error costs
-----------------------------------

:doc:`non_parametric_estimation` showed the same records giving three different survival
estimates. Carried through to the decision, those become three different recommendations:

>>> naive = Weibull().fit(dataset[dataset["event"]]["time"])          # failures only
>>> no_entry = Weibull().fit(dataset["time"], event=dataset["event"])  # censoring only
>>> for name, model in (("mortality bias", naive), ("survivor bias", no_entry), ("correct", weibull)):
...     p = AgeReplacementPolicy(model)
...     ar = p.compute_optimal_ar(cf=1500., cp=400.)
...     cost = p.asymptotic_expected_equivalent_annual_cost(ar=ar, cf=1500., cp=400.)
...     print(f"{name:15s} ar*={float(ar):6.2f}  cost={float(cost):6.2f}")
mortality bias  ar*= 26.16  cost= 20.52
survivor bias   ar*= 47.40  cost= 10.58
correct         ar*= 47.44  cost= 11.69

Discarding the censored breakers recommends replacing at 26 years instead of 47: every
breaker scrapped with roughly 21 years of service life left, on a fleet of 4204, and a budget
overstated by 75%. Nothing in that analysis looks wrong: it fits cleanly, the curve has a
proper minimum, the recommendation is a plausible number.

The survivor-bias case is the more insidious of the two. It lands on essentially the correct
replacement age, so the decision variable gives no warning at all; the error surfaces only in
the budget, understated by about 10%. A recommendation that looks right is not evidence that
the data was handled right.

Turning the policy into a budget
-----------------------------------

An annual cost per asset is not yet a plan. ``annual_number_of_replacements`` and
``annual_number_of_failures`` project the physical workload, which is what determines crews,
spares and cash. This matters most for a fleet that is already in service: passing ``a0``
states the current age of the assets rather than assuming they are new.

For breakers currently 40 years old, under the 47.4-year policy:

>>> import numpy as np
>>> years, replacements = policy.annual_number_of_replacements(10, ar=ar_star, a0=40.)
>>> years, failures = policy.annual_number_of_failures(10, ar=ar_star, a0=40.)
>>> np.round(replacements * len(dataset), 0)
array([  29.,   31.,   33.,   34.,   36.,   38.,   40., 3963.,    0.,
          0.])
>>> np.round(failures * len(dataset), 0)
array([29., 31., 33., 34., 36., 38., 40., 18.,  0.,  0.])

For seven years the workload is about 30 to 40 units annually, and every one of them is a
failure: these are the breakers that won't make it to the replacement age. Then in year
eight, when the fleet crosses 47.4, essentially all 3963 survivors come due at once.

That cliff is a real and common consequence of a fleet installed over a short period, and it
is not something the annual-cost figure reveals: the long-run rate of 11.69 per breaker
averages over a workload that is in fact 40 units in year seven and 4000 in year eight. No
utility can replace a fleet in one year. The projection is what turns the optimum into a
feasible programme, typically by spreading replacements over a window around ``ar_star``,
which the flatness of the cost curve makes nearly free.

.. figure:: /_static/figures/cost_comparison_paths.png
    :alt: Cumulative replacement cost over time for a run-to-failure policy versus the optimal age-replacement policy, for two lifetime models, each showing the optimal policy tracking noticeably below run-to-failure.
    :width: 100%

    Simulated cumulative cost trajectories, optimal age-replacement policy versus
    run-to-failure, for two lifetime models. The gap between the solid (optimal policy) and
    dashed (run-to-failure) lines widens steadily, which is the forecast that determines the
    budget and the stock of spare parts to plan for over a given horizon.

Money later is worth less
----------------------------

Every figure above is undiscounted, which implicitly treats a replacement in 50 years as
costing exactly what one today costs. Over asset lifetimes measured in decades that
assumption is not neutral, and correcting it moves the recommendation:

>>> ar_discounted = policy.compute_optimal_ar(cf=1500., cp=400., discounting_rate=0.05)
>>> round(float(ar_discounted), 2)
61.14

At a 5% rate the optimal age moves from 47.4 to 61.1 years. Deferring a cost makes waiting
more attractive, so any study run undiscounted is systematically biased towards replacing
early. The rate belongs to the organisation's financial framework, not to the reliability
analysis, so it should be taken from it rather than chosen here.

If a single replacement decision is being made about assets currently in service, with no
commitment to what replaces them, the one-cycle policies answer that question instead; see
:doc:`../user_guides/background/maintenance_policies/from_process_to_policy`.
