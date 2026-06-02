Non Homogeneous Poisson Processes (NHPP)
========================================

Before diving into Non Homogeneous Poisson Processes (NHPP), let's first recall
what a "simple" (or homogeneous) Poisson process is.

The simple Poisson process
---------------------------

A Poisson process is a **counting process**: it counts events that occur at a
**fixed rate** :math:`\lambda`. Concretely:

- If an asset breaks down twice a year on average, we say it follows a Poisson
  process at rate :math:`\lambda = 2` per year.
- Events occur "at random" in time: they are independent of one another and
  their pace never changes (we say the increments are *stationary*).

The key word here is **fixed**: regardless of the asset's age or how many
failures have already happened, the risk of a new failure over the next hour
stays the same.

Why do we need Non Homogeneous Poisson Processes ?
--------------------------------------------------

Let :math:`N(t)` be the **total number of repairs** carried out on a single asset
up to time :math:`t`. We might be tempted to model this as a simple
Poisson process, assuming repairs always happen at the same pace.

In practice, this is almost never the case for aging assets. The repair pace
is **not stationary**: the older the asset and the more repairs it has already
undergone, the more likely a new intervention becomes. The pace *accelerates*
over time. This is exactly what an NHPP describes.

The only difference between a simple Poisson process and an NHPP lies in the rate:

- simple Poisson: constant rate, :math:`\lambda`;
- NHPP: time-varying rate, :math:`\lambda(t)`.

This function :math:`\lambda(t)` is called the **intensity function**. It can be
read as "the instantaneous pace of repairs at age :math:`t`":

- an **increasing** intensity reflects an asset that ages and wears out (the most
  common case in maintenance);
- a **constant** intensity recovers the simple Poisson process;
- a **decreasing** intensity would correspond to equipment that becomes more
  reliable over time (it can be early-life defects being resolved).

A concrete example: SF6 leaks
-----------------------------

Consider a gas-insulated compact substation, insulated with SF6. 
When a seal starts to degrade, gas leaks out and a technician
must **top up the SF6** to restore the nominal pressure.

This kind of intervention is a **minimal repair**:

- it fixes the symptom — the gas level returns to normal;
- but it does not replace the worn seal. The equipment therefore restarts in an
  *"as bad as old"* state, not in a brand-new state.

As a result, the seal keeps degrading. The top-ups, several years apart at first,
eventually come back every year, then every six months. If you plotted the
cumulative number of top-ups against time, the curve would not be a straight line
(constant rate) but a curve that **bends upward** more and more (increasing
rate). In all these cases, the asset is repaired without being rejuvenated, and the 
pace of interventions accelerates with age.

Diving into the code
--------------------

The structure of the NHPP object in ReLife is described below. It expects a list of 
times and a list of asset IDs corresponding to each of these times. If an asset never 
had a repair, then it should appear only once. Otherwise, it should appear one time 
for each repair. Also note that the ``Weibull()`` parametric function is not fitted 
and directly given to the ``NonHomogeneousPoissonProcess`` object.

.. code-block:: python

    >>> from relife.lifetime_models import Weibull
    >>> from relife.stochastic_processes import NonHomogeneousPoissonProcess
    >>> import numpy as np
    >>> nhpp = NonHomogeneousPoissonProcess(Weibull())
    >>> nhpp.fit(np.array([11., 13., 21., 25., 27.]), ("AB2", "CX13", "AB2", "AB2", "CX13"))
