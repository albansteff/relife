Fitting parametric distributions
===================================

A non-parametric estimate stops at the last observed failure and gives no mean lifetime, so
it cannot answer "what happens at 100 years" or feed a maintenance policy. Fitting a
distribution buys both, at the price of an assumption about the shape. This example fits two
candidates on the power transformer dataset (see :doc:`../user_guides/datasets`) and, more
importantly, shows how far the resulting model can be trusted.

>>> from relife.datasets import load_power_transformer
>>> dataset = load_power_transformer()
>>> dataset["event"].sum(), len(dataset)
(np.int64(318), 1650)

318 observed failures out of 1650 transformers, with 1158 units entering observation already
aged. As always, both facts go into the fit; see
:doc:`../user_guides/background/lifetime_modeling/censoring_and_truncation` for why omitting
either one biases the result rather than merely blurring it.

>>> from relife.lifetime_models import Weibull, Gompertz
>>> weibull = Weibull().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])
>>> gompertz = Gompertz().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])
>>> weibull.get_params()
array([3.46597396, 0.0122785 ])
>>> gompertz.get_params()
array([0.00865741, 0.06062632])

Choosing a candidate shape
-----------------------------

The candidates should be picked from what is known about how the equipment degrades, not by
sweeping every distribution in the library. Three shapes cover most power-grid equipment:

- **Exponential**: constant hazard, failures arrive at random regardless of age. Appropriate
  for equipment dominated by external causes (lightning, third-party damage, operator error).
  If this one wins, no age-based replacement policy will ever beat run-to-failure, and the
  study is over.
- **Weibull**: hazard following a power of age. The default for mechanical wear-out, and
  flexible enough that its shape parameter above 1 is itself the evidence of ageing.
- **Gompertz**: hazard rising exponentially with age. Fits degradation that accelerates once
  it starts, such as insulation and dielectric ageing in transformers.

Comparing information criteria
---------------------------------

>>> print(weibull.fitting_results)
fitted params : [3.46597, 0.0122785]
AIC           : 3400.49
AICc          : 3400.49
BIC           : 3411.3
>>> print(gompertz.fitting_results)
fitted params : [0.00865741, 0.0606263]
AIC           : 3374.22
AICc          : 3374.23
BIC           : 3385.04

Gompertz wins on both criteria, by about 26 points. That is a decisive gap on this scale, and
consistent with the physics: transformer failure is driven by insulation ageing, which
accelerates.

What the criteria compare is fit *over the observed data*. They say nothing about the region
where there is no data, and they cannot detect a shape that is wrong for the right reason,
since two models can agree everywhere you looked and diverge completely where the decision is
actually made.

Checking the fit against the data
------------------------------------

The real acceptance test is the non-parametric estimate from
:doc:`non_parametric_estimation`, which makes no shape assumption. A fitted curve that
tracks it through the dense part of the timeline has earned its interpolation:

>>> import numpy as np
>>> from relife.lifetime_models import KaplanMeier
>>> km = KaplanMeier(dataset["time"], event=dataset["event"], entry=dataset["entry"]).sf()
>>> for age in (40., 60., 80.):
...     i = np.searchsorted(km.timeline, age, side="right") - 1
...     print(age, round(float(km.values[i]), 3), round(float(weibull.sf(age)), 3), round(float(gompertz.sf(age)), 3))
40.0 0.911 0.918 0.915
60.0 0.725 0.707 0.726
80.0 0.318 0.391 0.334

At 40 and 60 years both models sit within a point or two of the empirical curve. At 80 the
gap opens: Gompertz stays close to the observed 0.318 while Weibull is 7 points optimistic,
which is where the AIC difference comes from and, on a fleet of 1650 units, amounts to about
120 transformers misplaced on the wrong side of the survival curve.

.. plot::
    :context: close-figs

    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> from relife.datasets import load_power_transformer
    >>> from relife.lifetime_models import Weibull, Gompertz
    >>> dataset = load_power_transformer()
    >>> weibull = Weibull().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])
    >>> gompertz = Gompertz().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])
    >>> timeline = np.arange(0, 100)
    >>> _ = weibull.plot("sf", timeline, label="Weibull")
    >>> _ = gompertz.plot("sf", timeline, label="Gompertz")
    >>> _ = plt.xlabel("time")
    >>> _ = plt.ylabel("survival probability")
    >>> _ = plt.legend()
    >>> plt.show()

How far the model can be pushed
----------------------------------

Past the data, the two fitted shapes stop agreeing, and nothing in the data can arbitrate:

>>> round(float(weibull.sf(100.)), 4), round(float(gompertz.sf(100.)), 4)
(0.1304, 0.0245)

13% against 2.5%, a factor of five, at an age where the dataset holds nothing at all:

>>> int((dataset["time"] >= 80).sum()), int((dataset["event"] & (dataset["time"] >= 80)).sum())
(31, 5)

Thirty-one transformers ever reached 80 years and five of them were seen failing. Beyond
that, both curves are the shape assumption talking, not the fleet. The practical rule is to
treat predictions as supported up to roughly the age where the at-risk count is still
substantial, and to carry both candidate models through the decision when the answer depends
on a region past it. If Weibull and Gompertz recommend the same replacement age, the shape
choice didn't matter; if they don't, that disagreement is the honest uncertainty and should
be reported as such rather than resolved by picking the lower AIC.

The mean lifetime is subject to the same caveat, since it integrates over the whole tail:

>>> round(float(weibull.mean()), 1), round(float(gompertz.mean()), 1)
(73.2, 69.6)

Both fitted models are usable inputs to a policy; see :doc:`maintenance_policy_costs`. If the
fleet is not homogeneous (different manufacturers, sites, or operating stresses), a single
distribution averages over differences that matter, and :doc:`regression_modeling` is the
next step instead.
