# SSC Pure-Field Consumption

This page records how the current SSC field-first controller consumes LRPC scoring. It is a downstream-specific reference page, not a canonical LRPC runtime contract. Read it when you need to reconstruct the current SSC objective, the obstacle semantics, and the exact way MPPI turns LRPC ordering into control.

## Scope

The scope of this page is the current SSC pure-field path. In that path:

- LRPC stays a pure reference-path cost surface
- obstacle information does not attenuate or rewrite the LRPC value itself
- costmap + footprint checks classify trajectories as feasible or infeasible before field ranking
- only safe trajectories are ranked by pure field reward

This is a downstream control policy. It does not replace the base LRPC contract described in [Runtime Evaluation Contract](./runtime_evaluation_contract.md) and [Layer Composition](./layer_composition.md).

## Why SSC uses this structure

SSC wants LRPC to remain the main ordering signal. The controller should basically follow the field.

At the same time, SSC does not want a soft tradeoff where a high-field trajectory can still win by paying an obstacle penalty. In practice that can produce near-obstacle override, late stopping, or unstable left-right switching when the optimizer sees several trajectories with similar field values.

The current SSC policy therefore separates the roles:

- LRPC answers which safe states and trajectories are more preferred
- obstacle checks answer whether a trajectory is admissible at all

That separation keeps LRPC pure and makes the overwrite rule explicit: unsafe trajectories are discarded before ranking.

## Data path

The current SSC field-first path is:

1. `/planned_path_detailed.path_data.nodes[*].utm_info` supplies the progression guide.
2. `score_field_adapter` projects ego onto that guide and keeps a forward-biased local slice.
3. The adapter builds a planner lookup cache over the local query window.
4. MPPI samples rollout trajectories in SSC state space.
5. Each trajectory is checked against the costmap with footprint samples.
6. Infeasible trajectories are removed from effective ranking by assigning a large sentinel cost.
7. Safe trajectories are scored only with the pure LRPC lookup.
8. MPPI updates the nominal control sequence from the weighted sample population.

## Current local context and operating point

The current SSC field-first baseline uses this local context:

- local window size: `10 m x 10 m`
- window forward offset: `2.5 m`
- grid resolution: `0.25 m`
- lookup cache rebuild rate: `5 Hz`
- forward local path margin: `1.0 m`
- rear local path margin: `1.0 m`

The current optimizer operating point is:

- control frequency: `12 Hz`
- batch size: `384`
- time steps: `30`
- model dt: `0.1 s`
- temperature: `1.0`
- action regularization weight: `0.08`
- derivative-control noise std: `[0.25, 0.15]`
- action smoothness weights: `[0.6, 1.2]`
- max linear velocity: `1.5 m/s`
- min tracking speed in field-first mode: `0.50 m/s`

## Pure field reward

Let `f_t` be the LRPC value queried from `progression_tilted` at rollout sample `t`:

`f_t = progression_tilted(x_t, y_t)`

The SSC pure-field critic does not modify `f_t` with obstacle attenuation.

For one trajectory, SSC builds three reward terms:

### Positive progress

`R_pos = sum_t max(f_{t+1} - f_t, 0)`

This rewards monotone movement toward higher-field regions.

### Net progress

`R_net = f_T - f_0`

This rewards end-to-end field gain even when the gain is not strictly monotone at every step.

### Weighted field mean

SSC also keeps a small absolute-field support term:

`R_mean = sum_t \bar{w}_t f_t`

where the temporal weights are linearly increased from a bias floor `b = 0.3` to `1.0` and normalized to sum to `1`.

### Final field reward

The full pure-field reward is:

`R_field = R_pos + R_net + 0.10 * R_mean`

With the current baseline, reward normalization is disabled. SSC therefore uses the raw reward scale directly.

For feasible trajectories, the field critic cost is:

`J_field = -w_field * R_field`

where the current field weight is `w_field = 4.0`.

## Feasibility rule

Obstacle handling is footprint-based and costmap-based.

For each rollout pose, SSC samples the vehicle footprint against the current costmap and reads the worst local cell cost:

`c_t = max_{p in footprint_t} costmap(p)`

A trajectory is feasible only if all sampled footprint points stay inside the map and remain below the unsafe threshold:

`trajectory is feasible iff for all t: c_t < 70 and sample_t is inside map`

The current thresholds are:

- `cost < 70`: feasible
- `70 <= cost < 90`: unsafe, therefore infeasible
- `cost >= 90`: occupied, therefore infeasible
- `map outside`: infeasible

The important point is that unsafe and occupied trajectories are not ranked against safe trajectories. They are treated as outside the admissible set.

## Sentinel cost for infeasible trajectories

The generic SSC MPPI optimizer expects a scalar cost for every sample. To preserve that optimizer structure without adding a separate boolean filtering API, the field-first critic assigns a large sentinel cost to infeasible trajectories:

`J_fieldfirst = J_inf` if the trajectory is infeasible

`J_fieldfirst = J_field` if the trajectory is feasible

In the current implementation, `J_inf` is a large constant on the order of `1e6` or above, and the stop policy also treats that region as infeasible evidence.

This is why obstacle semantics are overwrite semantics in practice even though the optimizer still consumes scalar costs internally.

## MPPI control update

SSC uses derivative control samples, then integrates them into action sequences.

Let the sampled derivative controls be `U_t = [u_v,t, u_delta,t]`. SSC integrates them into actions `A_t = [v_t, delta_t]`:

`A_0 = a_0 + U_0 * dt`

`A_t = A_{t-1} + U_t * dt`

Then SSC clamps the resulting `v_t` and `delta_t` to the active action bounds.

For each sample `i`, MPPI evaluates:

`J_total,i = J_fieldfirst,i + lambda_action * J_action,i`

where the action smoothness term is:

`J_action = sum_t (omega_v * (v_t - v_{t-1})^2 + omega_delta * (delta_t - delta_{t-1})^2)`

The sample weights are then computed with a softmin:

`beta = min_i J_total,i`

`pi_i = exp(-(J_total,i - beta) / temperature) / sum_j exp(-(J_total,j - beta) / temperature)`

If the sampled derivative-control noise is `epsilon_i`, the nominal derivative-control sequence update is:

`Delta U = sum_i pi_i * epsilon_i`

`U_nominal <- U_nominal + Delta U`

This matters for interpretation. SSC MPPI does not pick one exact winning trajectory and copy its controls. It updates the nominal control sequence from a weighted sample population around the current nominal sequence.

## Stop policy

The field-first stop logic follows the same admissible-set idea.

SSC publishes zero command when either condition holds:

- no feasible trajectory remains in the current rollout batch
- the best sample cost already sits inside the infeasible sentinel band

Goal completion remains separate from field ranking. The current controller still stops when the robot is within the terminal distance threshold of the final planned-path node.

## Visualization policy

The score-field mesh shown in SSC visualization is pure LRPC score, not obstacle-masked LRPC score.

The mesh is produced from the same prepared planner lookup and the same bilinear lookup operator that the controller uses for scoring. Obstacles are not mixed into the color values. This keeps the display interpretable:

- the mesh shows the pure reference-path cost surface
- costmap/obstacle logic decides feasibility separately

## Relation to the LRPC contract

This SSC path is intentionally downstream-specific.

- LRPC still provides a whole-space preference ordering
- obstacle, rule, and dynamic layers remain conceptually separate from the reference-path cost model
- SSC chooses to consume that reference-path cost model with a safe-set-first MPPI policy

Another downstream consumer could choose a different policy. This page records the current SSC choice. It does not redefine the canonical LRPC runtime semantics for every consumer.
