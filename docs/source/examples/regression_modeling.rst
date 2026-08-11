Regression modeling with covariates
======================================

This example fits a proportional hazard regression on the insulator string dataset (see
:doc:`../user_guides/datasets`), whose three covariates (acid concentrations) plausibly
accelerate degradation — see
:doc:`../user_guides/background/lifetime_modeling/distributions_and_regressions` for the
model itself.

>>> import numpy as np
>>> from relife.datasets import load_insulator_string
>>> dataset = load_insulator_string()
>>> covar = np.column_stack((dataset["pHCl"], dataset["pH2SO4"], dataset["HNO3"]))
>>> covar.shape
(12000, 3)

>>> from relife.lifetime_models import ParametricProportionalHazard, Gompertz
>>> regression = ParametricProportionalHazard(Gompertz()).fit(
...     dataset["time"], covar, event=dataset["event"], entry=dataset["entry"]
... )
>>> regression.get_params_names()
('coef_1', 'coef_2', 'coef_3', 'shape', 'rate')
>>> regression.get_params()
array([ 4.11133664, -2.67876549,  3.24289683,  0.22422175,  0.02944488])

All three coefficients are far from zero, and of different signs — ``pHCl`` and ``HNO3``
increase the hazard rate (positive coefficients), while ``pH2SO4`` decreases it. Two
insulators exposed to different acid concentrations therefore have different hazard curves,
even though they share the same baseline Gompertz shape:

.. plot::
    :context: close-figs

    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> from relife.datasets import load_insulator_string
    >>> from relife.lifetime_models import ParametricProportionalHazard, Gompertz
    >>> dataset = load_insulator_string()
    >>> covar = np.column_stack((dataset["pHCl"], dataset["pH2SO4"], dataset["HNO3"]))
    >>> regression = ParametricProportionalHazard(Gompertz()).fit(
    ...     dataset["time"], covar, event=dataset["event"], entry=dataset["entry"]
    ... )
    >>> timeline = np.arange(0, 100)
    >>> for idx in (0, 1, 2):
    ...     _ = regression.plot("hf", timeline, covar[idx], label=f"hf of asset {idx}")
    >>> _ = plt.xlabel("time")
    >>> _ = plt.ylabel("hazard rate")
    >>> _ = plt.legend()
    >>> plt.show()

``ParametricAcceleratedFailureTime`` fits the same way and accepts the same covariates, but
rescales *time* by the covariate effect instead of the hazard rate — the choice between the
two is about which effect shape better matches the physical degradation mechanism, not a
difference in how you call them. For a covariate effect estimated without committing to a
baseline shape at all, see :doc:`semi_parametric_cox`.
