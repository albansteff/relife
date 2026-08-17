Non-parametric survival and hazard estimation
================================================

This is the first thing to run on a newly assembled fleet dataset: it shows what the records
actually say, before any modeling choice can distort it. The example uses the circuit breaker
dataset (see :doc:`../user_guides/datasets`), 4204 real RTE breakers.

Knowing what you actually have
---------------------------------

Before estimating anything, count the two things that decide which estimator is usable at
all: how many failures were really seen, and how many assets were already in service when
observation started.

>>> from relife.datasets import load_circuit_breaker
>>> dataset = load_circuit_breaker()
>>> dataset["event"].sum(), len(dataset)
(np.int64(204), 4204)
>>> (dataset["entry"] > 0).sum()
np.int64(4000)

Only 204 of 4204 breakers were observed failing, and 4000 of them entered the study already
aged. This is what industrial fleet data normally looks like: the equipment outlives the
monitoring system, so nearly everything is right-censored, and monitoring started long after
the assets were installed.

Two conventions matter when you build such an array from your own records, and both are easy
to get wrong:

- ``time`` is the asset's **total age** at the moment it was last seen, not the time elapsed
  since it entered observation. ``entry`` is its age when observation started. A breaker
  installed in 1980, observed from 2010, still working in 2024, is ``time=44``, ``entry=30``,
  ``event=False``.
- ``event`` marks whether the failure was *actually observed*, not whether the asset is
  currently broken. An asset replaced preventively, decommissioned, or sold is
  ``event=False``: you know it reached that age, not that it failed there.

ReLife rejects the most common encoding error outright rather than fitting something
meaningless:

>>> from relife.lifetime_models import Weibull
>>> Weibull().fit(dataset["time"] - dataset["entry"], event=dataset["event"], entry=dataset["entry"])
Traceback (most recent call last):
    ...
ValueError: All time values must be greater than entry values

Assets whose installation date is unknown are the usual missing-data case. There is no way to
supply a partial age: either you can bound the install date well enough to give an ``entry``,
or the record has to be dropped. Dropping it is the safer of the two, but only if the
unknown-date assets aren't systematically the oldest ones, which they often are.

Estimating survival
----------------------

``KaplanMeier`` and ``NelsonAalen`` both take the censoring and truncation into account
directly. Neither assumes anything about the shape of the lifetime distribution.

>>> from relife.lifetime_models import KaplanMeier, NelsonAalen
>>> km = KaplanMeier(dataset["time"], event=dataset["event"], entry=dataset["entry"])
>>> na = NelsonAalen(dataset["time"], event=dataset["event"], entry=dataset["entry"])

``sf()``/``chf()`` return the whole estimated curve (timeline, values, and standard errors)
rather than a function you evaluate anywhere, so reading an estimate at a given age means
locating it on the timeline:

>>> import numpy as np
>>> sf = km.sf()
>>> idx = np.searchsorted(sf.timeline, 40., side="right") - 1
>>> round(float(sf.values[idx]), 4), round(float(sf.se[idx]), 4)
(0.9312, 0.0082)

An estimated 93.1% of breakers are still in service at 40 years, with a standard error of
0.8%. That standard error is not decoration: it widens sharply where few assets remain at
risk, which is exactly the old-age region a replacement decision depends on. An estimate
without its standard error is not a usable input to a policy.

The same three records, three different answers
--------------------------------------------------

This is where studies go wrong, and it is worth doing deliberately once. Take the same 4204
records and treat them three ways: keeping only the assets seen failing, accounting for
censoring but not for the entry ages, and accounting for both.

>>> from relife.lifetime_models import ECDF
>>> failures_only = dataset[dataset["event"]]
>>> naive = ECDF(failures_only["time"]).sf()
>>> i = np.searchsorted(naive.timeline, 40., side="right") - 1
>>> round(float(naive.values[i]), 4)
0.5
>>> km_no_entry = KaplanMeier(dataset["time"], event=dataset["event"]).sf()
>>> j = np.searchsorted(km_no_entry.timeline, 40., side="right") - 1
>>> round(float(km_no_entry.values[j]), 4)
0.9639

Against the correct 0.9312, the three answers to "what fraction of the fleet is still
standing at 40 years" are 50%, 96.4% and 93.1%.

The first is **mortality bias**: discarding the 4000 censored breakers keeps only the assets
that failed, so by construction all of them are dead by the end. The population being
described is "breakers that failed", not "breakers". It is the more dangerous error because
it looks like a clean dataset: no censoring flags, no truncation, every row a real observed
failure.

The second is **survivor bias**: ignoring ``entry`` treats a breaker that entered observation
at 30 as if it had been watched from new, crediting the model with 30 years of failure-free
service that was never observed. Worse, the assets that failed *before* 1980-something never
made it into the records at all, so the sample only contains units hardy enough to still be
there. The result is optimistic at every age.

Neither error announces itself. Both fit without warning, and the direction of the resulting
bias is systematic, not random, so more data does not fix it. :doc:`maintenance_policy_costs`
shows what these two numbers do to an actual replacement decision.

Choosing between the estimators
----------------------------------

.. plot::
    :context: close-figs

    >>> import matplotlib.pyplot as plt
    >>> from relife.datasets import load_circuit_breaker
    >>> from relife.lifetime_models import KaplanMeier, NelsonAalen
    >>> dataset = load_circuit_breaker()
    >>> km = KaplanMeier(dataset["time"], event=dataset["event"], entry=dataset["entry"])
    >>> na = NelsonAalen(dataset["time"], event=dataset["event"], entry=dataset["entry"])
    >>> fig, axs = plt.subplots(ncols=2, nrows=1, figsize=(10, 4))
    >>> _ = km.plot("sf", ax=axs[0])
    >>> _ = na.plot("chf", ax=axs[1])
    >>> _ = axs[0].set_title("Kaplan-Meier survival function")
    >>> _ = axs[1].set_title("Nelson-Aalen cumulative hazard")
    >>> plt.show()

Both are step functions that only move at the 204 observed failure times, which is the honest
picture: between two failures, the data contains no information.

Use **Kaplan-Meier** when the question is "what fraction survives to age :math:`t`": fleet
availability, spare provisioning, contractual survival guarantees. Use **Nelson-Aalen** when
the question is about the failure *rate* and whether it rises with age: its cumulative hazard
curving upwards is the signature of wear-out, and therefore the evidence that preventive
replacement can pay off at all. On a fleet with a flat hazard, no replacement age beats
run-to-failure, and that verdict is visible here before any model is fitted.

Do not use the plain **ECDF** on censored data, as done above to illustrate the bias: it is
only correct when every asset was followed from installation to failure, which essentially
never happens on in-service equipment.

What non-parametric estimation cannot do is go past the last observation, or produce the mean
lifetime and smooth hazard a maintenance policy needs. That is the job of a fitted
distribution, and these curves are the yardstick to check it against; see
:doc:`distributions_fitting`.
