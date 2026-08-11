Fitting parametric distributions
===================================

This example fits two candidate distributions on the power transformer dataset (see
:doc:`../user_guides/datasets`) and picks the better one using the likelihood-based criteria
introduced in :doc:`../user_guides/background/lifetime_modeling/distributions_and_regressions`.

>>> from relife.datasets import load_power_transformer
>>> dataset = load_power_transformer()
>>> dataset.dtype.names
('time', 'event', 'entry')

Fit both a Weibull and a Gompertz distribution, accounting for the dataset's censoring and
truncation:

>>> from relife.lifetime_models import Weibull, Gompertz
>>> weibull = Weibull().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])
>>> gompertz = Gompertz().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])
>>> weibull.get_params()
array([3.46597396, 0.0122785 ])
>>> gompertz.get_params()
array([0.00865741, 0.06062632])

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

Gompertz has both a lower AIC and a lower BIC here — for this fleet of transformers, its
shape describes the observed failure pattern better than Weibull's.

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

The two fitted survival curves are close over most of the timeline but diverge past around
80 time units, which is where the AIC/BIC gap above comes from. Once you've picked a
distribution, plug it into a maintenance policy — see
:doc:`maintenance_policy_costs`.
