Distributions, regressions, and likelihood
=============================================

Parametric distributions
--------------------------

A parametric lifetime distribution assumes a fixed functional shape (Weibull, Gamma,
Gompertz, ...) for the survival function, and estimates its parameters from data. Fitting
one is a single call, accounting for censoring and truncation as described in
:doc:`censoring_and_truncation`:

>>> from relife.datasets import load_power_transformer
>>> from relife.lifetime_models import Weibull
>>> dataset = load_power_transformer()
>>> weibull = Weibull().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])
>>> weibull.get_params()
array([3.46597396, 0.0122785 ])

Maximum likelihood and choosing a shape
------------------------------------------

Fitting works by maximizing the likelihood of the observed data under the chosen
distribution: each row contributes a term to the log-likelihood that depends on whether it
was an observed failure, a right-censored observation, or left-truncated (see
:doc:`censoring_and_truncation`), and ``fit`` searches for the parameters that maximize the
sum of these terms (equivalently, minimize the negative log-likelihood). The result is
stored on ``fitting_results``, along with information criteria (AIC, AICc, BIC) that let you
compare *different distribution shapes* fitted on the same data; the lower, the better the
trade-off between fit quality and number of parameters:

>>> print(weibull.fitting_results)
fitted params : [3.46597, 0.0122785]
AIC           : 3400.49
AICc          : 3400.49
BIC           : 3411.3

>>> from relife.lifetime_models import Gamma
>>> gamma = Gamma().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])
>>> print(gamma.fitting_results)
fitted params : [5.35711, 0.0662282]
AIC           : 3442.37
AICc          : 3442.37
BIC           : 3453.18

On this dataset, the Weibull shape has both a lower AIC and a lower BIC than Gamma, so it's
the better-supported choice between the two.

Regressions: adding covariates
-----------------------------------

A distribution alone can't account for the fact that different assets operate under
different conditions. Regressions extend a baseline distribution with covariates: for
instance, an insulator string's lifetime plausibly depends on the acid concentrations it's
exposed to (see :doc:`../../datasets`).
``ParametricProportionalHazard`` scales the baseline hazard function by
:math:`e^{\beta \cdot \text{covar}}`; fitting it estimates both the regression coefficients
and the baseline distribution's parameters together:

>>> import numpy as np
>>> from relife.datasets import load_insulator_string
>>> from relife.lifetime_models import ParametricProportionalHazard, Gompertz
>>> insulator_data = load_insulator_string()
>>> covar = [
...     insulator_data["pHCl"], insulator_data["pH2SO4"], insulator_data["HNO3"]
... ]
>>> regression = ParametricProportionalHazard(Gompertz()).fit(
...     insulator_data["time"], covar,
...     event=insulator_data["event"], entry=insulator_data["entry"],
... )
>>> regression.get_params()
array([ 4.11133664, -2.67876549,  3.24289683,  0.22422175,  0.02944488])

The first three parameters are the covariate coefficients (for ``pHCl``, ``pH2SO4`` and
``HNO3`` respectively), and the last two are the baseline Gompertz distribution's own
parameters. ``ParametricAcceleratedFailureTime`` offers the same interface with a different
covariate effect (rescaling time instead of the hazard rate). See
:doc:`../../../examples/regression_modeling` for a complete, worked example on this dataset.

For a covariate effect that isn't estimated jointly with the baseline distribution's shape,
see :doc:`semi_parametric_cox`.
