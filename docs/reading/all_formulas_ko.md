# 전체 수식 정리 (Current Implementation + Runtime Contract)

이 문서는 `driving-preference-field`에 등장하는 **모든 현재 구현 수식**과 변수를 한 곳에 정리한다.

- canonical truth를 대신하지 않는다
- 구현과 문서 SSOT를 한 번에 대조하는 용도다
- 수식 변경 시 README, 관련 design 문서, 그리고 이 문서를 함께 갱신한다

## 0. 공통 표기

점/벡터:

- 점: \(p\in\mathbb{R}^2\)
- 벡터: \(v\in\mathbb{R}^2\)
- 내적: \(\langle a,b\rangle\)
- 정규화: \(\mathrm{normalize}(v)=v/\lVert v\rVert\)
- 클립: \(\mathrm{clip}(x, a, b)=\min(\max(x,a),b)\)

## 1. Progression Surface (whole-fabric)

### 1.1 Anchor local coordinates

anchor i에 대해:

```math
\tau_i = \langle p-a_i,\ t_i \rangle
```

```math
\nu_i = \langle p-a_i,\ n_i \rangle
```

변수:

- \(p\): query point
- \(a_i\): anchor point
- \(t_i\): anchor tangent (unit)
- \(n_i\): anchor normal (unit)

### 1.2 Gaussian anchor weights

```math
r_i = w_i^{guide}\, c_i\, \exp\left(-\frac{1}{2}\left[\left(\frac{\tau_i}{\sigma_t}\right)^2+\left(\frac{\nu_i}{\sigma_n}\right)^2\right]\right)
```

```math
\bar{w}_i = \frac{r_i}{\sum_j r_j}
```

변수:

- \(w_i^{guide}\): guide weight
- \(c_i\): confidence
- \(\sigma_t\): tangential scale
- \(\sigma_n\): normal scale

현재 구현:

```math
\sigma_t=\max(0.40,\ L\cdot \text{lookahead\_scale}\cdot 0.35)
```

```math
\sigma_n=\max(0.35,\ \text{transverse\_scale}\cdot 1.50)
```

### 1.3 Blended coordinates

```math
\hat{s} = \sum_i \bar{w}_i s_i
```

```math
\hat{n} = \sqrt{\sum_i \bar{w}_i \nu_i^2}
```

```math
\hat{t} = \mathrm{normalize}\left(\sum_i \bar{w}_i t_i\right)
```

여기서:

```math
s_i = s_i^{\text{anchor}} + \tau_i
```

변수:

- \(\hat{s}\): blended progress
- \(\hat{n}\): blended transverse distance (\(\ge 0\))
- \(\hat{t}\): blended tangent

### 1.4 Longitudinal frame

local absolute:

```math
u = \mathrm{clip}\left(\frac{\hat{s}-s_{\min}^{ext}}{s_{\max}^{ext}-s_{\min}^{ext}},\ 0,\ 1\right)
```

ego relative:

```math
u = \mathrm{clip}\left(\frac{\max(0,\ \hat{s}-\hat{s}_{ego})}{\text{lookahead}},\ 0,\ 1\right)
```

### 1.5 Longitudinal families

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

### 1.6 Transverse families

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

변수:

- \(\beta=\text{transverse\_shape}\)

### 1.7 Secondary modulation

```math
\text{alignment\_mod} = 0.95 + 0.05\,\max(0,\langle h,\hat{t}\rangle)
```

```math
\text{support\_mod} = 0.95 + 0.05\,\mathrm{clip}\left(\frac{\sum_i \bar{w}_i\min(c_i,c_{\max})}{c_{\max}},\ 0,\ 1\right)
```

### 1.8 Final progression score

```math
\text{progression\_tilted}(p)=\text{support\_mod}\cdot\text{alignment\_mod}\cdot\left(T(r)+g\cdot L(u)\right)
```

변수:

- \(g=\text{longitudinal\_gain}\)

## 2. Interior / Boundary

### 2.1 Interior boundary score

```math
\text{interior\_boundary}(p)=\gamma\cdot\mathrm{clip}\left(\frac{d_{\partial\Omega}(p)}{\text{margin\_scale}},\ 0,\ 1\right)
```

변수:

- \(d_{\partial\Omega}(p)\): drivable boundary distance
- \(\gamma\): interior boundary gain

### 2.2 Interior signed margin (debug)

```math
\text{interior\_signed\_margin}(p)=\max_{\Omega}\ d_{\text{signed}}(p,\Omega)
```

region 내부이면 signed distance가 양수, 외부이면 음수.

## 3. Branch Continuity

guide i에 대해:

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

변수:

- \(d_i\): point-to-guide distance
- \(\lambda\): distance scale
- \(w_{align}\): alignment weight

## 4. Exception Layers

soft burden:

```math
b_{\text{soft}}(p,R)=
\begin{cases}
\text{severity}(R), & p\in R\\
\text{severity}(R)\exp\left(\frac{d_{\text{signed}}(p,R)}{\rho_R}\right), & p\notin R
\end{cases}
```

hard hit:

```math
b_{\text{hard}}(p,R)=\text{hard}(R)\land(p\in R)
```

채널별 합:

```math
\text{safety\_soft}(p)=\sum_{R\in\mathcal{S}} b_{\text{soft}}(p,R)
```

```math
\text{rule\_soft}(p)=\sum_{R\in\mathcal{R}} b_{\text{soft}}(p,R)
```

```math
\text{dynamic\_soft}(p)=\sum_{R\in\mathcal{D}} b_{\text{soft}}(p,R)
```

## 5. State / Trajectory Composition

state base total:

```math
\text{base\_preference\_total}(p)=
\text{progression\_tilted}(p)+
\text{interior\_boundary}(p)+
\text{continuity\_branch}(p)
```

state soft total:

```math
\text{soft\_exception\_total}(p)=
\text{safety\_soft}(p)+
\text{rule\_soft}(p)+
\text{dynamic\_soft}(p)
```

trajectory totals:

```math
\text{trajectory\_base\_preference\_total}=\sum_k \text{base\_preference\_total}(p_k)
```

```math
\text{trajectory\_soft\_exception\_total}=\sum_k \text{soft\_exception\_total}(p_k)
```

ordering key:

```math
(\text{hard\_violation\_count},\ \text{trajectory\_soft\_exception\_total},\ -\text{trajectory\_base\_preference\_total})
```

## 6. 변수 요약 (핵심)

- \(p\): query point
- \(h\): heading unit vector
- \(\tau_i\): tangential offset
- \(\nu_i\): signed normal offset
- \(\hat{n}\): blended transverse distance
- \(\hat{s}\): blended progress
- \(s_t\): transverse scale
- \(\alpha\): longitudinal shape
- \(\beta\): transverse shape
- \(g\): longitudinal gain
- \(c_i\): confidence
- \(c_{\max}\): support ceiling
- \(\gamma\): interior boundary gain
- \(\lambda\): branch distance scale