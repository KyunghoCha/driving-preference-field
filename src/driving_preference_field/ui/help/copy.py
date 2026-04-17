from __future__ import annotations

from driving_preference_field.ui.locale import LANG_EN, LANG_KO


PARAMETER_GUIDE_INTRO = {
    LANG_EN: (
        "This page explains the controls in the right-hand `Parameters` dock.\n"
        "`Guide` explains the workflow. This page explains what each control changes.\n"
        "Always start from `progression_tilted` with `Fixed` scale.\n"
        "Read the drivable boundary as an overlay only; do not read it as an additive base score.\n"
        "Treat obstacle / rule / dynamic channels as costmap visualization only.\n"
        "`Main` changes field semantics directly. `Advanced Surface` is for discretization, kernel, and weak modulation tuning.\n"
        "The current implementation evaluates one pooled blended progress field across all progression anchors, then reads transverse by selecting the nearest guide branch and softly blending nearby segments on that same guide.\n"
        "The exact current formula is `score = support_mod * alignment_mod * (transverse_component + longitudinal_gain * longitudinal_component)`.\n"
        "Support and alignment are weak secondary modulation terms. They should not dominate morphology.\n"
        "Split and merge are expressed as multiple progression guides with shared prefix/suffix. The raster is only a local-map sample of the continuous field."
    ),
    LANG_KO: (
        "이 도움말은 오른쪽 `Parameters` 패널의 조정 항목을 설명한다.\n"
        "`Guide`는 도구를 어떤 순서로 읽고 써야 하는지 설명하고, 여기서는 각 항목이 무엇을 바꾸는지에만 집중한다.\n"
        "항상 `progression_tilted`를 `Fixed` scale에서 먼저 읽는다.\n"
        "drivable boundary는 overlay로만 읽고 base heatmap에 더하지 않는다.\n"
        "obstacle / rule / dynamic 채널은 costmap 시각화로만 읽는다.\n"
        "`Main`은 field semantics를 직접 바꾸고, `Advanced Surface`는 discretization, kernel, 약한 modulation 품질을 조정한다.\n"
        "현재 구현은 progression anchor 전체를 하나의 pooled blended progress field로 읽고, 횡방향은 nearest guide branch를 고른 뒤 같은 guide의 nearby segments를 부드럽게 섞어 읽는다.\n"
        "현재 수식은 `score = support_mod * alignment_mod * (transverse_component + longitudinal_gain * longitudinal_component)`다.\n"
        "support와 alignment는 shape를 지배하지 않는 약한 보조 modulation이다.\n"
        "split과 merge는 shared prefix/suffix를 가진 multiple progression guides로 표현하고, raster는 continuous field를 local map 위에서 샘플링한 결과다."
    ),
}


SECTION_TITLES = {
    LANG_EN: {
        "longitudinal": "Longitudinal",
        "transverse": "Transverse",
        "support_gate": "Support / Gate",
        "advanced": "Advanced Surface",
        "discretization": "Discretization",
        "support_kernel": "Support Kernel",
        "modulation": "Modulation",
    },
    LANG_KO: {
        "longitudinal": "Longitudinal",
        "transverse": "Transverse",
        "support_gate": "Support / Gate",
        "advanced": "Advanced Surface",
        "discretization": "Discretization",
        "support_kernel": "Support Kernel",
        "modulation": "Modulation",
    },
}


PANEL_NOTE_TEXT = {
    LANG_EN: (
        "Current GUI edits `progression_tilted` through Main + Advanced Surface controls.\n"
        "Read the drivable boundary as overlay and obstacle/rule/dynamic as costmap."
    ),
    LANG_KO: (
        "이 패널은 `Main`과 `Advanced Surface`로 `progression_tilted`를 조정한다.\n"
        "Drivable boundary는 overlay로 읽고, obstacle/rule/dynamic은 costmap으로 읽는다."
    ),
}


# NOTE: Keep this table aligned with ui.help.catalog.PARAMETER_SPECS.
PARAMETER_TEXTS: dict[str, dict[str, dict[str, str]]] = {
    "longitudinal_frame": {
        LANG_EN: {
            "meaning": "Choose whether longitudinal tilt reads absolute progress along the local map or progress relative to the ego state.",
            "effect_up": "There is no numeric raise direction. `local_absolute` builds a global slope across the visible fabric; `ego_relative` emphasizes ahead-of-ego ordering more directly.",
            "effect_down": "Switching from `ego_relative` to `local_absolute` makes the whole local map ordering matter more than the immediate ego-forward region.",
            "tooltip": "frame for longitudinal tilt",
        },
        LANG_KO: {
            "meaning": "longitudinal tilt를 local map의 절대 progress로 읽을지, ego 기준 progress 차이로 읽을지 고른다.",
            "effect_up": "숫자 증가 개념은 없다. `local_absolute`는 local map 전체 fabric space의 전역적인 기울기를 만들고, `ego_relative`는 ego 기준 앞쪽 ordering을 더 직접적으로 키운다.",
            "effect_down": "`ego_relative`에서 `local_absolute`로 바꾸면 바로 앞 ego 기준보다 local map 전체 progress ordering을 더 강하게 본다.",
            "tooltip": "longitudinal tilt 기준 frame",
        },
    },
    "longitudinal_family": {
        LANG_EN: {
            "meaning": "Pick the longitudinal family that determines how additional score grows along the progression axis on the continuous surface.",
            "effect_up": "There is no numeric raise direction. Changing the family changes the ramp shape for the same progress delta.",
            "effect_down": "A gentler family makes the progression gradient look less sharp.",
            "tooltip": "function family used along the progression axis",
        },
        LANG_KO: {
            "meaning": "continuous surface 위에서 progression axis를 따라 더 먼 gain을 어떻게 더할지 정하는 longitudinal family를 고른다.",
            "effect_up": "숫자 증가 개념은 없다. family를 바꾸면 같은 progress 차이에도 ramp 형태가 달라진다.",
            "effect_down": "가족을 더 완만한 쪽으로 바꾸면 progression gradient가 덜 날카롭게 보인다.",
            "tooltip": "progression axis를 따라 점수가 커지는 함수 family",
        },
    },
    "longitudinal_gain": {
        LANG_EN: {
            "meaning": "Set the strength of the longitudinal tilt added on top of the center-high transverse profile.",
            "effect_up": "Score differences grow more aggressively in the forward direction, so the ordering can favor farther good regions without stepping through the nearest center first.",
            "effect_down": "The center-high transverse profile dominates more, so the field behaves more like a nearby center-following surface.",
            "tooltip": "strength of longitudinal tilt. Recommended 0.5..3.0",
        },
        LANG_KO: {
            "meaning": "center-high transverse profile 위에 더해지는 longitudinal tilt의 세기를 정한다.",
            "effect_up": "진행방향으로 갈수록 score 차이가 더 벌어져, 바로 앞 중심을 안 밟고도 더 먼 좋은 영역을 향하는 ordering이 쉬워진다.",
            "effect_down": "횡단면 중심 profile이 더 지배적이 되어 가까운 중심을 따라가는 성향이 강해진다.",
            "tooltip": "진행방향 tilt 세기. 추천 0.5..3.0",
        },
    },
    "lookahead_scale": {
        LANG_EN: {
            "meaning": "In `ego_relative`, control how quickly the ego-forward gain saturates. In `local_absolute`, the effect is weak or absent.",
            "effect_up": "The ego-relative gain grows more slowly and stretches farther ahead.",
            "effect_down": "The ego-relative gain saturates sooner, so nearby forward points get a stronger tilt faster.",
            "tooltip": "accumulation speed for longitudinal tilt. Recommended 0.1..1.0",
        },
        LANG_KO: {
            "meaning": "`ego_relative` frame에서 ego 앞쪽 gain이 얼마나 빨리 포화되는지 정한다. `local_absolute`에서는 영향이 약하거나 없다.",
            "effect_up": "ego-relative gain이 더 천천히 커져, 멀리 보며 점진적으로 기울어진다.",
            "effect_down": "ego-relative gain이 더 빨리 커져, 가까운 앞쪽에서도 tilt가 강하게 나타난다.",
            "tooltip": "진행방향 tilt 누적 속도. 추천 0.1..1.0",
        },
    },
    "longitudinal_shape": {
        LANG_EN: {
            "meaning": "Control the curvature or nonlinearity within the chosen longitudinal family.",
            "effect_up": "Within the selected family, the ramp becomes steeper or grows later depending on the family definition.",
            "effect_down": "Within the selected family, the ramp becomes gentler and less aggressive.",
            "tooltip": "nonlinearity of the longitudinal family. Recommended 0.5..4.0",
        },
        LANG_KO: {
            "meaning": "선택한 longitudinal family의 곡률이나 nonlinearity 정도를 정한다.",
            "effect_up": "family가 허용하는 범위 안에서 더 급하거나 더 늦게 커지는 ramp가 된다.",
            "effect_down": "family가 허용하는 범위 안에서 더 완만하고 덜 공격적인 ramp가 된다.",
            "tooltip": "longitudinal family 비선형 정도. 추천 0.5..4.0",
        },
    },
    "transverse_family": {
        LANG_EN: {
            "meaning": "Pick the transverse family that shapes the center-high profile across a single progression slice. Split and merge still derive from the progression guide set directly.",
            "effect_up": "There is no numeric raise direction. Changing the family changes how quickly score decays off-axis.",
            "effect_down": "A gentler family keeps off-axis score alive longer, which can connect to farther good regions more easily.",
            "tooltip": "cross-section function family around the guide center",
        },
        LANG_KO: {
            "meaning": "같은 진행 slice에서 중심이 가장 높게 보이는 횡단면 profile의 함수 family를 고른다. split/merge도 현재는 progression guide 집합에서 바로 계산한다.",
            "effect_up": "숫자 증가 개념은 없다. family를 바꾸면 축 밖 감쇠 모양이 달라진다.",
            "effect_down": "더 완만한 family로 바꾸면 off-axis 점수가 더 오래 유지되어 멀리 있는 좋은 영역으로 이어질 여지가 커진다.",
            "tooltip": "경로 중심 횡단면 함수 family",
        },
    },
    "transverse_scale": {
        LANG_EN: {
            "meaning": "Set how widely the center-high transverse profile spreads on the continuous surface.",
            "effect_up": "Score falls more slowly away from the axis, so the field spreads wider.",
            "effect_down": "Score falls faster once the axis is left, so the field narrows.",
            "tooltip": "width of the cross-section around the guide. Recommended 0.25..3.0",
        },
        LANG_KO: {
            "meaning": "continuous surface에서 중심 횡단면이 얼마나 넓게 퍼질지 정한다.",
            "effect_up": "축에서 조금 멀어져도 점수가 덜 줄어들어 field가 더 넓게 퍼진다.",
            "effect_down": "축을 벗어나면 점수가 더 빨리 줄어들어 field가 더 좁아진다.",
            "tooltip": "경로 중심 횡단면 폭. 추천 0.25..3.0",
        },
    },
    "transverse_shape": {
        LANG_EN: {
            "meaning": "Set the curvature of the selected transverse family.",
            "effect_up": "Off-axis score falls more sharply or center-to-edge contrast grows, depending on the family.",
            "effect_down": "The profile becomes gentler and more spread near the axis.",
            "tooltip": "curvature of the transverse profile. Recommended 0.5..4.0",
        },
        LANG_KO: {
            "meaning": "선택한 transverse family의 횡단면 곡률을 정한다.",
            "effect_up": "축 밖 점수가 더 급하게 줄거나, family에 따라 중심부와 바깥부의 contrast가 커진다.",
            "effect_down": "축 주변이 더 완만해지고 퍼진다.",
            "tooltip": "횡단면 곡률. 추천 0.5..4.0",
        },
    },
    "support_ceiling": {
        LANG_EN: {
            "meaning": "Upper bound of the auxiliary scale that guide weight and confidence can impose on the progression surface.",
            "effect_up": "High-support guides are allowed to contribute more strongly.",
            "effect_down": "Even high-support guides cannot amplify progression score past a lower cap.",
            "tooltip": "upper cap for guide support. Recommended 0.25..1.0",
        },
        LANG_KO: {
            "meaning": "guide weight와 confidence가 progression surface 전체에 주는 보조 scale의 상한이다.",
            "effect_up": "support가 높은 guide의 기여를 더 많이 허용한다.",
            "effect_down": "support가 높아도 일정 수준 이상 progression 점수가 세지지 않게 막는다.",
            "tooltip": "guide support 상한. 추천 0.25..1.0",
        },
    },
    "anchor_spacing_m": {
        LANG_EN: {
            "meaning": "Distance between guide anchors in meters.",
            "effect_up": "Fewer anchors reduce computation cost but can make local coordinates and support fields coarser.",
            "effect_down": "Denser anchors can stabilize shape at the cost of more computation.",
            "tooltip": "spacing between anchors",
        },
        LANG_KO: {
            "meaning": "guide anchor를 몇 m 간격으로 배치할지 정한다.",
            "effect_up": "anchor가 성기어져 계산량은 줄지만 local coordinate와 support field가 더 거칠어질 수 있다.",
            "effect_down": "anchor가 촘촘해져 shape는 더 안정적일 수 있지만 계산량이 늘어난다.",
            "tooltip": "anchor 간격",
        },
    },
    "spline_sample_density_m": {
        LANG_EN: {
            "meaning": "Sampling density used when densifying the guide polyline.",
            "effect_up": "Coarser sampling reduces cost but can lower curve fidelity.",
            "effect_down": "Denser sampling improves curve fidelity at higher cost.",
            "tooltip": "interval used for spline densification",
        },
        LANG_KO: {
            "meaning": "guide polyline을 densify할 때 세그먼트를 얼마나 촘촘히 샘플링할지 정한다.",
            "effect_up": "샘플이 성기어져 계산량은 줄지만 곡선의 smooth resampling 품질이 낮아질 수 있다.",
            "effect_down": "샘플이 촘촘해져 곡선 fidelity는 좋아질 수 있지만 계산량이 늘어난다.",
            "tooltip": "spline densification 간격",
        },
    },
    "spline_min_subdivisions": {
        LANG_EN: {
            "meaning": "Minimum subdivision count kept even for very short segments.",
            "effect_up": "Short segments get sampled more heavily, which can improve curve fidelity at higher cost.",
            "effect_down": "Short-segment resampling becomes rougher.",
            "tooltip": "minimum subdivision count",
        },
        LANG_KO: {
            "meaning": "짧은 세그먼트에서도 유지할 최소 subdivision 수다.",
            "effect_up": "짧은 구간도 더 많이 쪼개 곡선 fidelity가 올라갈 수 있지만 계산량이 늘어난다.",
            "effect_down": "짧은 세그먼트의 resampling이 더 거칠어질 수 있다.",
            "tooltip": "최소 subdivision 수",
        },
    },
    "end_extension_m": {
        LANG_EN: {
            "meaning": "Length of the virtual continuation anchors added beyond the visible guide end.",
            "effect_up": "Endpoint end-cap artifacts shrink and continuation beyond the visible endpoint lasts longer.",
            "effect_down": "Influence from the guide end dies out sooner.",
            "tooltip": "virtual extension length at the guide end",
        },
        LANG_KO: {
            "meaning": "guide 끝에 virtual continuation anchor를 얼마나 연장할지 정한다.",
            "effect_up": "visible endpoint 근처 end-cap artifact를 줄이고 끝 이후 continuation을 더 길게 허용한다.",
            "effect_down": "guide 끝 influence가 더 빨리 사라진다.",
            "tooltip": "guide 끝 연장 길이",
        },
    },
    "min_sigma_t": {
        LANG_EN: {
            "meaning": "Minimum width of the longitudinal Gaussian support kernel.",
            "effect_up": "Support spreads farther along the guide axis.",
            "effect_down": "Longitudinal support falls off sooner.",
            "tooltip": "minimum width for longitudinal support",
        },
        LANG_KO: {
            "meaning": "longitudinal Gaussian support의 최소 폭이다.",
            "effect_up": "guide 축 방향 influence가 더 넓게 퍼진다.",
            "effect_down": "guide 축 방향 support가 더 빠르게 줄어든다.",
            "tooltip": "longitudinal support 최소 폭",
        },
    },
    "min_sigma_n": {
        LANG_EN: {
            "meaning": "Minimum width of the lateral Gaussian support kernel.",
            "effect_up": "Support spreads farther away from the axis.",
            "effect_down": "Off-axis support falls off sooner.",
            "tooltip": "minimum width for lateral support",
        },
        LANG_KO: {
            "meaning": "lateral Gaussian support의 최소 폭이다.",
            "effect_up": "축 밖 support가 더 넓게 퍼진다.",
            "effect_down": "축 밖 support가 더 빨리 줄어든다.",
            "tooltip": "lateral support 최소 폭",
        },
    },
    "sigma_t_scale": {
        LANG_EN: {
            "meaning": "Scale that converts guide length and lookahead into longitudinal sigma.",
            "effect_up": "The longitudinal blending span becomes longer, so pooled coordinates mix over a farther region.",
            "effect_down": "Longitudinal locality becomes stronger.",
            "tooltip": "scale for longitudinal sigma",
        },
        LANG_KO: {
            "meaning": "guide length와 lookahead를 longitudinal sigma로 바꾸는 scale이다.",
            "effect_up": "longitudinal blending span이 길어져 pooled coordinate가 더 멀리 섞인다.",
            "effect_down": "longitudinal locality가 강해진다.",
            "tooltip": "longitudinal sigma scale",
        },
    },
    "sigma_n_scale": {
        LANG_EN: {
            "meaning": "Scale that converts transverse scale into lateral sigma.",
            "effect_up": "The lateral blending span grows wider, so ridges can spread out more.",
            "effect_down": "Lateral locality becomes stronger.",
            "tooltip": "scale for lateral sigma",
        },
        LANG_KO: {
            "meaning": "transverse_scale을 lateral sigma로 바꾸는 scale이다.",
            "effect_up": "lateral blending span이 넓어져 ridge가 더 퍼질 수 있다.",
            "effect_down": "lateral locality가 강해진다.",
            "tooltip": "lateral sigma scale",
        },
    },
    "support_base": {
        LANG_EN: {
            "meaning": "Lower bound of support modulation.",
            "effect_up": "Low-support regions lose less score.",
            "effect_down": "Poor-support regions lose more score.",
            "tooltip": "lower bound for support modulation",
        },
        LANG_KO: {
            "meaning": "support modulation의 바닥값이다.",
            "effect_up": "support가 낮아도 score가 덜 꺼진다.",
            "effect_down": "support quality가 낮을 때 score가 더 많이 줄어든다.",
            "tooltip": "support modulation 바닥값",
        },
    },
    "support_range": {
        LANG_EN: {
            "meaning": "How much support quality is allowed to change the modulation value.",
            "effect_up": "Support quality has more influence on the final score.",
            "effect_down": "Support modulation becomes flatter.",
            "tooltip": "variation range of support modulation",
        },
        LANG_KO: {
            "meaning": "support quality가 modulation에 줄 수 있는 변화량이다.",
            "effect_up": "support quality의 영향이 더 커진다.",
            "effect_down": "support modulation이 더 평평해진다.",
            "tooltip": "support modulation 변화량",
        },
    },
    "alignment_base": {
        LANG_EN: {
            "meaning": "Lower bound of heading-alignment modulation.",
            "effect_up": "Score is penalized less even when heading is misaligned.",
            "effect_down": "Heading mismatch penalty becomes stronger.",
            "tooltip": "lower bound for alignment modulation",
        },
        LANG_KO: {
            "meaning": "heading alignment modulation의 바닥값이다.",
            "effect_up": "heading이 어긋나도 score가 덜 깎인다.",
            "effect_down": "heading mismatch penalty가 더 강해진다.",
            "tooltip": "alignment modulation 바닥값",
        },
    },
    "alignment_range": {
        LANG_EN: {
            "meaning": "How much heading-alignment quality is allowed to change the modulation value.",
            "effect_up": "Heading alignment has more influence on the final score.",
            "effect_down": "Alignment modulation becomes flatter.",
            "tooltip": "variation range of alignment modulation",
        },
        LANG_KO: {
            "meaning": "heading alignment quality가 modulation에 줄 수 있는 변화량이다.",
            "effect_up": "heading alignment의 영향이 더 커진다.",
            "effect_down": "alignment modulation이 더 평평해진다.",
            "tooltip": "alignment modulation 변화량",
        },
    },
}
