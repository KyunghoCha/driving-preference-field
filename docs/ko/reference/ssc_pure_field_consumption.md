# SSC Pure-Field Consumption

이 문서는 현재 SSC field-first controller가 LRPC scoring을 어떻게 소비하는지 기록한다. 이는 downstream-specific reference이며 canonical LRPC runtime contract가 아니다. 현재 SSC objective, obstacle semantics, MPPI가 LRPC ordering을 control로 바꾸는 방식을 복원해야 할 때 읽는다.

## Scope

이 문서의 범위는 현재 SSC pure-field path다. 이 경로에서는 다음을 전제로 한다.

- LRPC는 순수 reference-path cost surface로 남는다.
- obstacle 정보는 LRPC 값 자체를 attenuate하거나 rewrite하지 않는다.
- costmap + footprint check가 field ranking 전에 trajectory를 feasible/infeasible로 분류한다.
- safe trajectory만 pure field reward로 ranking한다.

이는 downstream control policy다. [Runtime Evaluation Contract](./runtime_evaluation_contract.md)와 [Layer Composition](./layer_composition.md)에 적힌 base LRPC contract를 대체하지 않는다.

## Why SSC uses this structure

SSC는 LRPC가 주요 ordering signal로 남기를 원한다. controller는 기본적으로 그 surface를 따라야 한다.

동시에 SSC는 높은 field 값이 obstacle penalty를 지불하고도 이기는 soft tradeoff를 원하지 않는다. 실제로 이런 구조는 obstacle 근처 override, 늦은 정지, 비슷한 field 값을 가진 여러 trajectory 사이의 좌우 switching을 만들 수 있다.

현재 SSC policy는 그래서 역할을 분리한다.

- LRPC는 safe state와 safe trajectory 중 무엇이 더 나은지 답한다.
- obstacle check는 trajectory가 admissible한지 자체를 답한다.

이 분리는 LRPC를 pure하게 유지하고 overwrite rule을 명시적으로 만든다. unsafe trajectory는 ranking 전에 버린다.

## Data path

현재 SSC field-first path는 다음 순서다.

1. `/planned_path_detailed.path_data.nodes[*].utm_info`가 progression guide를 제공한다.
2. `score_field_adapter`가 ego를 guide에 project하고 forward-biased local slice를 유지한다.
3. adapter가 local query window 위에 planner lookup cache를 만든다.
4. MPPI가 SSC state space에서 rollout trajectory를 sample한다.
5. 각 trajectory를 costmap footprint sample로 검사한다.
6. infeasible trajectory는 큰 sentinel cost를 부여해 effective ranking에서 제거한다.
7. safe trajectory만 pure LRPC lookup으로 scoring한다.
8. MPPI가 weighted sample population으로 nominal control sequence를 갱신한다.

## Current local context and operating point

현재 SSC field-first baseline의 local context는 다음과 같다.

- local window size: `10 m x 10 m`
- window forward offset: `2.5 m`
- grid resolution: `0.25 m`
- lookup cache rebuild rate: `5 Hz`
- forward local path margin: `1.0 m`
- rear local path margin: `1.0 m`

현재 optimizer operating point는 다음과 같다.

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

`f_t`를 rollout sample `t`에서 `progression_tilted`로 query한 LRPC 값이라고 둔다.

`f_t = progression_tilted(x_t, y_t)`

SSC pure-field critic은 obstacle attenuation으로 `f_t`를 수정하지 않는다.

하나의 trajectory에 대해 SSC는 세 reward term을 만든다.

### Positive progress

`R_pos = sum_t max(f_{t+1} - f_t, 0)`

이는 더 높은 field region으로 단조롭게 움직이는 것을 보상한다.

### Net progress

`R_net = f_T - f_0`

이는 모든 step에서 gain이 단조롭지 않더라도 end-to-end field gain을 보상한다.

### Weighted field mean

SSC는 작은 absolute-field support term도 유지한다.

`R_mean = sum_t \bar{w}_t f_t`

여기서 temporal weight는 bias floor `b = 0.3`에서 `1.0`까지 선형 증가시키고 합이 `1`이 되도록 normalize한다.

### Final field reward

전체 pure-field reward는 다음과 같다.

`R_field = R_pos + R_net + 0.10 * R_mean`

현재 baseline에서는 reward normalization을 끈다. 그래서 SSC는 raw reward scale을 그대로 사용한다.

feasible trajectory의 field critic cost는 다음과 같다.

`J_field = -w_field * R_field`

현재 field weight는 `w_field = 4.0`이다.

## Feasibility rule

Obstacle handling은 footprint 기반이며 costmap 기반이다.

각 rollout pose에서 SSC는 vehicle footprint를 현재 costmap에 대해 sample하고 local cell cost의 최댓값을 읽는다.

`c_t = max_{p in footprint_t} costmap(p)`

모든 sampled footprint point가 map 안에 있고 unsafe threshold보다 낮을 때만 trajectory는 feasible하다.

`trajectory is feasible iff for all t: c_t < 70 and sample_t is inside map`

현재 threshold는 다음과 같다.

- `cost < 70`: feasible
- `70 <= cost < 90`: unsafe, therefore infeasible
- `cost >= 90`: occupied, therefore infeasible
- `map outside`: infeasible

중요한 점은 unsafe와 occupied trajectory가 safe trajectory와 ranking되지 않는다는 것이다. 이들은 admissible set 바깥으로 취급된다.

## Sentinel cost for infeasible trajectories

generic SSC MPPI optimizer는 모든 sample에 대해 scalar cost를 기대한다. 별도 boolean filtering API를 추가하지 않고 이 구조를 유지하기 위해 field-first critic은 infeasible trajectory에 큰 sentinel cost를 부여한다.

`J_fieldfirst = J_inf` if the trajectory is infeasible

`J_fieldfirst = J_field` if the trajectory is feasible

현재 구현에서 `J_inf`는 `1e6` 이상 수준의 큰 상수이며, stop policy도 이 영역을 infeasible evidence로 읽는다.

그래서 optimizer가 내부적으로 scalar cost를 소비하더라도 obstacle semantics는 실제로 overwrite semantics가 된다.

## MPPI control update

SSC는 derivative control sample을 사용하고 이를 action sequence로 적분한다.

sampled derivative control을 `U_t = [u_v,t, u_delta,t]`라고 두면, SSC는 이를 action `A_t = [v_t, delta_t]`로 적분한다.

`A_0 = a_0 + U_0 * dt`

`A_t = A_{t-1} + U_t * dt`

그 뒤 결과 `v_t`와 `delta_t`를 active action bound로 clamp한다.

각 sample `i`에 대해 MPPI는 다음을 평가한다.

`J_total,i = J_fieldfirst,i + lambda_action * J_action,i`

action smoothness term은 다음과 같다.

`J_action = sum_t (omega_v * (v_t - v_{t-1})^2 + omega_delta * (delta_t - delta_{t-1})^2)`

sample weight는 softmin으로 계산한다.

`beta = min_i J_total,i`

`pi_i = exp(-(J_total,i - beta) / temperature) / sum_j exp(-(J_total,j - beta) / temperature)`

sampled derivative-control noise가 `epsilon_i`라면 nominal derivative-control sequence update는 다음과 같다.

`Delta U = sum_i pi_i * epsilon_i`

`U_nominal <- U_nominal + Delta U`

이 점은 해석에 중요하다. SSC MPPI는 하나의 exact winning trajectory를 골라 control을 복사하지 않는다. 현재 nominal sequence 주변의 weighted sample population으로 nominal control sequence를 갱신한다.

## Stop policy

field-first stop logic도 같은 admissible-set 아이디어를 따른다.

SSC는 다음 중 하나가 참이면 zero command를 publish한다.

- 현재 rollout batch에 feasible trajectory가 남지 않는다.
- best sample cost가 이미 infeasible sentinel band 안에 있다.

Goal completion은 field ranking과 분리되어 있다. 현재 controller는 final planned-path node의 terminal distance threshold 안에 들어오면 여전히 정지한다.

## Visualization policy

SSC visualization에 표시되는 score-field mesh는 obstacle-masked LRPC score가 아니라 pure LRPC score다.

mesh는 controller scoring에 쓰는 prepared planner lookup과 같은 bilinear lookup operator에서 생성된다. obstacle은 color value에 섞이지 않는다. 이 방식은 display 해석을 명확하게 유지한다.

- mesh는 pure reference-path cost surface를 보여준다.
- costmap/obstacle logic은 feasibility를 별도로 결정한다.

## Relation to the LRPC contract

이 SSC path는 의도적으로 downstream-specific이다.

- LRPC는 여전히 whole-space ordering을 제공한다.
- obstacle, rule, dynamic layer는 reference-path cost model과 개념적으로 분리되어 있다.
- SSC는 safe-set-first MPPI policy로 reference-path cost model을 소비하기로 선택한다.

다른 downstream consumer는 다른 policy를 선택할 수 있다. 이 문서는 현재 SSC 선택을 기록한다. 모든 consumer의 canonical LRPC runtime semantics를 재정의하지 않는다.
