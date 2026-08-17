Semi-parametric Cox regression
================================

The parametric regression in :doc:`regression_modeling` needed two decisions: how covariates
act, and what the baseline lifetime shape is. Cox regression removes the second one. It
estimates covariate effects while leaving the baseline hazard completely unspecified, which
is the right trade when the question is *"which conditions shorten asset life, and by how
much"* rather than *"how long will this asset last"*.

This example uses the same insulator string dataset (see :doc:`../user_guides/datasets`); see
:ref:`cox_model` for the model itself.

>>> import numpy as np
>>> from relife.datasets import load_insulator_string
>>> from relife.lifetime_models import SemiParametricProportionalHazard
>>> dataset = load_insulator_string()
>>> covar = [dataset["pHCl"], dataset["pH2SO4"], dataset["HNO3"]]
>>> cox = SemiParametricProportionalHazard(
...     time=dataset["time"], covar=covar, event=dataset["event"], entry=dataset["entry"]
... )
>>> np.round(cox.get_params(), 3)  # the underlying solver isn't bit-exact run to run
array([ 4.406, -2.985,  3.874])

Note ``entry`` in that call. Dropping a baseline assumption does not exempt the model from
the observation scheme, and on this dataset 8216 of the 12000 strings entered observation
already aged. Fitting without it moves every coefficient:

>>> cox_no_entry = SemiParametricProportionalHazard(
...     time=dataset["time"], covar=covar, event=dataset["event"]
... )
>>> np.round(cox_no_entry.get_params(), 3)
array([ 5.088, -2.986,  4.518])

The ``pHCl`` effect is overstated by 15% and ``HNO3`` by 17%. Cox is more robust here than
the parametric regression, which flipped a sign under the same omission, but "more robust"
is not "immune", and the direction of the error is not knowable in advance.

Cross-checking against the parametric fit
--------------------------------------------

With the truncation handled, the two models agree closely, despite one of them having assumed
a Gompertz baseline and the other nothing at all:

==========  ================================  =====
Covariate   ``ParametricProportionalHazard``  Cox
==========  ================================  =====
``pHCl``    4.11                              4.41
``pH2SO4``  -2.68                             -2.99
``HNO3``    3.24                              3.87
==========  ================================  =====

This agreement is the useful diagnostic. The parametric model's coefficients could in
principle be an artifact of forcing a Gompertz shape onto the data; the fact that a model
free of any such assumption lands in the same place says they are not. When the two disagree
substantially, the baseline shape is doing work it shouldn't, and the parametric fit needs
revisiting before its extrapolations are used.

Predicting survival for individual assets
---------------------------------------------

>>> estimation = cox.sf(*(c[:3] for c in covar), se=False)
>>> timeline, sf_values = estimation.timeline, estimation.values
>>> np.column_stack([c[:3] for c in covar])
array([[0.49, 1.69, 0.24],
       [0.76, 1.79, 0.39],
       [0.43, 1.61, 0.25]])
>>> np.round(sf_values[:, ::200], 3)
array([[1.   , 0.959, 0.876, 0.746, 0.54 ],
       [1.   , 0.835, 0.56 , 0.279, 0.068],
       [1.   , 0.959, 0.874, 0.744, 0.535]])

Asset 1 is the most exposed on all three acids and its survival profile is visibly worse;
assets 0 and 2 have near-identical conditions and near-identical curves. For an asset manager
this is the ranking that matters: which strings to inspect first, not what their absolute
lifetime is.

.. plot::
    :context: close-figs

    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> from relife.datasets import load_insulator_string
    >>> from relife.lifetime_models import SemiParametricProportionalHazard
    >>> dataset = load_insulator_string()
    >>> covar = [dataset["pHCl"], dataset["pH2SO4"], dataset["HNO3"]]
    >>> cox = SemiParametricProportionalHazard(
    ...     time=dataset["time"], covar=covar, event=dataset["event"], entry=dataset["entry"]
    ... )
    >>> estimation = cox.sf(*(c[:3] for c in covar), se=False)
    >>> timeline, sf_values = estimation.timeline, estimation.values
    >>> for idx in (0, 1, 2):
    ...     _ = plt.plot(timeline, sf_values[idx], label=f"asset {idx}")
    >>> _ = plt.xlabel("time")
    >>> _ = plt.ylabel("survival probability")
    >>> _ = plt.legend()
    >>> plt.show()

What you give up
-------------------

The survival curve above exists only on the observed timeline. There is no baseline formula
to evaluate past the last failure, no mean lifetime, and consequently no way to feed a Cox
model into a maintenance policy: everything in :doc:`maintenance_policy_costs` requires a
parametric lifetime model.

That decides the choice in practice. Use Cox for diagnosis: ranking assets by risk,
quantifying which conditions matter, and validating a parametric regression's coefficients.
Use a parametric regression when the answer has to extrapolate or turn into a replacement
age. The two are complementary steps in the same study far more often than they are
alternatives: fit Cox first to see what the covariates do without prejudging the shape, then
commit to a baseline once you know the effects are real.
