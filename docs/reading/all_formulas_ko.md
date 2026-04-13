# 전체 수식 정리 (Current Implementation + Runtime Contract)

이 문서는 `driving-preference-field`에 등장하는 현재 구현 수식을 한 곳에 정리한다.

- canonical truth를 대신하지 않는다
- 구현과 문서 SSOT를 함께 대조하는 용도다
- 수식 변경 시 README, 관련 design 문서, 그리고 이 문서를 함께 갱신한다
- Notion에 붙여넣을 때 수식은 `$$...$` 형식으로 쓴다

## 0. 공통 표기

점/벡터:

- 점: `$$p \in \mathbb{R}^2$`
- 벡터: `$$v \in \mathbb{R}^2$`
- 내적: `$$\langle a,b \rangle$`
- 정규화: `$$\mathrm{normalize}(v)=v/\lVert v \rVert$`
- 클립: `$$\mathrm{clip}(x,a,b)=\min(\max(x,a),b)$`

## 1. Progression Surface

코드 이름과 수식 기호:

- `progression_tilted` -> `$$P(p)$`
- `alignment_mod` -> `$$A_m$`
- `support_mod` -> `$$S_m$`
- `longitudinal_component` -> `$$L(u)$`
- `transverse_component` -> `$$T(r)$`

### 1.1 Anchor local coordinates

anchor `i`에 대해:

`$$\tau_i=\langle p-a_i,\ t_i \rangle$`

`$$\nu_i=\langle p-a_i,\ n_i \rangle$`

변수:

- `$$p$`: query point
- `$$a_i$`: anchor point
- `$$t_i$`: anchor tangent (unit)
- `$$n_i$`: anchor normal (unit)

### 1.2 Gaussian anchor weights

`$$r_i=w_i^{\mathrm{guide}}\,c_i\,\exp\left(-\frac{1}{2}\left[\left(\frac{\tau_i}{\sigma_t}\right)^2+\left(\frac{\nu_i}{\sigma_n}\right)^2\right]\right)$`

`$$\bar{w}_i=\frac{r_i}{\sum_j r_j}$`

변수:

- `$$w_i^{\mathrm{guide}}$`: guide weight
- `$$c_i$`: confidence
- `$$\sigma_t$`: tangential scale
- `$$\sigma_n$`: normal scale

현재 구현:

`$$\sigma_t=\max(0.40,\ L_g \cdot s_{\ell}\cdot 0.35)$`

`$$\sigma_n=\max(0.35,\ s_t \cdot 1.50)$`

변수:

- `$$L_g$`: guide length
- `$$s_{\ell}$`: `lookahead_scale`
- `$$s_t$`: `transverse_scale`

### 1.3 Blended coordinates

`$$\hat{s}=\sum_i \bar{w}_i s_i$`

`$$\hat{n}=\sqrt{\sum_i \bar{w}_i \nu_i^2}$`

`$$\hat{t}=\mathrm{normalize}\left(\sum_i \bar{w}_i t_i\right)$`

여기서:

`$$s_i=s_i^{\mathrm{anchor}}+\tau_i$`

변수:

- `$$\hat{s}$`: blended progress
- `$$\hat{n}$`: blended transverse distance, `$$\hat{n}\ge 0$`
- `$$\hat{t}$`: blended tangent

### 1.4 Longitudinal frame

local absolute:

`$$u=\mathrm{clip}\left(\frac{\hat{s}-s_{\min}^{\mathrm{ext}}}{s_{\max}^{\mathrm{ext}}-s_{\min}^{\mathrm{ext}}},0,1\right)$`

ego relative:

`$$u=\mathrm{clip}\left(\frac{\max(0,\hat{s}-\hat{s}_{\mathrm{ego}})}{\ell},0,1\right)$`

변수:

- `$$\ell$`: lookahead

### 1.5 Longitudinal families

`$$L_{\mathrm{linear}}(u)=u$`

`$$L_{\mathrm{inverse}}(u)=\frac{(1+\alpha)u}{1+\alpha u}$`

`$$L_{\mathrm{power}}(u)=u^{\alpha}$`

`$$L_{\tanh}(u)=\frac{\tanh(\alpha u)}{\tanh(\alpha)}$`

변수:

- `$$\alpha$`: longitudinal shape

### 1.6 Transverse families

정의:

`$$r=\frac{\hat{n}}{s_t}$`

`$$T_{\mathrm{exp}}(r)=e^{-\beta r}$`

`$$T_{\mathrm{inv}}(r)=\frac{1}{1+\beta r}$`

`$$T_{\mathrm{pow}}(r)=\frac{1}{1+r^{\beta}}$`

변수:

- `$$\beta$`: transverse shape

### 1.7 Secondary modulation

`$$A_m=0.95+0.05\,\max(0,\langle h,\hat{t}\rangle)$`

`$$S_m=0.95+0.05\,\mathrm{clip}\left(\frac{\sum_i \bar{w}_i\min(c_i,c_{\max})}{c_{\max}},0,1\right)$`

변수:

- `$$h$`: heading unit vector
- `$$c_{\max}$`: support ceiling

### 1.8 Final progression score

`$$P(p)=S_m \cdot A_m \cdot \left(T(r)+g\cdot L(u)\right)$`

변수:

- `$$g$`: longitudinal gain

## 2. Interior / Boundary

코드 이름과 수식 기호:

- `interior_boundary` -> `$$B(p)$`
- `interior_signed_margin` -> `$$M(p)$`

### 2.1 Interior boundary score

`$$B(p)=\gamma\cdot\mathrm{clip}\left(\frac{d_{\partial\Omega}(p)}{m},0,1\right)$`

변수:

- `$$d_{\partial\Omega}(p)$`: drivable boundary distance
- `$$\gamma$`: interior boundary gain
- `$$m$`: margin scale

### 2.2 Interior signed margin

`$$M(p)=\max_{\Omega} d_{\mathrm{signed}}(p,\Omega)$`

region 내부이면 signed distance가 양수, 외부이면 음수다.

## 3. Branch Continuity

코드 이름과 수식 기호:

- `continuity_branch` -> `$$C(p)$`

guide `i`에 대해:

`$$a_i=\max(0,\langle h,t_i\rangle)\cdot w_{\mathrm{align}}$`

`$$q_i=e^{-d_i/\lambda}$`

`$$c_i^{\ast}=g_b\cdot w_i^{\mathrm{guide}}\cdot\min(c_i,c_{\max})\cdot q_i\cdot a_i$`

`$$C(p)=\max_i c_i^{\ast}$`

변수:

- `$$d_i$`: point-to-guide distance
- `$$\lambda$`: branch distance scale
- `$$w_{\mathrm{align}}$`: alignment weight
- `$$g_b$`: branch gain

## 4. Exception Layers

코드 이름과 수식 기호:

- `safety_soft` -> `$$E_s(p)$`
- `rule_soft` -> `$$E_r(p)$`
- `dynamic_soft` -> `$$E_d(p)$`

soft burden:

`$$b_{\mathrm{soft}}(p,R)=\begin{cases}\sigma(R), & p\in R\\[4pt]\sigma(R)\exp\left(\frac{d_{\mathrm{signed}}(p,R)}{\rho_R}\right), & p\notin R\end{cases}$`

hard hit:

`$$b_{\mathrm{hard}}(p,R)=H(R)\land(p\in R)$`

채널별 합:

`$$E_s(p)=\sum_{R\in\mathcal{S}} b_{\mathrm{soft}}(p,R)$`

`$$E_r(p)=\sum_{R\in\mathcal{R}} b_{\mathrm{soft}}(p,R)$`

`$$E_d(p)=\sum_{R\in\mathcal{D}} b_{\mathrm{soft}}(p,R)$`

변수:

- `$$\sigma(R)$`: region severity
- `$$\rho_R$`: influence radius
- `$$H(R)$`: hard flag

## 5. State / Trajectory Composition

코드 이름과 수식 기호:

- `base_preference_total` -> `$$F_b(p)$`
- `soft_exception_total` -> `$$F_s(p)$`
- `trajectory_base_preference_total` -> `$$J_b$`
- `trajectory_soft_exception_total` -> `$$J_s$`

state base total:

`$$F_b(p)=P(p)+B(p)+C(p)$`

state soft total:

`$$F_s(p)=E_s(p)+E_r(p)+E_d(p)$`

trajectory totals:

`$$J_b=\sum_k F_b(p_k)$`

`$$J_s=\sum_k F_s(p_k)$`

ordering key:

`$$(N_{\mathrm{hard}},J_s,-J_b)$`

변수:

- `$$N_{\mathrm{hard}}$`: hard violation count

## 6. 핵심 변수 요약

- `$$p$`: query point
- `$$h$`: heading unit vector
- `$$\tau_i$`: tangential offset
- `$$\nu_i$`: signed normal offset
- `$$\hat{n}$`: blended transverse distance
- `$$\hat{s}$`: blended progress
- `$$s_t$`: transverse scale
- `$$\alpha$`: longitudinal shape
- `$$\beta$`: transverse shape
- `$$g$`: longitudinal gain
- `$$c_i$`: confidence
- `$$c_{\max}$`: support ceiling
- `$$\gamma$`: interior boundary gain
- `$$\lambda$`: branch distance scale
