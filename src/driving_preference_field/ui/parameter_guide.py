from __future__ import annotations

import html
import re
from dataclasses import dataclass

from driving_preference_field.ui.locale import DEFAULT_LANGUAGE, LANG_EN, LANG_KO


@dataclass(frozen=True)
class ParameterGuideEntry:
    key: str
    label: str
    meaning: str
    effect_up: str
    effect_down: str
    practical_band: str
    technical_range: str
    tooltip: str


@dataclass(frozen=True)
class _ParameterStatic:
    label: str
    practical_band: str
    technical_range: str


PARAMETER_GUIDE_INTRO = {
    LANG_EN: (
        "This page explains the controls in the right-hand `Parameters` dock.\n"
        "`Guide` explains the workflow. This page explains what each control changes.\n"
        "Always start from `progression_tilted` with `Fixed` scale.\n"
        "Read the drivable boundary as an overlay only; do not read it as an additive base score.\n"
        "Treat obstacle / rule / dynamic channels as costmap visualization only.\n"
        "`Main` changes field semantics directly. `Advanced Surface` is for discretization, kernel, modulation, and handoff tuning.\n"
        "The current implementation builds guide-local coordinates and then reads the final field through the maximum guide score.\n"
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
        "`Main`은 field semantics를 직접 바꾸고, `Advanced Surface`는 discretization, kernel, modulation, handoff 품질을 조정한다.\n"
        "현재 구현은 progression guide 안에서 guide-local coordinate를 만들고, guide별 score 가운데 가장 큰 값을 최종 field로 읽는다.\n"
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
        "handoff": "Handoff",
    },
    LANG_KO: {
        "longitudinal": "Longitudinal",
        "transverse": "Transverse",
        "support_gate": "Support / Gate",
        "advanced": "Advanced Surface",
        "discretization": "Discretization",
        "support_kernel": "Support Kernel",
        "modulation": "Modulation",
        "handoff": "Handoff",
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


ADVANCED_PARAMETER_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "discretization",
        (
            "anchor_spacing_m",
            "spline_sample_density_m",
            "spline_min_subdivisions",
            "end_extension_m",
        ),
    ),
    (
        "support_kernel",
        (
            "min_sigma_t",
            "min_sigma_n",
            "sigma_t_scale",
            "sigma_n_scale",
        ),
    ),
    (
        "modulation",
        (
            "support_base",
            "support_range",
            "alignment_base",
            "alignment_range",
        ),
    ),
    (
        "handoff",
        (
            "transverse_handoff_support_ratio",
            "transverse_handoff_score_delta",
            "transverse_handoff_temperature",
        ),
    ),
)


PARAMETER_STATIC: dict[str, _ParameterStatic] = {
    "longitudinal_frame": _ParameterStatic("frame", "local_absolute | ego_relative", "local_absolute | ego_relative"),
    "longitudinal_family": _ParameterStatic("long family", "tanh | linear | inverse | power", "tanh | linear | inverse | power"),
    "longitudinal_gain": _ParameterStatic("long gain", "0.5 .. 3.0", "0.0 .. 1000.0"),
    "lookahead_scale": _ParameterStatic("long horizon", "0.1 .. 1.0", "0.0 .. 1000.0"),
    "longitudinal_shape": _ParameterStatic("long shape", "0.5 .. 4.0", "0.0 .. 1000.0"),
    "transverse_family": _ParameterStatic("trans family", "exponential | inverse | power", "exponential | inverse | power"),
    "transverse_scale": _ParameterStatic("trans scale", "0.25 .. 3.0", "0.0 .. 1000.0"),
    "transverse_shape": _ParameterStatic("trans shape", "0.5 .. 4.0", "0.0 .. 1000.0"),
    "support_ceiling": _ParameterStatic("support cap", "0.25 .. 1.0", "0.0 .. 1000.0"),
    "anchor_spacing_m": _ParameterStatic("anchor spacing", "0.05 .. 2.0", "0.05 .. 2.0"),
    "spline_sample_density_m": _ParameterStatic("spline density", "0.01 .. 1.0", "0.01 .. 1.0"),
    "spline_min_subdivisions": _ParameterStatic("min subdivisions", "1 .. 64", "1 .. 64"),
    "end_extension_m": _ParameterStatic("end extension", "0.0 .. 10.0", "0.0 .. 10.0"),
    "min_sigma_t": _ParameterStatic("min sigma_t", "0.05 .. 5.0", "0.05 .. 5.0"),
    "min_sigma_n": _ParameterStatic("min sigma_n", "0.05 .. 5.0", "0.05 .. 5.0"),
    "sigma_t_scale": _ParameterStatic("sigma_t scale", "0.05 .. 5.0", "0.05 .. 5.0"),
    "sigma_n_scale": _ParameterStatic("sigma_n scale", "0.05 .. 5.0", "0.05 .. 5.0"),
    "support_base": _ParameterStatic("support base", "0.0 .. 1.0", "0.0 .. 1.0"),
    "support_range": _ParameterStatic("support range", "0.0 .. 1.0", "0.0 .. 1.0"),
    "alignment_base": _ParameterStatic("alignment base", "0.0 .. 1.0", "0.0 .. 1.0"),
    "alignment_range": _ParameterStatic("alignment range", "0.0 .. 1.0", "0.0 .. 1.0"),
    "transverse_handoff_support_ratio": _ParameterStatic("handoff support ratio", "0.0 .. 1.0", "0.0 .. 1.0"),
    "transverse_handoff_score_delta": _ParameterStatic("handoff score delta", "0.0 .. 2.0", "0.0 .. 2.0"),
    "transverse_handoff_temperature": _ParameterStatic("handoff temperature", "0.01 .. 1.0", "0.01 .. 1.0"),
}


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
            "effect_up": "The longitudinal blending span becomes longer, so guide-local coordinates mix over a farther region.",
            "effect_down": "Longitudinal locality becomes stronger.",
            "tooltip": "scale for longitudinal sigma",
        },
        LANG_KO: {
            "meaning": "guide length와 lookahead를 longitudinal sigma로 바꾸는 scale이다.",
            "effect_up": "longitudinal blending span이 길어져 guide-local coordinate가 더 멀리 섞인다.",
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
    "transverse_handoff_support_ratio": {
        LANG_EN: {
            "meaning": "Minimum support ratio, relative to the dominant guide, for a guide to participate in transverse handoff smoothing.",
            "effect_up": "Candidate guides are filtered more aggressively, so handoff becomes harder.",
            "effect_down": "More guides participate in smoothing.",
            "tooltip": "minimum support ratio for handoff candidates",
        },
        LANG_KO: {
            "meaning": "transverse handoff candidate guide를 고를 때 dominant support 대비 최소 비율이다.",
            "effect_up": "candidate guide가 더 엄격하게 걸러져 handoff가 더 hard해진다.",
            "effect_down": "더 많은 guide가 handoff smoothing에 참여한다.",
            "tooltip": "handoff candidate 최소 support 비율",
        },
    },
    "transverse_handoff_score_delta": {
        LANG_EN: {
            "meaning": "Allowed score gap from the dominant guide when collecting transverse handoff candidates.",
            "effect_up": "More nearby guides remain eligible candidates.",
            "effect_down": "Candidate guides shrink more aggressively.",
            "tooltip": "allowed score gap for handoff candidates",
        },
        LANG_KO: {
            "meaning": "transverse handoff candidate guide를 고를 때 dominant score와 허용 차이다.",
            "effect_up": "더 많은 근접 guide가 candidate로 남는다.",
            "effect_down": "candidate guide가 더 엄격하게 줄어든다.",
            "tooltip": "handoff candidate score 허용 차",
        },
    },
    "transverse_handoff_temperature": {
        LANG_EN: {
            "meaning": "Soft weighting temperature used when blending transverse values across candidate guides.",
            "effect_up": "Guide handoff spreads more softly.",
            "effect_down": "Guide handoff collapses harder toward the dominant guide.",
            "tooltip": "temperature used for handoff smoothing",
        },
        LANG_KO: {
            "meaning": "candidate guide 사이 transverse blending의 soft weighting temperature다.",
            "effect_up": "guide handoff가 더 부드럽게 퍼진다.",
            "effect_down": "guide handoff가 dominant guide 쪽으로 더 hard하게 수렴한다.",
            "tooltip": "handoff smoothing temperature",
        },
    },
}


def _normalize_language(language: str) -> str:
    return language if language in {LANG_EN, LANG_KO} else DEFAULT_LANGUAGE


def _entry(language: str, key: str) -> ParameterGuideEntry:
    lang = _normalize_language(language)
    static = PARAMETER_STATIC[key]
    localized = PARAMETER_TEXTS[key][lang]
    return ParameterGuideEntry(
        key=key,
        label=static.label,
        meaning=localized["meaning"],
        effect_up=localized["effect_up"],
        effect_down=localized["effect_down"],
        practical_band=static.practical_band,
        technical_range=static.technical_range,
        tooltip=localized["tooltip"],
    )


def panel_note_text(language: str) -> str:
    return PANEL_NOTE_TEXT[_normalize_language(language)]


def section_title(language: str, key: str) -> str:
    return SECTION_TITLES[_normalize_language(language)][key]


def progression_parameter_guide(language: str) -> dict[str, ParameterGuideEntry]:
    lang = _normalize_language(language)
    return {key: _entry(lang, key) for key in PARAMETER_STATIC}


def main_parameter_keys() -> list[str]:
    return [
        "longitudinal_frame",
        "longitudinal_family",
        "longitudinal_gain",
        "lookahead_scale",
        "longitudinal_shape",
        "transverse_family",
        "transverse_scale",
        "transverse_shape",
        "support_ceiling",
    ]


def parameter_help_html(language: str = DEFAULT_LANGUAGE) -> str:
    lang = _normalize_language(language)
    guide = progression_parameter_guide(lang)

    def _inline_code_html(text: str) -> str:
        escaped = html.escape(text)
        return re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)

    def _summary_table(keys: list[str] | tuple[str, ...], *, anchor: str, title: str) -> str:
        rows = []
        for key in keys:
            entry = guide[key]
            rows.append(
                f"""
                <tr>
                  <td><code>{entry.label}</code></td>
                  <td>{entry.meaning}</td>
                  <td>{entry.effect_up}</td>
                  <td><code>{entry.practical_band}</code></td>
                </tr>
                """
            )
        return f"""
            <h3 id="{anchor}">{title}</h3>
            <table class="summary-table">
              <tr>
                <th>{"Parameter" if lang == LANG_EN else "파라미터"}</th>
                <th>{"What it changes" if lang == LANG_EN else "무엇이 바뀌는가"}</th>
                <th>{"Raise it when" if lang == LANG_EN else "올릴 때"}</th>
                <th>{"Practical Band" if lang == LANG_EN else "권장 구간"}</th>
              </tr>
              {''.join(rows)}
            </table>
        """

    advanced_sections = []
    for group_key, keys in ADVANCED_PARAMETER_GROUPS:
        advanced_sections.append(
            _summary_table(
                keys,
                anchor=f"group-{group_key.replace('_', '-')}",
                title=section_title(lang, group_key),
            )
        )

    detail_sections = []
    for key in [*main_parameter_keys(), *(key for _, keys in ADVANCED_PARAMETER_GROUPS for key in keys)]:
        entry = guide[key]
        detail_sections.append(
            f"""
            <div class="param-card">
              <h3><code>{entry.label}</code></h3>
              <table class="detail-table">
                <tr><th>{"Meaning" if lang == LANG_EN else "의미"}</th><td>{entry.meaning}</td></tr>
                <tr><th>{"Raise" if lang == LANG_EN else "올릴 때"}</th><td>{entry.effect_up}</td></tr>
                <tr><th>{"Lower" if lang == LANG_EN else "내릴 때"}</th><td>{entry.effect_down}</td></tr>
                <tr><th>{"Practical Band" if lang == LANG_EN else "권장 구간"}</th><td><code>{entry.practical_band}</code></td></tr>
                <tr><th>{"Technical Range" if lang == LANG_EN else "기술 범위"}</th><td><code>{entry.technical_range}</code></td></tr>
              </table>
            </div>
            """
        )

    intro_items = "".join(
        f"<li>{_inline_code_html(line)}</li>" for line in PARAMETER_GUIDE_INTRO[lang].splitlines()
    )
    if lang == LANG_EN:
        title = "Parameter Help"
        intro_paragraph = (
            "This page is the control reference for the right-hand <code>Parameters</code> dock. "
            "<code>Guide</code> covers the workflow; this page explains when to touch a knob and what changes when the value moves."
        )
        page_purpose_title = "What This Page Is For"
        main_title = "When to Use Main"
        main_intro = "Start here when you are deciding field semantics: longitudinal frame, family, gain, transverse profile, and support ceiling."
        main_intro += " Read `progression_tilted` on `Fixed` scale first."
        advanced_title = "When to Open Advanced Surface"
        advanced_intro = (
            "Open this only after the semantics are already clear. "
            "This section tunes discretization, support kernels, modulation, and split/merge handoff quality."
        )
        interpretation_title = "How to Read Parameter Effects"
        interpretation_items = [
            "<code>higher is better</code> is the score sign itself.",
            "<code>Fixed</code> is the reading mode. <code>Normalized</code> is only a convenience view.",
            "<code>Diff</code> always means <code>candidate - baseline</code>.",
            "<code>drivable boundary</code> is an overlay. It is not additive base preference.",
            "<code>Obstacle / Rule / Dynamic</code> are costmap views, not the base preference layer.",
            "<code>Raster</code> is a sampled visualization of the continuous field, not the field contract itself.",
        ]
        groups_title = "Parameter Groups"
        groups_intro = "Use these jumps when you already know which group you need."
        groups_links = [
            ("Longitudinal", "#group-longitudinal"),
            ("Transverse", "#group-transverse"),
            ("Support / Gate", "#group-support-gate"),
            ("Advanced Surface", "#group-advanced-surface"),
            ("Discretization", "#group-discretization"),
            ("Support Kernel", "#group-support-kernel"),
            ("Modulation", "#group-modulation"),
            ("Handoff", "#group-handoff"),
        ]
        detail_title = "Detailed Reference"
        detail_intro = "Use the lookup cards below when you need a fast up/down decision."
    else:
        title = "Parameter Help"
        intro_paragraph = (
            "이 도움말은 오른쪽 <code>Parameters</code> 패널의 참고 페이지다. "
            "<code>Guide</code>는 사용 흐름을 설명하고, 여기서는 각 조정 항목을 언제 만져야 하는지와 값을 올리거나 내리면 무엇이 달라지는지만 설명한다."
        )
        page_purpose_title = "이 페이지의 역할"
        main_title = "`Main`을 먼저 볼 때"
        main_intro = "field semantics를 읽을 때는 여기서 시작한다. longitudinal frame, family, gain, transverse profile, support ceiling을 먼저 본다."
        main_intro += " 먼저 `progression_tilted`를 `Fixed` scale로 읽는다."
        advanced_title = "`Advanced Surface`를 여는 때"
        advanced_intro = (
            "semantics가 먼저 잡힌 뒤에만 연다. 이 섹션은 discretization, support kernel, modulation, split/merge handoff 품질을 다룬다."
        )
        interpretation_title = "파라미터 효과 읽기"
        interpretation_items = [
            "<code>higher is better</code>는 score sign 자체다.",
            "<code>Fixed</code>는 읽는 기준이고, <code>Normalized</code>는 탐색용 보조 모드다.",
            "<code>Diff</code>는 항상 <code>candidate - baseline</code>이다.",
            "<code>drivable boundary</code>는 overlay다. base heatmap에 더하지 않는다.",
            "<code>Obstacle / Rule / Dynamic</code>는 costmap 시각화다. base preference와 같은 층이 아니다.",
            "<code>Raster</code>는 continuous field를 local map 위에서 샘플링한 시각화다.",
        ]
        groups_title = "Parameter groups"
        groups_intro = "필요한 그룹을 이미 알고 있다면 여기서 바로 이동한다."
        groups_links = [
            ("Longitudinal", "#group-longitudinal"),
            ("Transverse", "#group-transverse"),
            ("Support / Gate", "#group-support-gate"),
            ("Advanced Surface", "#group-advanced-surface"),
            ("Discretization", "#group-discretization"),
            ("Support Kernel", "#group-support-kernel"),
            ("Modulation", "#group-modulation"),
            ("Handoff", "#group-handoff"),
        ]
        detail_title = "세부 참고"
        detail_intro = "아래 lookup card는 값을 올릴지 내릴지 빠르게 결정할 때 쓴다."

    interpretation_html = "".join(f"<li>{item}</li>" for item in interpretation_items)
    groups_links_html = "".join(
        f'<li><a href="{target}">{html.escape(label)}</a></li>' for label, target in groups_links
    )
    return f"""
    <html>
      <head>
        <style>
          body {{
            font-family: 'Noto Sans CJK KR', 'Noto Sans', 'Malgun Gothic', sans-serif;
            font-size: 14px;
            line-height: 1.5;
            color: #202124;
          }}
          h1 {{ font-size: 28px; margin: 4px 0 12px 0; }}
          h2 {{ font-size: 20px; margin: 22px 0 10px 0; }}
          h3 {{ font-size: 17px; margin: 16px 0 8px 0; }}
          p {{ margin: 8px 0; }}
          code {{
            font-family: 'JetBrains Mono', 'Consolas', monospace;
            background: #f3f4f6;
            padding: 1px 4px;
            border-radius: 4px;
          }}
          .callout {{
            background: #f8fafc;
            border: 1px solid #d7e3f1;
            border-radius: 8px;
            padding: 12px 14px;
            margin: 10px 0 16px 0;
          }}
          .link-list {{
            columns: 2;
            margin: 8px 0 16px 0;
            padding-left: 20px;
          }}
          .link-list li {{
            margin-bottom: 4px;
          }}
          a {{
            color: #1d4ed8;
            text-decoration: none;
          }}
          .summary-table, .detail-table, .decision-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 8px 0 16px 0;
          }}
          .summary-table th, .summary-table td,
          .detail-table th, .detail-table td,
          .decision-table th, .decision-table td {{
            border: 1px solid #d8dee6;
            padding: 8px 10px;
            vertical-align: top;
          }}
          .summary-table th, .detail-table th, .decision-table th {{
            background: #f6f8fa;
            text-align: left;
            white-space: nowrap;
          }}
          .param-card {{
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 12px 14px;
            margin: 0 0 14px 0;
            background: #ffffff;
          }}
        </style>
      </head>
      <body>
        <h1>{title}</h1>
        <h2 id="page-purpose">{page_purpose_title}</h2>
        <p>{intro_paragraph}</p>
        <div class="callout">
          <p style="margin-top:0;">{_inline_code_html(PARAMETER_GUIDE_INTRO[lang].splitlines()[0])}</p>
          <p style="margin-bottom:0;">{_inline_code_html(PARAMETER_GUIDE_INTRO[lang].splitlines()[1])}</p>
        </div>
        <h2 id="when-main">{main_title}</h2>
        <p>{_inline_code_html(main_intro)}</p>
        {_summary_table(("longitudinal_frame", "longitudinal_family", "longitudinal_gain", "lookahead_scale", "longitudinal_shape"), anchor="group-longitudinal", title=section_title(lang, "longitudinal"))}
        {_summary_table(("transverse_family", "transverse_scale", "transverse_shape"), anchor="group-transverse", title=section_title(lang, "transverse"))}
        {_summary_table(("support_ceiling",), anchor="group-support-gate", title=section_title(lang, "support_gate"))}
        <h2 id="when-advanced">{advanced_title}</h2>
        <p>{_inline_code_html(advanced_intro)}</p>
        <h3 id="group-advanced-surface">{section_title(lang, "advanced")}</h3>
        <p>{_inline_code_html(advanced_intro)}</p>
        <h2 id="read-effects">{interpretation_title}</h2>
        <ul>{interpretation_html}</ul>
        <h2 id="parameter-groups">{groups_title}</h2>
        <p>{_inline_code_html(groups_intro)}</p>
        <ul class="link-list">{groups_links_html}</ul>
        {''.join(advanced_sections)}
        <h2 id="detailed-reference">{detail_title}</h2>
        <p>{_inline_code_html(detail_intro)}</p>
        {''.join(detail_sections)}
      </body>
    </html>
    """
