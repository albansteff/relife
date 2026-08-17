The reward and discounting framework
=======================================

:doc:`run_to_failure` and :doc:`preventive_age_replacement` both reduce to the same question:
attach a cost to each renewal of the :doc:`renewal process <renewal_theory>`, and compute the
expected cost per unit of time. ``RenewalRewardProcess`` is where that happens; the policies
are thin wrappers over it. It takes a lifetime model, and two further ingredients supplied as
arguments to its methods: a **reward** (how much does *this* renewal cost) and a
**discounting rate** (how much is a cost incurred at time :math:`x` worth today).

>>> from relife.datasets import load_circuit_breaker
>>> from relife.lifetime_models import Weibull
>>> from relife.stochastic_processes import RenewalRewardProcess
>>> dataset = load_circuit_breaker()
>>> weibull = Weibull().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])
>>> process = RenewalRewardProcess(weibull)

Rewards
--------

A reward answers "what does this renewal cost, given how long it lasted". It isn't a separate
object to build: you describe it with the cost keyword arguments accepted by every method of
the process. Two shapes are available, and they are exactly the two policies above.

Passing ``cf`` alone means every renewal is a failure costing ``cf`` whatever its duration,
i.e. :math:`Y = c_f`:

>>> round(float(process.asymptotic_expected_equivalent_annual_worth(cf=1500.)), 2)
20.47

Passing ``cf``, ``cp`` and ``ar`` together instead makes the cost a step function of the
realized lifetime :math:`X`: the asset costs ``cf`` if it failed before the replacement age,
and ``cp`` if it reached it and was replaced preventively.

.. math::

    Y = \begin{cases} c_f & \text{if } X < a_r \\ c_p & \text{if } X \geq a_r \end{cases}

>>> round(float(process.asymptotic_expected_equivalent_annual_worth(cf=1500., cp=400., ar=47.44)), 2)
11.69

Those are the same 20.47 and 11.69 that :doc:`run_to_failure` and
:doc:`preventive_age_replacement` report: the policies simply pick the reward shape for you
and rename the method.

The step is easy to see by pushing ``ar`` far beyond the range of plausible lifetimes, so
that virtually no asset ever reaches the replacement age and ``cp`` is never paid:

>>> round(float(process.asymptotic_expected_equivalent_annual_worth(cf=1500., cp=400., ar=200.)), 6)
20.474811

The age-replacement reward has degenerated into the run-to-failure one. ``cp`` and ``ar``
describe a single decision and only make sense together, so setting one without the other is
rejected rather than silently ignored:

>>> process.asymptotic_expected_equivalent_annual_worth(cf=1500., cp=400.)
Traceback (most recent call last):
    ...
TypeError: cp and ar must be set together.

First-cycle costs
~~~~~~~~~~~~~~~~~~~

In a *delayed* process (one whose first asset doesn't start new, either because
``first_lifetime_model`` differs from ``lifetime_model`` or because an initial age ``a0`` is
given), the first renewal can be given its own costs through ``cf1`` and ``cp1``. Starting
from assets already 20 time units old, and making that first replacement twice as expensive
as the following ones:

>>> import numpy as np
>>> timeline, z = process.expected_total_reward(100., 5, cf=1500., a0=20.)
>>> np.round(z, 2)
array([   0.  ,  150.95,  662.81, 1328.36, 1788.86])
>>> timeline, z1 = process.expected_total_reward(100., 5, cf=1500., cf1=3000., a0=20.)
>>> np.round(z1, 2)
array([   0.  ,  301.4 , 1315.48, 2578.88, 3268.35])

These two arguments only affect the first cycle, so they leave the long-run rate untouched
and matter on a finite horizon only. Note that they are honoured for a delayed process only:
on a non-delayed one there is nothing to distinguish the first renewal from the others, and
``cf1`` is ignored.

Discounting
------------

A cost incurred later is worth less than the same cost incurred now. ReLife applies
exponential discounting at a rate :math:`\delta`, passed as ``discounting_rate`` to any
method: a factor :math:`e^{-\delta x}` converts a single cost at time :math:`x` into its
present value, and an annuity factor :math:`\frac{1-e^{-\delta x}}{\delta}` converts a total
into the equivalent constant annual worth. At a 5 % rate:

>>> rate = 0.05
>>> times = np.array([0., 10., 50.])
>>> np.exp(-rate * times)
array([1.        , 0.60653066, 0.082085  ])
>>> (1 - np.exp(-rate * times)) / rate
array([ 0.        ,  7.86938681, 18.35830003])

A cost paid in 50 time units counts for about 8 % of its face value. With ``rate=0.``, the
default used everywhere above, both factors reduce to no discounting at all and every cost
counts in full whenever it occurs.

That default is not innocuous. Without discounting, the expected *total* cost of an
indefinitely renewed asset diverges, since the renewals never stop accumulating:

>>> float(process.asymptotic_expected_total_reward(cf=1500.))
inf

which is why the policies report an annualized rate instead. Introduce a rate and the same
total becomes finite, because distant renewals contribute geometrically less:

>>> round(float(process.asymptotic_expected_total_reward(cf=1500., discounting_rate=0.05)), 2)
72.65

Discounting also shifts the decision itself, not just its accounting. Costs deferred into the
future being cheaper, waiting longer becomes more attractive, and the optimal replacement age
moves later:

>>> from relife.policies import AgeReplacementPolicy
>>> ar_star = AgeReplacementPolicy(weibull).compute_optimal_ar(cf=1500., cp=400., discounting_rate=0.05)
>>> round(float(ar_star), 2)
61.14

61.1 against the 47.4 obtained undiscounted in :doc:`preventive_age_replacement`.

Putting it together: the renewal reward process
---------------------------------------------------

Combining a lifetime model, a reward and a discounting rate, the expected *total* reward up
to time :math:`t` solves a renewal equation very similar to :doc:`renewal_theory`'s renewal
function:

.. math::

    z(t) = \int_0^t \mathbb{E}[Y \mid X = x] e^{-\delta x} \mathrm{d}F(x)
         + \int_0^t z(t-x) e^{-\delta x}\mathrm{d}F(x)

where :math:`X` is the interarrival (lifetime) random variable, :math:`Y` its associated
reward, and :math:`F` its cumulative distribution function. Solving it over an explicit
timeline gives the cumulative cost trajectory:

>>> timeline, z = process.expected_total_reward(500., 51, cf=1500.)
>>> np.round(z[::10], 1)
array([   0. , 1435.2, 3418.6, 5459.5, 7508.7, 9547.7])

Late in that timeline the total grows by about 2040 per 100 time units, i.e. very close to
the 20.47 per unit of time found above: this is the long-run rate emerging. Re-expressed per
unit of time, it converges to it explicitly:

.. math::

    z^\infty = \lim_{t\to \infty} \frac{z(t)}{AF(t)} = \frac{\mathbb{E}\left[Y e^{-\delta X}\right]}{1-\mathbb{E}\left[e^{-\delta X}\right]}

>>> timeline, q = process.expected_equivalent_annual_worth(500., 51, cf=1500.)
>>> np.round(q[::10], 2)
array([ 0.  , 14.35, 17.09, 18.2 , 18.77, 19.1 ])

Still climbing towards 20.47 after 500 time units: a long-run rate is a limit, and a fleet
observed over a finite horizon sits below it.

The four methods used on this page are the ones the policies expose under maintenance
vocabulary, so anything shown here can be read directly off a policy object:

===============================================  ==============================================
``RenewalRewardProcess``                         policy
===============================================  ==============================================
``expected_total_reward``                        ``expected_net_present_value``
``asymptotic_expected_total_reward``             ``asymptotic_expected_net_present_value``
``expected_equivalent_annual_worth``             ``expected_equivalent_annual_cost``
``asymptotic_expected_equivalent_annual_worth``  ``asymptotic_expected_equivalent_annual_cost``
===============================================  ==============================================

:doc:`cost_calculations` covers that policy-level API, and what changes for the one-cycle
policies, which integrate the reward directly instead of solving this renewal equation.
