from __future__ import annotations

from local_reference_path_cost.ui.locale import LANG_EN, LANG_KO


PARAMETER_GUIDE_INTRO = {
    LANG_EN: (
        "This page explains the controls in the right-hand `Parameters` dock.\n"
        "`Guide` explains the workflow. This page explains what each control changes.\n"
        "Always start from `progression_tilted` with `Fixed` scale.\n"
        "Read the drivable boundary as an overlay only; do not read it as an additive base score.\n"
        "Treat obstacle / rule / dynamic channels as costmap visualization only.\n"
        "`Main` changes score semantics directly. `Advanced Surface` is for discretization, kernel, and modulation tuning.\n"
        "The current implementation blends guide-local progress coordinates, reads transverse from shortest distance to the raw visible progression guide polyline, and then reads the final field through the maximum guide score.\n"
        "The exact current formula is `score = support_mod * alignment_mod * (transverse_term + longitudinal_gain * longitudinal_component)`.\n"
        "`Planner Lookup Progression Tilted` and `Planner Lookup Error` are internal comparison channels for the planner lookup surrogate. They do not replace the exact runtime channels as canonical inspection surfaces.\n"
        "Support and alignment are weak secondary modulation terms. They should not dominate morphology.\n"
        "Split and merge are expressed as multiple progression guides with shared prefix/suffix. The raster is only a local-map sample of the continuous field."
    ),
    LANG_KO: (
        "이 도움말은 오른쪽 `Parameters` 패널의 조정 항목을 설명한다.\n"
        "`Guide`는 도구를 어떤 순서로 읽고 써야 하는지 설명하고, 여기서는 각 항목이 무엇을 바꾸는지에만 집중한다.\n"
        "항상 `progression_tilted`를 `Fixed` scale에서 먼저 읽는다.\n"
        "drivable boundary는 overlay로만 읽고 base heatmap에 더하지 않는다.\n"
        "obstacle / rule / dynamic 채널은 costmap 시각화로만 읽는다.\n"
        "`Main`은 score semantics를 직접 바꾸고, `Advanced Surface`는 discretization, kernel, modulation 품질을 조정한다.\n"
        "현재 구현은 progression guide 안에서 guide-local progress coordinate를 섞고, 횡방향은 raw visible progression guide polyline까지의 최단거리로 읽은 뒤, guide별 score 가운데 가장 큰 값을 최종 field로 읽는다.\n"
        "현재 수식은 `score = support_mod * alignment_mod * (transverse_term + longitudinal_gain * longitudinal_component)`다.\n"
        "`Planner Lookup Progression Tilted`와 `Planner Lookup Error`는 planner lookup surrogate를 비교하기 위한 internal channel일 뿐이며, canonical inspection 기준을 exact runtime channel에서 바꾸지 않는다.\n"
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
            "meaning": "Set the mixing weight applied to the longitudinal function after the function itself is formed.",
            "effect_up": "The already-shaped longitudinal term contributes more strongly relative to the transverse term in the final score composition.",
            "effect_down": "The transverse term dominates more strongly in the final score composition.",
            "tooltip": "mixing weight for the longitudinal term. Recommended 0.5..3.0",
        },
        LANG_KO: {
            "meaning": "함수 자체가 만들어진 뒤 longitudinal term에 곱해지는 mixing weight를 정한다.",
            "effect_up": "이미 만들어진 longitudinal 함수가 최종 score 합성에서 transverse term보다 더 강하게 작동한다.",
            "effect_down": "최종 score 합성에서 transverse term이 더 지배적으로 남는다.",
            "tooltip": "longitudinal term mixing weight. 추천 0.5..3.0",
        },
    },
    "longitudinal_peak": {
        LANG_EN: {
            "meaning": "Set the ceiling of the longitudinal function itself before longitudinal gain is applied.",
            "effect_up": "The longitudinal function rises to a higher endpoint or family ceiling on its own, instead of relying on gain to amplify it afterward.",
            "effect_down": "The longitudinal function stays lower on its own, so endpoint strength depends more on the later mixing weight.",
            "tooltip": "ceiling of the longitudinal function itself. Recommended 0.5..3.0",
        },
        LANG_KO: {
            "meaning": "longitudinal gain을 곱하기 전에 함수 자체가 가지는 ceiling을 정한다.",
            "effect_up": "나중 gain으로 키우기 전에 함수 자체가 더 높은 끝단 또는 family ceiling을 갖게 된다.",
            "effect_down": "함수 자체 ceiling이 낮아져, 끝단 세기가 이후 mixing weight에 더 의존하게 된다.",
            "tooltip": "longitudinal 함수 자체 ceiling. 추천 0.5..3.0",
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
            "meaning": "Control the curvature or nonlinearity within the chosen longitudinal family. In the `linear` family it also scales the ramp slope and endpoint ceiling together.",
            "effect_up": "Within the selected family, the ramp becomes steeper or grows later depending on the family definition. In `linear`, the endpoint ceiling also rises because the slope itself gets steeper.",
            "effect_down": "Within the selected family, the ramp becomes gentler and less aggressive. In `linear`, the endpoint ceiling also drops because the slope itself gets shallower.",
            "tooltip": "nonlinearity of the longitudinal family. Recommended 0.5..4.0",
        },
        LANG_KO: {
            "meaning": "선택한 longitudinal family 안에서 곡률이나 nonlinearity를 정한다. `linear` family에서는 ramp 기울기와 끝단 ceiling이 같이 움직인다.",
            "effect_up": "family 정의에 따라 더 급하거나 더 늦게 커지는 ramp가 된다. `linear`에서는 기울기 자체가 커져 끝단 ceiling도 함께 올라간다.",
            "effect_down": "family 정의에 따라 더 완만하고 덜 공격적인 ramp가 된다. `linear`에서는 기울기가 완만해져 끝단 ceiling도 함께 내려간다.",
            "tooltip": "longitudinal family 비선형 정도. 추천 0.5..4.0",
        },
    },
    "transverse_family": {
        LANG_EN: {
            "meaning": "Pick the transverse family that shapes the center-high profile across a single progression slice. Split and merge still derive from the progression guide set directly.",
            "effect_up": "There is no numeric raise direction. Changing the family changes how quickly score decays off-axis. `linear` gives straight flanks, `exponential` gives rounded flanks, and `inverse` / `power` keep longer shoulders.",
            "effect_down": "A gentler family keeps off-axis score alive longer, which can connect to farther good regions more easily.",
            "tooltip": "cross-section function family around the guide center",
        },
        LANG_KO: {
            "meaning": "같은 진행 slice에서 중심이 가장 높게 보이는 횡단면 profile의 함수 family를 고른다. split/merge도 현재는 progression guide 집합에서 바로 계산한다.",
            "effect_up": "숫자 증가 개념은 없다. family를 바꾸면 축 밖 감쇠 모양이 달라진다. `linear`는 직선 flank, `exponential`은 둥근 flank, `inverse` / `power`는 더 긴 shoulder를 만든다.",
            "effect_down": "더 완만한 family로 바꾸면 off-axis 점수가 더 오래 유지되어 멀리 있는 좋은 영역으로 이어질 여지가 커진다.",
            "tooltip": "경로 중심 횡단면 함수 family",
        },
    },
    "transverse_peak": {
        LANG_EN: {
            "meaning": "Set the center maximum of the transverse profile.",
            "effect_up": "The guide center pulls upward more strongly, so the transverse term can dominate more even before longitudinal gain is applied.",
            "effect_down": "The center maximum is weaker, so transverse behaves more like a broad background score than a strong center pull.",
            "tooltip": "center ceiling of the transverse profile. Recommended 0.5..3.0",
        },
        LANG_KO: {
            "meaning": "횡단면 profile의 중심 최대값을 정한다.",
            "effect_up": "guide 중심이 더 강하게 올라가서 longitudinal gain을 더하기 전에도 transverse term이 더 강하게 작용한다.",
            "effect_down": "중심 최대값이 약해져 transverse가 강한 center pull보다 넓은 배경 score에 가까워진다.",
            "tooltip": "횡단면 중심 최대값. 추천 0.5..3.0",
        },
    },
    "transverse_shape": {
        LANG_EN: {
            "meaning": "Set the core shape of the transverse profile near the center. In the exponential family this moves from pointier (`<1`) through exponential (`=1`) toward flatter or more Gaussian-like (`>1`).",
            "effect_up": "The center stays flatter and wider near the axis, while the outer region can still be pressed down later through falloff.",
            "effect_down": "The center becomes pointier and more cusp-like near the axis.",
            "tooltip": "core shape near the transverse center. Recommended 0.5..4.0",
        },
        LANG_KO: {
            "meaning": "횡단면 중심 근처 core shape를 정한다. exponential family에서는 뾰족한 형태(`<1`)부터 지수형(`=1`), 더 펑퍼지거나 Gaussian에 가까운 형태(`>1`)까지 움직인다.",
            "effect_up": "축 근처 중심부가 더 넓고 평평하게 유지되고, 바깥쪽 감소는 falloff로 따로 늦출 수 있다.",
            "effect_down": "축 근처 중심부가 더 뾰족하고 cusp처럼 날카로워진다.",
            "tooltip": "횡단면 중심 core shape. 추천 0.5..4.0",
        },
    },
    "transverse_falloff": {
        LANG_EN: {
            "meaning": "Set the extra outer-tail suppression away from the guide center.",
            "effect_up": "The transverse shoulder gets pressed down more strongly in the far field while the center maximum stays fixed.",
            "effect_down": "The transverse shoulder stays broader and survives farther from the center.",
            "tooltip": "extra outer-tail falloff of the transverse profile. Recommended 0.0..4.0",
        },
        LANG_KO: {
            "meaning": "guide 중심에서 멀어질수록 바깥 tail을 얼마나 더 눌러 내릴지 정한다.",
            "effect_up": "중심 최대값은 유지한 채 먼 바깥쪽 shoulder가 더 강하게 눌려 내려간다.",
            "effect_down": "바깥쪽 shoulder가 더 넓게 살아남아 멀리까지 퍼진다.",
            "tooltip": "횡단면 바깥 tail falloff 추가 강도. 추천 0.0..4.0",
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
            "meaning": "Length of the virtual continuation anchors added beyond the visible guide end for guide-local progress/support sampling.",
            "effect_up": "Guide-local progress/support influence persists longer beyond the visible endpoint, but transverse still uses only raw visible guide geometry.",
            "effect_down": "Guide-local progress/support influence from the guide end dies out sooner.",
            "tooltip": "virtual extension length at the guide end",
        },
        LANG_KO: {
            "meaning": "guide-local progress/support sampling을 위해 guide 끝에 virtual continuation anchor를 얼마나 연장할지 정한다.",
            "effect_up": "visible endpoint 바깥에서도 guide-local progress/support influence가 더 오래 남지만, transverse는 raw visible guide geometry만 따른다.",
            "effect_down": "guide 끝의 progress/support influence가 더 빨리 사라진다.",
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
            "meaning": "Set the lateral Gaussian blend width used inside the guide-local progression kernel.",
            "effect_up": "The lateral blending span grows wider, so guide-local mixing becomes more permissive off-axis.",
            "effect_down": "Lateral locality becomes stronger inside the progression kernel.",
            "tooltip": "lateral sigma width for the progression kernel",
        },
        LANG_KO: {
            "meaning": "guide-local progression kernel 안에서 쓰는 lateral Gaussian blend 폭이다.",
            "effect_up": "lateral blending span이 넓어져 off-axis에서도 guide-local mixing이 더 느슨해진다.",
            "effect_down": "progression kernel 안에서 lateral locality가 더 강해진다.",
            "tooltip": "progression kernel용 lateral sigma 폭",
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
