# Current Implementation Formula Reference

이 문서는 `driving-preference-field`의 **현재 구현 수식**을 모아 둔 reading 자료다.

- canonical truth를 대신하지 않는다
- 구현과 README가 어떤 current formula를 쓰는지 빠르게 대조하는 용도다
- exact formula가 바뀌면 이 문서와 README, 코드 주석을 같이 갱신한다

## 1. Progression Surface

구현 경로:

- `src/driving_preference_field/progression_surface.py`
- `src/driving_preference_field/channels.py`

현재 progression은 smooth skeleton anchor를 control point로 쓰는 Gaussian-blended coordinate field다.

- visible guide endpoint는 semantic start/end가 아니라 virtual continuation으로 처리한다
- support/alignment는 주형을 만들지 않는 weak secondary modulation이다

anchor별 local coordinate:

```math
\tau_i = \langle p - a_i,\ t_i \rangle
```

```math
\nu_i = \langle p - a_i,\ n_i \rangle
```

```math
r_i = w_i^{guide}\, c_i \exp \left(
-\frac{1}{2}\left[\left(\frac{\tau_i}{\sigma_t}\right)^2 + \left(\frac{\nu_i}{\sigma_n}\right)^2\right]
\right)
```

```math
\bar{w}_i = \frac{r_i}{\sum_j r_j}
```

blended coordinate:

```math
\hat{s} = \sum_i \bar{w}_i s_i
```

```math
\hat{n} = \sqrt{\sum_i \bar{w}_i \nu_i^2}
```

```math
\hat{t} = \mathrm{normalize}\left(\sum_i \bar{w}_i t_i\right)
```

longitudinal frame:

```math
u_{\text{local\_absolute}} = \mathrm{clip}\left(
\frac{\hat{s} - s_{\min}^{ext}}{s_{\max}^{ext} - s_{\min}^{ext}}, 0, 1
\right)
```

```math
u_{\text{ego\_relative}} = \mathrm{clip}\left(
\frac{\max(0,\ \hat{s} - \hat{s}_{ego})}{\text{lookahead}},\ 0,\ 1
\right)
```

longitudinal family:

- `linear`

```math
L(u) = u
```

- `inverse`

```math
L(u) = \frac{(1+\alpha)u}{1+\alpha u}
```

- `power`

```math
L(u) = u^\alpha
```

- `tanh`

```math
L(u) = \frac{\tanh(\alpha u)}{\tanh(\alpha)}
```

transverse family:

- `inverse`

```math
T(r) = \frac{1}{1+\beta r}
```

- `power`

```math
T(r) = \frac{1}{1+r^\beta}
```

- `exponential`

```math
T(r) = e^{-\beta r}
```

secondary modulation:

```math
\text{alignment\_mod} = 0.95 + 0.05 \max(0,\ \langle h,\ \hat{t} \rangle)
```

```math
\text{support\_mod} = 0.95 + 0.05 \ \mathrm{clip}\left(
\frac{\sum_i \bar{w}_i \min(c_i,\ c_{\max})}{c_{\max}},\ 0,\ 1
\right)
```

final progression score:

```math
\text{progression\_tilted}(p) =
\text{support\_mod}\cdot\text{alignment\_mod}\cdot
\left(T(\hat{n} / \text{transverse\_scale}) + g \cdot L(u)\right)
```

의도:

- 같은 progression slice에서는 center-high transverse profile을 만든다
- stronger longitudinal에서는 farther-ahead ordering을 만든다
- branch guide도 같은 anchor pool로 읽어서 gap을 비우지 않는다

## 2. Interior / Boundary

구현 경로:

- `src/driving_preference_field/channels.py`

drivable region 안쪽일 때 boundary margin score:

```math
\text{interior\_boundary}(p) =
\gamma \cdot \mathrm{clip}\left(\frac{d_{\partial \Omega}(p)}{\text{margin\_scale}},\ 0,\ 1\right)
```

의도:

- 같은 region 안에서 boundary보다 interior가 더 높게 읽히게 한다

## 3. Branch Continuity

구현 경로:

- `src/driving_preference_field/channels.py`

guide별 candidate score:

```math
\text{alignment}_i = \max(0,\ \langle h,\ t_i \rangle)\cdot w_{align}
```

```math
\text{proximity}_i = e^{-d_i / \lambda}
```

```math
\text{score}_i =
g \cdot w_i^{guide} \cdot \min(c_i,\ c_{\max}) \cdot \text{proximity}_i \cdot \text{alignment}_i
```

```math
\text{continuity\_branch}(p) = \max_i \text{score}_i
```

의도:

- branch/merge 쪽에서 더 aligned하고 continuity가 높은 흐름을 따로 읽게 한다

## 4. Exception Layers

구현 경로:

- `src/driving_preference_field/exception_layers.py`

soft burden:

```math
b_{\text{soft}}(p, R) =
\begin{cases}
\text{severity}(R), & p \in R \\
\text{severity}(R)\exp\left(\frac{d_{\text{signed}}(p, R)}{\rho_R}\right), & p \notin R
\end{cases}
```

hard hit:

```math
b_{\text{hard}}(p, R) = \text{hard}(R) \land (p \in R)
```

channel별 합:

```math
\text{safety\_soft}(p) = \sum_{R \in \mathcal{S}} b_{\text{soft}}(p, R)
```

```math
\text{rule\_soft}(p) = \sum_{R \in \mathcal{R}} b_{\text{soft}}(p, R)
```

```math
\text{dynamic\_soft}(p) = \sum_{R \in \mathcal{D}} b_{\text{soft}}(p, R)
```

## 5. State / Trajectory Composition

구현 경로:

- `src/driving_preference_field/evaluator.py`

state base total:

```math
\text{base\_preference\_total}(p) =
\text{progression\_tilted}(p) +
\text{interior\_boundary}(p) +
\text{continuity\_branch}(p)
```

state soft total:

```math
\text{soft\_exception\_total}(p) =
\text{safety\_soft}(p) +
\text{rule\_soft}(p) +
\text{dynamic\_soft}(p)
```

trajectory totals:

```math
\text{trajectory\_base\_preference\_total} = \sum_k \text{base\_preference\_total}(p_k)
```

```math
\text{trajectory\_soft\_exception\_total} = \sum_k \text{soft\_exception\_total}(p_k)
```

ordering key:

```math
(\text{hard\_violation\_count},\ \text{trajectory\_soft\_exception\_total},\ -\text{trajectory\_base\_preference\_total})
```

의도:

- hard violation이 가장 먼저 trajectory를 밀어낸다
- 그다음 soft burden이 적은 trajectory를 선호한다
- 그다음 higher-is-better base preference가 높은 trajectory를 선호한다
