# 현재 구현 수식

이 문서는 현재 구현 수식을 한 곳에 모아 둔 reference다. canonical 철학을 정의하지 않고, 현재 코드가 어떤 계산 순서로 움직이는지 정리한다. runtime contract와 현재 구현을 대조할 때 사용하며, 구현 파일을 읽기 전에 전체 계산 흐름을 빠르게 잡고 싶을 때 이 문서를 먼저 보면 된다.

## 이 문서를 읽는 방법

현재 구현 수식은 다섯 덩어리로 읽는 것이 가장 빠르다.

1. progression surface가 local map 위에 어떤 좌표장을 만드는가
2. exception layer가 soft / hard burden을 어떻게 만드는가
3. current tiny evaluator가 state / trajectory 단계에서 progression 값을 어떻게 합치는가

각 섹션은 수식 자체보다 먼저 “왜 이 수식이 필요한가”를 한두 문장으로 적는다. 목표는 수식만 나열하는 것이 아니라, 현재 구현이 어떤 계산 순서로 움직이는지 복원 가능하게 만드는 것이다.

## 공통 표기

- 점: \(p \in \mathbb{R}^2\)
- 벡터: \(v \in \mathbb{R}^2\)
- 내적: \(\langle a, b \rangle\)
- 정규화: \(\mathrm{normalize}(v) = v / \lVert v \rVert\)
- 클립: \(\mathrm{clip}(x, a, b) = \min(\max(x, a), b)\)

## `progression surface` 계산

구현 경로:

- `src/driving_preference_field/progression_surface.py`
- `src/driving_preference_field/channels.py`
- `src/driving_preference_field/field_runtime.py`

progression surface는 local map 전체에 진행 좌표와 횡방향 좌표를 동시에 부여하기 위해 필요하다. 현재 구현은 progression guide마다 Gaussian anchor blend로 guide-local progress coordinate를 먼저 계산하고, 횡방향은 guide 중심 구조까지의 최단거리로 읽은 뒤, guide-local score를 만든 다음 guide 간 hard max envelope를 취한다. score는 dominant guide 기준으로 유지하지만, exported transverse는 near-tied guide candidate의 transverse term을 부드럽게 섞은 inspection channel로 내보낸다.

현재 구현에서 progression surface는 canonical 본체에 가장 가까운 층이다. progression-centered whole-space preference를 가장 직접적으로 근사하는 수식이 이 섹션에 있다.

### `guide-local` anchor 좌표

각 progression guide는 자기 anchor만으로 local tangent / normal 좌표를 만든다. 이 좌표가 뒤에서 guide-local `s_hat`, `n_hat`를 만드는 기본 재료가 된다.

```math
\tau_i = \langle p - a_i,\ t_i \rangle
```

```math
\nu_i = \langle p - a_i,\ n_i \rangle
```

### `guide-local` Gaussian weight

guide 안에서는 nearest winner를 고르지 않고, Gaussian weight로 anchor를 부드럽게 섞는다. 이 단계가 guide-local progress coordinate와 tangent를 만드는 핵심이다.

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

### `guide-local` 좌표

이 단계에서 guide-local `s_hat`, `t_hat`를 만든다. `n_hat`는 같은 dominant guide의 조밀한 중심 곡선과 짧은 continuation까지의 최단거리로 읽는다. 이후 longitudinal 성분은 dominant guide 기준 coordinate를 사용한다.

```math
\hat{s} = \sum_i \bar{w}_i s_i
```

```math
\hat{t} = \mathrm{normalize}\left(\sum_i \bar{w}_i t_i\right)
```

```math
\hat{n} = \min_{q \in C_g} \|p-q\|
```

여기서 `C_g`는 guide `g`를 조밀하게 재표본화한 중심 곡선과 짧은 virtual continuation이다.

### `guide-local` longitudinal frame

longitudinal 성분은 guide-local 좌표장 위에서도 어떤 frame으로 progress를 읽느냐에 따라 달라진다. 현재 구현은 local absolute와 ego relative 두 frame을 모두 지원한다.

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

### 종방향 families

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

### 횡방향 families

`T(r)`는 중심에서 얼마나 벗어났는지에 대한 형태를 만든다. family와 decay에 따라 center-high profile의 폭과 날카로움이 바뀐다.

정의:

```math
r_g=\frac{|\hat{n}_g|}{s_t},\quad s_t=\text{transverse\_scale}
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

### 보조 modulation

support와 alignment는 본체 shape를 만들기보다 과확신을 줄이고 명백히 비양립한 방향만 약하게 누르는 역할을 맡는다.

```math
\text{alignment\_mod} = 0.95 + 0.05\,\max(0,\langle h,\hat{t}\rangle)
```

```math
\text{support\_mod} = 0.95 + 0.05\,\mathrm{clip}\left(
\frac{\sum_i \bar{w}_i\min(c_i,c_{\max})}{c_{\max}},\ 0,\ 1
\right)
```

### 최종 progression score

각 guide-local score는 transverse profile과 longitudinal gain을 더한 뒤, weak modulation을 곱해 만든다.

```math
\text{score}_g(p)=\text{support\_mod}_g\cdot\text{alignment\_mod}_g\cdot\left(T(r_g)+g\cdot L(u_g)\right)
```

최종 `progression_tilted`는 guide-local score 가운데 최대값을 택한다.

```math
\text{progression\_tilted}(p)=\max_g \text{score}_g(p)
```

detail channel 가운데 `progression_transverse_component`는 near-tied guide candidate의 transverse term을 support/score 기준으로 부드럽게 섞은 inspection channel이다. 반면 `score`, `s_hat`, `n_hat`, `longitudinal_component` 등은 dominant guide 기준 값을 유지한다. 현재 `n_hat`는 signed lateral이 아니라 dominant guide 중심 구조까지의 unsigned 최단거리다.

의도:

- 같은 progression slice에서는 center-high transverse profile을 만든다.
- stronger longitudinal에서는 farther-ahead ordering을 만든다.
- split/merge는 shared prefix/suffix를 가진 multiple progression guide로 읽는다.
- downstream consumer는 이 수식을 직접 복제하기보다 cached runtime query layer를 소비한다.

## `exception layer` 계산

exception layer는 base field와 다른 층이다. safety / rule / dynamic burden을 soft와 hard로 분리해 계산하고, base preference로 상쇄되지 않게 둔다. 이 채널들은 costmap / exception 성격의 burden channel로 읽는 편이 맞다.

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

## 현재 tiny evaluator 조합

최종 state / trajectory score는 progression 본체만 합쳐 읽는다. 아래 수식은 canonical 철학이 아니라 현재 tiny evaluator가 실제로 쓰는 composition rule이다. exception layer는 costmap / burden visualization으로만 남고 public evaluator ordering에는 들어가지 않는다.

```math
\text{base\_preference\_total}(p)=\text{progression\_tilted}(p)
```

```math
\text{ordering\_key}(\tau)=\left(-\sum_{p\in\tau}\text{progression\_tilted}(p)\right)
```

```math
\text{trajectory\_base\_preference\_total} = \sum_k \text{base\_preference\_total}(p_k)
```

```math
\text{trajectory\_soft\_exception\_total} = \sum_k \text{soft\_exception\_total}(p_k)
```
