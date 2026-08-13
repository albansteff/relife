Non-parametric lifetime models
================================

Before fitting a parametric distribution, it's often useful to estimate the survival or
hazard function directly from the data, without assuming any particular shape. ReLife
provides three such estimators, and they don't all handle censoring the same way: picking
the wrong one silently gives the wrong answer.

>>> from relife.datasets import load_circuit_breaker
>>> dataset = load_circuit_breaker()

ECDF: assumes no censoring
------------------------------

The empirical CDF just counts, for each ``time``, the fraction of observations at or below
it. It takes no ``event``/``entry`` argument at all: every row is treated as an observed
failure. On ``load_circuit_breaker``, only ~5% of the 4204 units were actually observed
failing; the rest are right-censored (see :doc:`censoring_and_truncation`). Feeding censored
data to ``ECDF`` treats "still working when we stopped observing it" as "failed at that
exact time", which is wrong:

>>> from relife.lifetime_models import ECDF
>>> ecdf = ECDF(dataset["time"])
>>> ecdf.sf().values[-1]  # estimated survival at the end of the observed timeline
np.float64(0.0)

ECDF concludes that *nothing* survives past the last observed time, because it has no
notion that most of those "last observed times" were censoring, not failure.

Kaplan-Meier: survival function, robust to censoring
---------------------------------------------------------

The Kaplan-Meier (product-limit) estimator only counts a decrease in survival at times
where a failure was actually observed, and correctly keeps censored units "at risk" up to
the time they were last seen:

>>> from relife.lifetime_models import KaplanMeier
>>> km = KaplanMeier(dataset["time"], event=dataset["event"], entry=dataset["entry"])
>>> km.sf().values[-1]
np.float64(0.19193717878444425)

Roughly 19% of the fleet is estimated to still be surviving at the end of the observed
timeline, a very different picture than ECDF's 0%.

Nelson-Aalen: cumulative hazard, robust to censoring
----------------------------------------------------------

The Nelson-Aalen estimator targets the cumulative hazard function :math:`H(t)` instead of
the survival function, using the same at-risk logic as Kaplan-Meier:

>>> from relife.lifetime_models import NelsonAalen
>>> na = NelsonAalen(dataset["time"], event=dataset["event"], entry=dataset["entry"])
>>> na.chf().values[-1]
np.float64(1.4826380355269857)

Survival and cumulative hazard are related by :math:`S(t) = e^{-H(t)}`, so the two
estimators should roughly agree:

>>> import numpy as np
>>> np.exp(-na.chf().values[-1])
np.float64(0.22703796347019162)

The two values (0.192 from Kaplan-Meier, 0.227 from :math:`e^{-H}`) are close but not
identical, which is expected, since they're two distinct nonparametric estimators of related but
different quantities, not two ways of computing the same number.

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

These estimators are a good sanity check before committing to a parametric shape (see
:doc:`distributions_and_regressions`): if a fitted distribution's survival curve strays far
from the Kaplan-Meier estimate, that shape is probably a poor fit for the data.
