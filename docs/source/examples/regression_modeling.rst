Regression modeling with covariates
======================================

A single fitted distribution describes an *average* asset. That is the right model when the
fleet is interchangeable, and the wrong one when it isn't: a transformer in a coastal
substation and one inland are not the same asset, and averaging them produces a curve that
describes neither. Regression keeps one baseline shape for the family and lets measured
conditions shift the hazard around it.

This example uses the insulator string dataset (see :doc:`../user_guides/datasets`), 12000
strings with the three acid concentrations they are exposed to; see
:doc:`../user_guides/background/lifetime_modeling/regressions` for the model itself.

When covariates are worth the trouble
----------------------------------------

Splitting the fleet and fitting a separate distribution per group is the simpler option and
is often better. Regression earns its extra parameters when the grouping variable is
continuous (a concentration, a load factor, a temperature), when groups would be too small to
fit separately, or when predictions are needed for a combination of conditions that no group
in the data represents exactly.

It also imposes an obligation the simpler approach doesn't: the covariates must be known for
*every* asset you later want a prediction for, including the ones you are deciding about.

Building the covariate arrays
--------------------------------

Covariates are passed as a **sequence of 1d arrays**, one array per covariate, not as a
single 2d array:

>>> import numpy as np
>>> from relife.datasets import load_insulator_string
>>> dataset = load_insulator_string()
>>> covar = [dataset["pHCl"], dataset["pH2SO4"], dataset["HNO3"]]
>>> len(covar), covar[0].shape
(3, (12000,))

Three practical points when assembling these from real records:

- **Scale drives interpretation, not fit.** A coefficient is per unit of the covariate, so
  the same effect reads as 4.4 or 0.044 depending on whether a concentration is in units or
  percent. Keep the units you will quote results in.
- **Missing covariate values have no encoding.** There is no sentinel for "unknown
  concentration": the row is either complete or dropped. Substituting the fleet mean is
  tempting and quietly shrinks the estimated effect towards zero.
- **A covariate must be measurable in advance.** Anything recorded *at* failure, or derived
  from the outcome, will produce a spectacular fit and no predictive value.

>>> from relife.lifetime_models import ParametricProportionalHazard, Gompertz
>>> regression = ParametricProportionalHazard(Gompertz()).fit(
...     dataset["time"], covar, event=dataset["event"], entry=dataset["entry"]
... )
>>> regression.get_params()
array([ 4.11133664, -2.67876549,  3.24289683,  0.22422175,  0.02944488])

The first three values are the covariate coefficients, in the order the covariates were
passed (``pHCl``, ``pH2SO4``, ``HNO3``); the last two are the baseline Gompertz ``shape`` and
``rate``.

Reading the coefficients
---------------------------

In a proportional hazard model a coefficient is a log hazard ratio, so exponentiating it
turns it into the multiplier on the failure rate. Quoting it over a realistic change in the
covariate rather than over one unit keeps it meaningful:

>>> round(float(np.exp(4.11133664 * 0.1)), 2)
1.51
>>> covar[0].min(), covar[0].max()
(np.float64(0.3), np.float64(1.5))

A 0.1 increase in ``pHCl`` multiplies the failure rate by about 1.5, and the observed range
spans 0.3 to 1.5, so the most and least exposed strings in this fleet are separated by orders
of magnitude in hazard, not by a few percent. That is the practical justification for
modeling them separately at all.

The signs are worth pausing on: ``pHCl`` and ``HNO3`` increase the hazard, ``pH2SO4``
decreases it. A negative coefficient on something believed to be corrosive is exactly the
kind of result to challenge before publishing, since it usually means the covariate is
standing in for something else it correlates with (a site, a supplier, a design generation)
rather than acting causally.

.. plot::
    :context: close-figs

    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> from relife.datasets import load_insulator_string
    >>> from relife.lifetime_models import ParametricProportionalHazard, Gompertz
    >>> dataset = load_insulator_string()
    >>> covar = [dataset["pHCl"], dataset["pH2SO4"], dataset["HNO3"]]
    >>> regression = ParametricProportionalHazard(Gompertz()).fit(
    ...     dataset["time"], covar, event=dataset["event"], entry=dataset["entry"]
    ... )
    >>> timeline = np.arange(0, 100)
    >>> for idx in (0, 1, 2):
    ...     _ = regression.plot(
    ...         "hf", timeline, *(c[idx] for c in covar), label=f"hf of asset {idx}"
    ...     )
    >>> _ = plt.xlabel("time")
    >>> _ = plt.ylabel("hazard rate")
    >>> _ = plt.legend()
    >>> plt.show()

What dropping the entry ages does here
-----------------------------------------

The bias described in :doc:`non_parametric_estimation` shifted a survival probability by a
few points. On a regression it does considerably more damage, because the truncation is not
independent of the covariates: the strings that survived long enough to enter observation are
disproportionately the ones in mild conditions, so omitting ``entry`` lets exposure look
harmless.

>>> wrong = ParametricProportionalHazard(Gompertz()).fit(
...     dataset["time"], covar, event=dataset["event"]
... )
>>> np.round(wrong.get_params(), 3)
array([1.058, 3.288, 0.516, 0.   , 0.035])

Every conclusion changes. The ``pHCl`` effect collapses from 4.11 to 1.06, ``HNO3`` from 3.24
to 0.52, and the ``pH2SO4`` coefficient flips sign, turning a protective association into an
apparently strong accelerating one. A study built on this fit would recommend controlling the
wrong acid.

The failure is silent (same call, no warning, plausible-looking numbers), which is why the
``entry`` column belongs in the dataset from the moment it is assembled, not added later if
results look odd.

Proportional hazard or accelerated failure time
--------------------------------------------------

``ParametricAcceleratedFailureTime`` fits the same way and takes the same covariates, but
applies the covariate effect to *time* rather than to the hazard rate: exposure makes the
asset age faster instead of making it fail more often at a given age. The two coincide only
for a Weibull baseline.

The choice is physical, not statistical. Use proportional hazards when exposure adds a
failure mechanism that acts at all ages, such as external stress or shocks. Use accelerated
failure time when exposure speeds up a degradation process the asset would undergo anyway,
such as corrosion, insulation ageing or thermal wear, which is usually the better description for
grid equipment in an aggressive chemical environment. When the physics is genuinely unclear,
fit both and compare criteria as in :doc:`distributions_fitting`, but treat that as a
tie-break rather than as the argument.

To estimate the same covariate effects without committing to a baseline shape at all, see
:doc:`semi_parametric_cox`.
