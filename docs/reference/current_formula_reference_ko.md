# Current Formula Reference

- 역할: reference
- 현재성: current implementation
- 대상 독자: contributor, maintainer
- 다음으로 읽을 문서: [06. Runtime Contract](./runtime_evaluation_contract_ko.md)

이 문서는 `driving-preference-field`의 **현재 구현 수식**을 한 곳에 정리한 reference다.

- canonical truth를 대신하지 않는다
- 현재 구현과 runtime contract를 대조하는 용도다
- exact formula가 바뀌면 이 문서와 관련 코드 주석, README를 함께 갱신한다

## 공통 표기

- 점: \(p \in \mathbb{R}^2\)
- 벡터: \(v \in \mathbb{R}^2\)
- 내적: \(\langle a, b \rangle\)
- 정규화: \(\mathrm{normalize}(v) = v / \lVert v \rVert\)
- 클립: \(\mathrm{clip}(x, a, b) = \min(\max(x, a), b)\)

## Progression Surface

구현 경로:

- `src/driving_preference_field/progression_surface.py`
- `src/driving_preference_field/channels.py`
- `src/driving_preference_field/field_runtime.py`

현재 progression은 smooth skeleton anchor를 control point로 쓰는 Gaussian-blended coordinate field다.

- visible guide endpoint는 semantic start/end가 아니라 virtual continuation으로 처리한다
- support/alignment는 주형을 만들지 않는 weak secondary modulation이다

### Anchor local coordinates

```math
\tau_i = \langle p - a_i,\ t_i \rangle
```

```math
\nu_i = \langle p - a_i,\ n_i \rangle
```

### Gaussian anchor weights

```math
r_i = w_i^{guide}\, c_i \exp \left(
-\frac{1}{2}\left[\left(\frac{\tau_i}{\sigma_t}\right)^2 + \left(\frac{\nu_i}{\sigma_n}\right)^2\right]
\right)
```

```math
\bar{w}_i = \frac{r_i}{\sum_j r_j}
```

현재 구현:

```math
\sigma_t=\max(0.40,\ L\cdot \text{lookahead\_scale}\cdot 0.35)
```

```math
\sigma_n=\max(0.35,\ \text{transverse\_scale}\cdot 1.50)
```

### Blended coordinate

```math
\hat{s} = \sum_i \bar{w}_i s_i
```

```math
\hat{n} = \sqrt{\sum_i \bar{w}_i \nu_i^2}
```

```math
\hat{t} = \mathrm{normalize}\left(\sum_i \bar{w}_i t_i\right)
```

### Longitudinal frame

local absolute:

```math
u_{\text{local\_absolute}} = \mathrm{clip}\left(
\frac{\hat{s} - s_{\min}^{ext}}{s_{\max}^{ext} - s_{\min}^{ext}}, 0, 1
\right)
```

ego relative:

```math
u_{\text{ego\_relative}} = \mathrm{clip}\left(
\frac{\max(0,\ \hat{s} - \hat{s}_{ego})}{\text{lookahead}},\ 0,\ 1
\right)
```

### Longitudinal families

```math
L_{\text{linear}}(u)=u
```

```math
L_{\text{inverse}}(u)=\frac{(1+\alpha)u}{1+\alpha u}
```

```math
L_{\text{power}}(u)=u^{\alpha}
```

```math
L_{\tanh}(u)=\frac{\tanh(\alpha u)}{\tanh(\alpha)}
```

### Transverse families

정의:

```math
r=\frac{\hat{n}}{s_t},\quad s_t=\text{transverse\_scale}
```

```math
T_{\text{exp}}(r)=e^{-\beta r}
```

```math
T_{\text{inv}}(r)=\frac{1}{1+\beta r}
```

```math
T_{\text{pow}}(r)=\frac{1}{1+r^{\beta}}
```

### Secondary modulation

```math
\text{alignment\_mod} = 0.95 + 0.05\,\max(0,\langle h,\hat{t}\rangle)
```

```math
\text{support\_mod} = 0.95 + 0.05\,\mathrm{clip}\left(
\frac{\sum_i \bar{w}_i\min(c_i,c_{\max})}{c_{\max}},\ 0,\ 1
\right)
```

### Final progression score

```math
\text{progression\_tilted}(p)=\text{support\_mod}\cdot\text{alignment\_mod}\cdot\left(T(r)+g\cdot L(u)\right)
```

의도:

- 같은 progression slice에서는 center-high transverse profile을 만든다
- stronger longitudinal에서는 farther-ahead ordering을 만든다
- branch guide도 같은 anchor pool로 읽어서 gap을 비우지 않는다
- downstream consumer는 이 수식을 직접 복제하기보다 cached runtime query layer를 소비한다

## Interior / Boundary

구현 경로:

- `src/driving_preference_field/channels.py`

```math
\text{interior\_boundary}(p)=\gamma\cdot\mathrm{clip}\left(\frac{d_{\partial\Omega}(p)}{\text{margin\_scale}},\ 0,\ 1\right)
```

```math
\text{interior\_signed\_margin}(p)=\max_{\Omega}\ d_{\text{signed}}(p,\Omega)
```

## Branch Continuity

```math
\text{alignment}_i = \max(0,\langle h, t_i\rangle)\cdot w_{align}
```

```math
\text{proximity}_i = e^{-d_i/\lambda}
```

```math
\text{score}_i = g\cdot w_i^{guide}\cdot\min(c_i,c_{\max})\cdot\text{proximity}_i\cdot\text{alignment}_i
```

```math
\text{continuity\_branch}(p)=\max_i \text{score}_i
```

## Exception Layers

```math
b_{\text{soft}}(p,R)=
\begin{cases}
\text{severity}(R), & p\in R\\
\text{severity}(R)\exp\left(\frac{d_{\text{signed}}(p,R)}{\rho_R}\right), & p\notin R
\end{cases}
```

```math
b_{\text{hard}}(p,R)=\text{hard}(R)\land(p\in R)
```

```math
\text{safety\_soft}(p)=\sum_{R\in\mathcal{S}} b_{\text{soft}}(p,R)
```

```math
\text{rule\_soft}(p)=\sum_{R\in\mathcal{R}} b_{\text{soft}}(p,R)
```

```math
\text{dynamic\_soft}(p)=\sum_{R\in\mathcal{D}} b_{\text{soft}}(p,R)
```

## State / Trajectory Composition

```math
\text{base\_preference\_total}(p)=
\text{progression\_tilted}(p)+
\text{interior\_boundary}(p)+
\text{continuity\_branch}(p)
```

```math
\text{soft\_exception\_total}(p)=
\text{safety\_soft}(p)+
\text{rule\_soft}(p)+
\text{dynamic\_soft}(p)
```

```math
\text{trajectory\_base\_preference\_total} = \sum_k \text{base\_preference\_total}(p_k)
```

```math
\text{trajectory\_soft\_exception\_total} = \sum_k \text{soft\_exception\_total}(p_k)
```
