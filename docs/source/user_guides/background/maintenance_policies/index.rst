Maintenance policies
======================

How to turn a fitted lifetime model into a maintenance decision: the policies ReLife
provides, the renewal-process theory and reward framework they're built on, and how their
costs are computed.

Each policy comes in two flavours: a *renewal* one, where the asset is replaced indefinitely
(the right model for planning a fleet over the long run), and a *one-cycle* one, which stops
at the first replacement (the right model for a decision about the asset currently in
service). The two share the same API but annualize costs over different horizons — see
:doc:`cost_calculations`.

.. toctree::
    :maxdepth: 1

    run_to_failure
    preventive_age_replacement
    renewal_theory
    reward_framework
    cost_calculations
