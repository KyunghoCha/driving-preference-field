# 현재 구현 수식

이 문서는 현재 구현 수식을 한 곳에 모아 둔 reference다. canonical 철학을 정의하지 않고, 현재 코드가 어떤 계산 순서로 움직이는지 정리한다. runtime contract와 현재 구현을 대조할 때 사용하며, 구현 파일을 읽기 전에 전체 계산 흐름을 빠르게 잡고 싶을 때 이 문서를 먼저 보면 된다.

## 이 문서를 읽는 방법

현재 구현 수식은 다섯 덩어리로 읽는 것이 가장 빠르다.

1. progression surface가 local map 위에 어떤 pooled 좌표장을 만드는가
2. exception layer가 soft / hard burden을 어떻게 만드는가
3. current tiny evaluator가 state / trajectory 단계에서 progression 값을 어떻게 합치는가

각 섹션은 수식 자체보다 먼저 “왜 이 수식이 필요한가”를 한두 문장으로 적는다. 목표는 수식만 나열하는 것이 아니라, 현재 구현이 어떤 계산 순서로 움직이는지 복원 가능하게 만드는 것이다.

## 공통 표기

- 점: \(p \in \mathbb{R}^2\)
- 벡터: \(v \in \mathbb{R}^2\)
- 내적: \(\langle a, b \rangle\)
- 정규화: \(\mathrm{normalize}(v) = v / \lVert v \rVert\)
- 클립: \(\mathrm{clip}(x, a, b) = \min(\max(x, a), b)\)

현재 구현은 progression guide별 winner를 먼저 고르지 않고, progression anchor 전체를 한 anchor pool로 읽는다.

## `progression surface` 계산

구현 경로:

- `src/driving_preference_field/progression_surface.py`
- `src/driving_preference_field/channels.py`
- `src/driving_preference_field/field_runtime.py`

progression surface는 local map 전체에 진행 좌표와 횡방향 좌표를 동시에 부여하기 위해 필요하다. 현재 구현은 progression anchor 전체에 대해 Gaussian raw weight를 먼저 계산하고, provisional pooled progress를 만든 뒤 soft progress gating을 한 번 더 곱한다. 그 다음 final pooled coordinate를 만들고, score는 한 번만 계산한다. exported `progression_transverse_component`만 guide-aware inspection smoothing을 유지한다.

현재 구현에서 progression surface는 canonical 본체에 가장 가까운 층이다. progression-centered whole-space preference를 가장 직접적으로 근사하는 수식이 이 섹션에 있다.

### `guide-local` anchor 좌표

각 progression guide는 anchor를 제공하지만, 현재 구현은 query마다 guide winner를 먼저 닫지 않는다. 모든 anchor는 같은 pooled evaluator 안에서 tangent / normal 좌표를 제공하는 재료로 들어간다.

```math
\tau_i = \langle p - a_i,\ t_i \rangle
```

```math
\nu_i = \langle p - a_i,\ n_i \rangle
```

```math
s_i = s_i^{anchor} + \tau_i
```

### `guide-local` Gaussian weight

첫 번째 단계는 모든 anchor에 대해 geometric Gaussian raw weight를 계산하는 것이다.

```math
r_i^{(0)} = w_i^{guide}\, c_i \exp \left(
-\frac{1}{2}\left[\left(\frac{\tau_i}{\sigma_{t,i}}\right)^2 + \left(\frac{\nu_i}{\sigma_n}\right)^2\right]
\right)
```

```math
\bar{w}_i^{(0)} = \frac{r_i^{(0)}}{\sum_j r_j^{(0)}}
```

```math
\hat{s}^{(0)} = \sum_i \bar{w}_i^{(0)} s_i
```

그 다음 branch 간 progress가 너무 멀리 섞이지 않도록 soft progress gate를 한 번 더 곱한다.

```math
g_i^{progress} = \exp \left(
-\frac{1}{2}\left(\frac{s_i-\hat{s}^{(0)}}{\sigma_{t,i}}\right)^2
\right)
```

```math
r_i = r_i^{(0)} g_i^{progress}
```

```math
\bar{w}_i = \frac{r_i}{\sum_j r_j}
```

현재 구현 상수:

```math
\sigma_{t,i}=\max(0.40,\ L_i\cdot \text{lookahead\_scale}\cdot 0.35)
```

```math
\sigma_n=\max(0.35,\ \text{transverse\_scale}\cdot 1.50)
```

### `guide-local` 좌표

final pooled coordinate는 모든 anchor를 다시 정규화한 뒤 만든다.

```math
\hat{s} = \sum_i \bar{w}_i s_i
```

```math
\hat{t} = \mathrm{normalize}\left(\sum_i \bar{w}_i t_i\right)
```

횡방향 magnitude는 opposite-side guide가 서로를 지워 버리지 않게, dominant participating anchor의 부호와 weighted absolute offset을 같이 사용한다.

```math
\text{sign}_{dom} =
\begin{cases}
\mathrm{sign}(\nu_{dom}), & |\nu_{dom}| > \varepsilon \\
\mathrm{sign}\left(\sum_i \bar{w}_i \nu_i\right), & \text{otherwise}
\end{cases}
```

```math
\hat{n} = \text{sign}_{dom}\sum_i \bar{w}_i |\nu_i|
```

이 정의는 parallel lane이나 split 내부에서 opposite-side guide가 lateral magnitude를 0으로 상쇄하는 것을 막기 위한 현재 구현 tradeoff다.

### `guide-local` longitudinal frame

longitudinal 성분은 pooled 좌표장 위에서도 어떤 frame으로 progress를 읽느냐에 따라 달라진다. 현재 구현은 local absolute와 ego relative 두 frame을 모두 지원한다.

먼저 anchor가 속한 guide extent를 final pooled weight로 섞어 pooled extent를 만든다.

```math
\hat{s}_{min} = \sum_i \bar{w}_i s_{min}(g(i))
```

```math
\hat{s}_{max} = \sum_i \bar{w}_i s_{max}(g(i))
```

local absolute:

```math
u_{\text{local\_absolute}} = \mathrm{clip}\left(
\frac{\hat{s} - \hat{s}_{min}}{\hat{s}_{max} - \hat{s}_{min}}, 0, 1
\right)
```

ego relative:

```math
\text{lookahead}_{pooled}=\max(0.40,\ (\hat{s}_{max}-\hat{s}_{min})\cdot \text{lookahead\_scale})
```

```math
u_{\text{ego\_relative}} = \mathrm{clip}\left(
\frac{\max(0,\ \hat{s} - \hat{s}_{ego})}{\text{lookahead}_{pooled}},\ 0,\ 1
\right)
```

여기서 \(\hat{s}_{ego}\)는 같은 pooled evaluator를 ego pose에 한 번 적용해서 얻는다.

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

score 본체는 pooled `\hat{n}`을 써서 transverse profile을 만든다.

```math
r=\frac{|\hat{n}|}{s_t},\quad s_t=\text{transverse\_scale}
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

exported `progression_transverse_component`는 inspection channel로 남기기 위해, guide별 local transverse candidate를 guide contribution과 guide-local inspection score 기준으로 다시 부드럽게 섞는다. 그래서 score 본체와 exported transverse debug channel은 current implementation에서 완전히 같은 값이 아니다.

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

최종 `progression_tilted`는 guide별 max 없이 한 번만 계산한다.

```math
\text{progression\_tilted}(p)=\text{support\_mod}\cdot\text{alignment\_mod}\cdot\left(T(|\hat{n}|)+g\cdot L(u)\right)
```

즉 현재 구현에는 guide 간 hard max envelope가 없다.

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
