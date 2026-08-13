The reward and discounting framework
=======================================

:doc:`run_to_failure` and :doc:`preventive_age_replacement` both reduce to the same question:
attach a cost to each renewal of the :doc:`renewal process <renewal_theory>`, and compute the
expected cost per unit of time. ReLife factors this into two independent building blocks: a
**reward** (how much does *this* renewal cost) and a **discounting** function (how much is a
cost incurred at time :math:`x` worth today) that combine into a **renewal reward
process**.

Rewards
--------

A ``Reward`` answers "what does this renewal cost, given how long it lasted". The two built
in ReLife directly encode the two policies above:

>>> import numpy as np
>>> from relife.rewards import RunToFailureReward, AgeReplacementReward
>>> rtf_reward = RunToFailureReward(cf=1500.)
>>> rtf_reward.conditional_expectation(np.array([10., 50., 200.]))
array([1500., 1500., 1500.])

A run-to-failure reward costs ``cf`` no matter how long the asset lasted, since every
renewal is a failure. An age-replacement reward instead depends on whether the asset made it
to the replacement age ``ar``:

>>> ar_reward = AgeReplacementReward(cf=1500., cp=400., ar=47.44)
>>> ar_reward.conditional_expectation(np.array([10., 50., 200.]))
array([1500.,  400.,  400.])

At ``t=10``, below ``ar``, the asset failed before reaching the replacement age, so it costs
``cf``; at ``t=50`` and ``t=200``, both past ``ar``, it was replaced preventively at cost
``cp``.

Discounting
------------

A cost incurred later is discounted relative to a cost incurred now. ``ExponentialDiscounting``
applies a rate :math:`\delta`: a factor :math:`e^{-\delta x}` to a single cost, or an annuity
factor :math:`\frac{1-e^{-\delta x}}{\delta}` to convert a total into its equivalent constant
annual worth:

>>> from relife.rewards import ExponentialDiscounting
>>> discounting = ExponentialDiscounting(rate=0.05)
>>> discounting.factor(np.array([0., 10., 50.]))
array([1.        , 0.60653066, 0.082085  ])
>>> discounting.annuity_factor(np.array([0., 10., 50.]))
array([ 0.        ,  7.86938681, 18.35830003])

With ``rate=0.`` (ReLife's default, and what :doc:`run_to_failure` and
:doc:`preventive_age_replacement` used), both factors reduce to no discounting at all:
every cost counts at face value regardless of when it occurs.

Putting it together: the renewal reward process
---------------------------------------------------

A ``RenewalRewardProcess`` combines a lifetime model, a reward, and a discounting function.
The expected *total* reward up to time :math:`t` solves a renewal equation very similar to
:doc:`renewal_theory`'s renewal function:

.. math::

    z(t) = \int_0^t \mathbb{E}[Y \mid X = x] e^{-\delta x} \mathrm{d}F(x)
         + \int_0^t z(t-x) e^{-\delta x}\mathrm{d}F(x)

where :math:`X` is the interarrival (lifetime) random variable, :math:`Y` its associated
reward, and :math:`F` its cumulative distribution function. Without discounting
(:math:`\delta = 0`), this total keeps growing forever as more renewals accumulate; it
diverges as :math:`t \to \infty`, which is why the policies report an *annualized* rate
instead of a raw total. That rate is this same total reward, re-expressed per unit of time,
in the long run:

.. math::

    z^\infty = \lim_{t\to \infty} \frac{z(t)}{AF(t)} = \frac{\mathbb{E}\left[Y e^{-\delta X}\right]}{1-\mathbb{E}\left[e^{-\delta X}\right]}

This is exactly what :doc:`run_to_failure`'s and :doc:`preventive_age_replacement`'s
``asymptotic_expected_equivalent_annual_cost`` compute: the run-to-failure reward from
above (``cf=1500``) on the same fitted model gives the 20.47 per-unit-of-time figure shown
there. :doc:`cost_calculations` covers the policy-level API that wraps all of this so you
don't need to build the process by hand.
