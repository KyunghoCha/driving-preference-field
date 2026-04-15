# Current Formula Reference

이 문서는 현재 구현 수식을 한 곳에 모아 둔 reference다. canonical 정의를 대신하지 않고, runtime contract와 현재 구현을 대조할 때 사용한다. 구현 파일을 읽기 전에 전체 계산 흐름을 빠르게 잡고 싶을 때 이 문서를 먼저 보면 된다.

## 이 문서를 읽는 방법

현재 구현 수식은 다섯 덩어리로 읽는 것이 가장 빠르다.

1. progression surface가 local map 위에 어떤 좌표장을 만드는가
2. interior / boundary가 어떤 보조 선호를 더하는가
3. branch continuity가 continuation 차이를 어떻게 읽는가
4. exception layer가 soft / hard burden을 어떻게 만든는가
5. state / trajectory 단계에서 위 값을 어떻게 합치는가

각 섹션은 수식 자체보다 먼저 “왜 이 수식이 필요한가”를 한두 문장으로 적는다. 목표는 수식만 나열하는 것이 아니라, 현재 구현이 어떤 계산 순서로 움직이는지 복원 가능하게 만드는 것이다.

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

progression surface는 local map 전체에 진행 좌표와 횡방향 좌표를 동시에 부여하기 위해 필요하다. 현재 구현은 smooth skeleton anchor를 control point로 쓰는 Gaussian-blended coordinate field를 사용한다. visible guide endpoint는 virtual continuation으로 처리하고, support/alignment는 weak secondary modulation으로 남긴다.

### Anchor local coordinates

각 anchor 기준의 local tangent / normal 좌표를 먼저 계산한다. 이 좌표가 뒤에서 blended coordinate를 만드는 기본 재료가 된다.

```math
\tau_i = \langle p - a_i,\ t_i \rangle
```

```math
\nu_i = \langle p - a_i,\ n_i \rangle
```

### Gaussian anchor weights

모든 anchor를 winner처럼 고르지 않고, Gaussian weight로 부드럽게 섞는다. 이 단계가 abrupt jump를 줄이고 whole-fabric surface를 만드는 핵심이다.

```math
r_i = w_i^{guide}\, c_i \exp \left(
-\frac{1}{2}\left[\left(\frac{\tau_i}{\sigma_t}\right)^2 + \left(\frac{\nu_i}{\sigma_n}\right)^2\right]
\right)
```

```math
\bar{w}_i = \frac{r_i}{\sum_j r_j}
```

현재 구현 상수:

```math
\sigma_t=\max(0.40,\ L\cdot \text{lookahead\_scale}\cdot 0.35)
```

```math
\sigma_n=\max(0.35,\ \text{transverse\_scale}\cdot 1.50)
```

### Blended coordinate

이 단계에서 `s_hat`, `n_hat`, `t_hat`를 만든다. 이후 longitudinal / transverse 성분은 이 blended coordinate를 기준으로 계산된다.

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

longitudinal 성분은 같은 좌표장 위에서도 어떤 frame으로 progress를 읽느냐에 따라 달라진다. 현재 구현은 local absolute와 ego relative 두 frame을 모두 지원한다.

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

`L(u)`는 얼마나 앞으로 갔는지에 대한 보상을 만든다. family에 따라 앞쪽 gain이 커지는 속도와 포화 방식이 달라진다.

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

`T(r)`는 중심에서 얼마나 벗어났는지에 대한 형태를 만든다. family와 decay에 따라 center-high profile의 폭과 날카로움이 바뀐다.

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

support와 alignment는 본체 shape를 만들기보다 과확신을 줄이고 명백히 비양립한 방향만 약하게 누르는 역할을 맡는다.

```math
\text{alignment\_mod} = 0.95 + 0.05\,\max(0,\langle h,\hat{t}\rangle)
```

```math
\text{support\_mod} = 0.95 + 0.05\,\mathrm{clip}\left(
\frac{\sum_i \bar{w}_i\min(c_i,c_{\max})}{c_{\max}},\ 0,\ 1
\right)
```

### Final progression score

최종 progression score는 transverse profile과 longitudinal gain을 더한 뒤, weak modulation을 곱해 만든다. 이 score가 `progression_tilted` 채널의 현재 구현이다.

```math
\text{progression\_tilted}(p)=\text{support\_mod}\cdot\text{alignment\_mod}\cdot\left(T(r)+g\cdot L(u)\right)
```

의도:

- 같은 progression slice에서는 center-high transverse profile을 만든다.
- stronger longitudinal에서는 farther-ahead ordering을 만든다.
- branch guide도 같은 anchor pool로 읽어서 gap을 비우지 않는다.
- downstream consumer는 이 수식을 직접 복제하기보다 cached runtime query layer를 소비한다.

## Interior / Boundary

interior / boundary 성분은 progression 본체와 별도로, 주행 가능한 구조 안에서 중심 쪽과 경계 쪽을 구분하는 보조 선호를 만든다.

구현 경로:

- `src/driving_preference_field/channels.py`

```math
\text{interior\_boundary}(p)=\gamma\cdot\mathrm{clip}\left(\frac{d_{\partial\Omega}(p)}{\text{margin\_scale}},\ 0,\ 1\right)
```

```math
\text{interior\_signed\_margin}(p)=\max_{\Omega}\ d_{\text{signed}}(p,\Omega)
```

## Branch Continuity

branch continuity는 여러 continuation이 있을 때 어떤 흐름이 더 자연스럽게 이어지는지 읽기 위해 필요하다. proximity와 heading 정합을 함께 써서 continuation score를 만든다.

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

exception layer는 base field와 다른 층이다. safety / rule / dynamic burden을 soft와 hard로 분리해 계산하고, base preference로 상쇄되지 않게 둔다.

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

최종 state / trajectory score는 각 층의 결과를 합쳐 읽는다. base preference와 soft exception은 별도로 유지되고, trajectory에서는 horizon 전체 누적으로 해석한다.

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
