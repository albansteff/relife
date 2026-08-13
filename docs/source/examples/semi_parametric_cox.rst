Semi-parametric Cox regression
================================

This example fits the Cox proportional hazard model on the insulator string dataset (see
:doc:`../user_guides/datasets`). See
:doc:`../user_guides/background/lifetime_modeling/semi_parametric_cox` for how it differs
from the fully parametric regression in :doc:`regression_modeling`.

>>> import numpy as np
>>> from relife.datasets import load_insulator_string
>>> from relife.lifetime_models import SemiParametricProportionalHazard
>>> dataset = load_insulator_string()
>>> covar = [dataset["pHCl"], dataset["pH2SO4"], dataset["HNO3"]]
>>> cox = SemiParametricProportionalHazard(
...     time=dataset["time"], covar=covar, event=dataset["event"]
... )
>>> np.round(cox.get_params(), 3)  # the underlying solver isn't bit-exact run to run
array([ 5.088, -2.986,  4.518])
>>> round(float(cox.fitting_results.aic), 1), round(float(cox.fitting_results.bic), 1)
(35358.4, 35380.6)

The three coefficients (for ``pHCl``, ``pH2SO4`` and ``HNO3`` respectively) are close to
the ones found with the fully parametric ``ParametricProportionalHazard(Gompertz())`` fit in
:doc:`regression_modeling` (4.11, -2.68, 3.24 there), even though this model never assumed a
Gompertz (or any other) baseline shape.

Predicting survival for individual assets
---------------------------------------------

>>> estimation = cox.sf(*(c[:3] for c in covar), se=False)
>>> timeline, sf_values = estimation.timeline, estimation.values
>>> np.column_stack([c[:3] for c in covar])
array([[0.49, 1.69, 0.24],
       [0.76, 1.79, 0.39],
       [0.43, 1.61, 0.25]])
>>> np.round(sf_values[:, ::200], 3)
array([[1.   , 0.981, 0.931, 0.829, 0.607],
       [1.   , 0.895, 0.661, 0.339, 0.056],
       [1.   , 0.981, 0.932, 0.832, 0.613]])

Asset 1 (higher ``pH2SO4``, and both other acids too) has a visibly worse survival profile
than assets 0 and 2, which have similar covariate values and similar predicted survival:

.. plot::
    :context: close-figs

    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> from relife.datasets import load_insulator_string
    >>> from relife.lifetime_models import SemiParametricProportionalHazard
    >>> dataset = load_insulator_string()
    >>> covar = [dataset["pHCl"], dataset["pH2SO4"], dataset["HNO3"]]
    >>> cox = SemiParametricProportionalHazard(
    ...     time=dataset["time"], covar=covar, event=dataset["event"]
    ... )
    >>> estimation = cox.sf(*(c[:3] for c in covar), se=False)
    >>> timeline, sf_values = estimation.timeline, estimation.values
    >>> for idx in (0, 1, 2):
    ...     _ = plt.plot(timeline, sf_values[idx], label=f"asset {idx}")
    >>> _ = plt.xlabel("time")
    >>> _ = plt.ylabel("survival probability")
    >>> _ = plt.legend()
    >>> plt.show()

Unlike a fitted parametric model, this survival curve is only defined on the observed
timeline: there's no baseline formula to extrapolate from, which is the trade-off for not
having to choose a baseline shape in the first place.
