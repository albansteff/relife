The semi-parametric Cox model
===============================

``ParametricProportionalHazard`` (see :doc:`distributions_and_regressions`) assumes a fixed
baseline distribution shape and estimates it jointly with the covariate effect. The Cox
proportional hazard model relaxes that assumption: it estimates the covariate effect without
committing to any particular shape for the baseline hazard, which is instead left
unspecified ("semi-parametric" — only the covariate part is parametric).

>>> import numpy as np
>>> from relife.datasets import load_insulator_string
>>> from relife.lifetime_models import SemiParametricProportionalHazard
>>> dataset = load_insulator_string()
>>> covar = np.column_stack((dataset["pHCl"], dataset["pH2SO4"], dataset["HNO3"]))
>>> cox = SemiParametricProportionalHazard()
>>> cox = cox.fit(time=dataset["time"], covar=covar, event=dataset["event"])
>>> np.round(cox.get_params(), 3)  # the underlying solver isn't bit-exact run to run
array([ 5.088, -2.986,  4.518])

These three coefficients are the covariate effects (for ``pHCl``, ``pH2SO4`` and ``HNO3``),
directly comparable to the first three coefficients of the ``ParametricProportionalHazard``
fit in :doc:`distributions_and_regressions` — without needing to also get the baseline
distribution's shape right.

Because there's no parametric baseline, ``sf`` returns the estimated timeline together with
the survival values, rather than evaluating at arbitrary times like a parametric model
would:

>>> timeline, sf_values = cox.sf(covar=covar[:2, :], se=False)
>>> timeline[:3]
array([1.1, 2.6, 3. ])
>>> np.round(sf_values[0][:3], 4)
array([1.    , 0.9999, 0.9999])
>>> np.round(sf_values[1][:3], 4)
array([0.9999, 0.9997, 0.9995])

.. plot::
    :context: close-figs

    >>> import matplotlib.pyplot as plt
    >>> import numpy as np
    >>> from relife.datasets import load_insulator_string
    >>> from relife.lifetime_models import SemiParametricProportionalHazard
    >>> dataset = load_insulator_string()
    >>> covar = np.column_stack((dataset["pHCl"], dataset["pH2SO4"], dataset["HNO3"]))
    >>> cox = SemiParametricProportionalHazard().fit(
    ...     time=dataset["time"], covar=covar, event=dataset["event"]
    ... )
    >>> timeline, sf_values = cox.sf(covar=covar[:2, :], se=False)
    >>> _ = plt.plot(timeline, sf_values[0], label="asset 0")
    >>> _ = plt.plot(timeline, sf_values[1], label="asset 1")
    >>> _ = plt.xlabel("time")
    >>> _ = plt.ylabel("survival probability")
    >>> _ = plt.legend()
    >>> plt.show()

The two assets shown here have different covariate values (different acid exposure), hence
the different estimated survival curves. See
:doc:`../../../examples/semi_parametric_cox` for a more complete worked example.
