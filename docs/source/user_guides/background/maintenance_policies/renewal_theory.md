# Renewal processes and the renewal equation

Every maintenance policy in ReLife ([Run-to-failure policy](run_to_failure.md),
[Preventive age replacement policy](preventive_age_replacement.md)) is built on the same
underlying model: a **renewal process**. Each time an asset is
replaced (whether on failure or preventively), the process "renews": a new asset starts
its own, statistically identical lifetime. `RenewalProcess` wraps a lifetime model this
way:

```python
>>> from relife.datasets import load_circuit_breaker
>>> from relife.lifetime_models import Weibull
>>> from relife.stochastic_processes import RenewalProcess
>>> dataset = load_circuit_breaker()
>>> weibull = Weibull().fit(dataset["time"], event=dataset["event"], entry=dataset["entry"])
>>> renewal_process = RenewalProcess(weibull)

```

Each simulated asset lifetime is a random draw, so the number of renewals observed by time
\(t\), written \(N(t)\), is itself random and traces out a step function that jumps
by one at every replacement.

The quantity of interest for planning purposes isn't one random realization, but its
average across the whole fleet: the expected number of renewals up to time \(t\), the
**renewal function** \(m(t) = \mathbb{E}[N(t)]\). It's obtained by solving the renewal
equation

\[
    m(t) = F_1(t) + \int_0^t m(t-x) \mathrm{d}F(x)
\]

where \(F\) is the cumulative distribution function of the time between two renewals,
and \(F_1\) is the cumulative distribution function of the *first* renewal (the two
differ if the process is "delayed", e.g. the first asset wasn't new when observation
started). Solving it numerically over a timeline:

```python
>>> timeline, m = renewal_process.renewal_function(100., 5)
>>> timeline
array([  0.,  25.,  50.,  75., 100.])
>>> m
array([0.        , 0.01236231, 0.15251764, 0.53746995, 0.96142435])

```

After 100 time units, this fleet is expected to have gone through just under one full
replacement per asset on average, consistent with the Weibull fit's mean lifetime:

```python
>>> round(weibull.mean(), 6)
np.float64(73.260749)

```

The rate at which renewals accumulate has a limit, given by the elementary renewal theorem:
an asset lasting \(\mathbb{E}[X]\) on average is replaced once every \(\mathbb{E}[X]\)
units of time, so over a long horizon

\[
    \lim_{t \to \infty} \frac{m(t)}{t} = \frac{1}{\mathbb{E}[X]}
\]

This is where the \(1/\mathbb{E}[X]\) used throughout the maintenance pages comes from,
and it is the same quantity the run-to-failure cost per unit of time is built on (see
[Run-to-failure policy](run_to_failure.md)). Early in the timeline the process sits below
that rate, because the first replacements haven't had time to accumulate:

```python
>>> round(float(m[-1] / 100.), 6)
0.009614
>>> round(float(1 / weibull.mean()), 6)
0.01365

```

Pushing the horizon out makes the convergence visible:

```python
>>> long_timeline, long_m = renewal_process.renewal_function(5000., 501)
>>> round(float(long_m[-1] / 5000.), 6)
0.013559

```

This is the mechanism that everything else in the maintenance-policy layer is built on: a
policy replaces "renewal" with "renewal *and its cost*" (see
[The reward and discounting framework](reward_framework.md)) to
go from "how many replacements do I expect" to "how much will they cost".

The one exception is the one-cycle policies (`OneCycleRunToFailurePolicy` and
`OneCycleAgeReplacementPolicy`, see [Run-to-failure policy](run_to_failure.md) and
[Preventive age replacement policy](preventive_age_replacement.md)). Since they stop at the
first replacement, there is no sequence of renewals to solve for: no renewal equation is
involved, and their costs are obtained by integrating the reward directly against the
lifetime distribution of the single cycle.
