Examples
=========

Worked examples following the order a real reliability study runs in: assemble the records,
look at them without assumptions, commit to a model, then turn it into a decision. They use
ReLife's :doc:`../user_guides/datasets`, which are actual RTE-France power-grid equipment
data, with all the awkwardness that implies. The theory behind each step is in the
:doc:`../user_guides/index`.

Each example also flags the mistakes that are easy to make at that step, because most of
them are silent: they don't raise, they just move the answer.

.. toctree::
    :maxdepth: 1

    non_parametric_estimation
    distributions_fitting
    regression_modeling
    semi_parametric_cox
    maintenance_policy_costs

Which method for which situation
----------------------------------

The four modeling approaches are not competing implementations of the same thing. They
answer different questions and carry different obligations:

.. list-table::
    :header-rows: 1
    :widths: 25 40 35

    * - Method
      - Use it when
      - Cannot do
    * - Kaplan-Meier / Nelson-Aalen (:doc:`non_parametric_estimation`)
      - You want the fleet's actual survival with no assumed shape, as a first look and as
        the yardstick every fitted model is checked against
      - Extrapolate past the last observation; feed a maintenance policy
    * - Parametric distribution (:doc:`distributions_fitting`)
      - You need a smooth curve, a mean lifetime, or a model to plug into a policy
      - Represent a fleet whose assets face different stresses
    * - Parametric regression (:doc:`regression_modeling`)
      - Assets differ in ways you measured, and you need per-asset predictions or
        extrapolation
      - Be trusted when a covariate falls outside the observed range
    * - Cox regression (:doc:`semi_parametric_cox`)
      - You want covariate effects without committing to a baseline shape
      - Extrapolate; feed a maintenance policy

The practical rule: start non-parametric to see what the data says, go parametric only when
you need something the data alone can't give you (a mean, a tail, a decision), and add
covariates only when the fleet is genuinely heterogeneous and you have the measurements to
describe how.
