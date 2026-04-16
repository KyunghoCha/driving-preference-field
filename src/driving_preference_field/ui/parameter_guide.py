from __future__ import annotations

from dataclasses import dataclass


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


PARAMETER_GUIDE_INTRO = (
    "canonical score는 `higher is better`로 읽는다.\n"
    "현재 GUI는 `progression_tilted`를 기준으로 Main + Advanced Surface 파라미터를 수정한다.\n"
    "drivable boundary는 overlay로만 읽고 base heatmap에 더하지 않는다.\n"
    "obstacle / rule / dynamic 채널은 costmap 성격의 시각화로만 남긴다.\n"
    "차이는 `progression_tilted` 채널에서 먼저 확인하는 것이 맞다.\n"
    "Main은 longitudinal frame/term, transverse profile, support ceiling을 다루고, Advanced Surface는 discretization / kernel / modulation / handoff tuning을 다룬다.\n"
    "current implementation은 각 progression guide 안에서 local coordinate를 만들고, guide별 score 가운데 최대값을 최종 field로 읽는다.\n"
    "보이는 guide 끝은 semantic start/end가 아니라 virtual continuation이 붙은 local patch로 읽는다.\n"
    "현재 exact formula는 `score = support_mod * alignment_mod * (transverse_component + longitudinal_gain * longitudinal_component)`다.\n"
    "support / alignment는 shape를 주도하지 않는 약한 secondary modulation이다.\n"
    "같은 진행 slice에서는 중심이 가장 높고, longitudinal tilt가 충분히 강하면 더 먼 좋은 영역이 가까운 중심보다 더 높은 ordering을 만들 수 있다.\n"
    "split/merge는 shared prefix/suffix를 가진 multiple progression guide로 표현하고, raster는 이 continuous function을 local map 위에서 샘플링한 시각화일 뿐이다."
)


PROGRESSION_PARAMETER_GUIDE: dict[str, ParameterGuideEntry] = {
    "longitudinal_frame": ParameterGuideEntry(
        key="longitudinal_frame",
        label="frame",
        meaning="longitudinal tilt를 local map의 절대 progress로 읽을지, ego 기준 progress 차이로 읽을지 고른다.",
        effect_up="숫자 증가 개념은 없다. `local_absolute`는 local map 전체 fabric space의 전역적인 기울기를 만들고, `ego_relative`는 ego 기준 앞쪽 ordering을 더 직접적으로 키운다.",
        effect_down="`ego_relative`에서 `local_absolute`로 바꾸면 바로 앞 ego 기준보다 local map 전체 progress ordering을 더 강하게 본다.",
        practical_band="local_absolute | ego_relative",
        technical_range="local_absolute | ego_relative",
        tooltip="longitudinal tilt 기준 frame",
    ),
    "longitudinal_family": ParameterGuideEntry(
        key="longitudinal_family",
        label="long family",
        meaning="continuous surface 위에서 progression axis를 따라 더 먼 gain을 어떻게 더할지 정하는 longitudinal family를 고른다.",
        effect_up="숫자 증가 개념은 없다. family를 바꾸면 같은 progress 차이에도 ramp 형태가 달라진다.",
        effect_down="가족을 더 완만한 쪽으로 바꾸면 progression gradient가 덜 날카롭게 보인다.",
        practical_band="tanh | linear | inverse | power",
        technical_range="tanh | linear | inverse | power",
        tooltip="progression axis를 따라 점수가 커지는 함수 family",
    ),
    "longitudinal_gain": ParameterGuideEntry(
        key="longitudinal_gain",
        label="long gain",
        meaning="center-high transverse profile 위에 더해지는 longitudinal tilt의 세기를 정한다.",
        effect_up="진행방향으로 갈수록 score 차이가 더 벌어져, 바로 앞 중심을 안 밟고도 더 먼 좋은 영역을 향하는 ordering이 쉬워진다.",
        effect_down="횡단면 중심 profile이 더 지배적이 되어 가까운 중심을 따라가는 성향이 강해진다.",
        practical_band="0.5 .. 3.0",
        technical_range="0.0 .. 1000.0",
        tooltip="진행방향 tilt 세기. 추천 0.5..3.0",
    ),
    "lookahead_scale": ParameterGuideEntry(
        key="lookahead_scale",
        label="long horizon",
        meaning="`ego_relative` frame에서 ego 앞쪽 gain이 얼마나 빨리 포화되는지 정한다. `local_absolute`에서는 영향이 약하거나 없다.",
        effect_up="ego-relative gain이 더 천천히 커져, 멀리 보며 점진적으로 기울어진다.",
        effect_down="ego-relative gain이 더 빨리 커져, 가까운 앞쪽에서도 tilt가 강하게 나타난다.",
        practical_band="0.1 .. 1.0",
        technical_range="0.0 .. 1000.0",
        tooltip="진행방향 tilt 누적 속도. 추천 0.1..1.0",
    ),
    "longitudinal_shape": ParameterGuideEntry(
        key="longitudinal_shape",
        label="long shape",
        meaning="선택한 longitudinal family의 곡률이나 nonlinearity 정도를 정한다.",
        effect_up="family가 허용하는 범위 안에서 더 급하거나 더 늦게 커지는 ramp가 된다.",
        effect_down="family가 허용하는 범위 안에서 더 완만하고 덜 공격적인 ramp가 된다.",
        practical_band="0.5 .. 4.0",
        technical_range="0.0 .. 1000.0",
        tooltip="longitudinal family 비선형 정도. 추천 0.5..4.0",
    ),
    "transverse_family": ParameterGuideEntry(
        key="transverse_family",
        label="trans family",
        meaning="같은 진행 slice에서 중심이 가장 높게 보이는 횡단면 profile의 함수 family를 고른다. split/merge도 현재는 progression guide 집합에서 바로 계산한다.",
        effect_up="숫자 증가 개념은 없다. family를 바꾸면 축 밖 감쇠 모양이 달라진다.",
        effect_down="더 완만한 family로 바꾸면 off-axis 점수가 더 오래 유지되어 멀리 있는 좋은 영역으로 이어질 여지가 커진다.",
        practical_band="exponential | inverse | power",
        technical_range="exponential | inverse | power",
        tooltip="경로 중심 횡단면 함수 family",
    ),
    "transverse_scale": ParameterGuideEntry(
        key="transverse_scale",
        label="trans scale",
        meaning="continuous surface에서 중심 횡단면이 얼마나 넓게 퍼질지 정한다.",
        effect_up="축에서 조금 멀어져도 점수가 덜 줄어들어 field가 더 넓게 퍼진다.",
        effect_down="축을 벗어나면 점수가 더 빨리 줄어들어 field가 더 좁아진다.",
        practical_band="0.25 .. 3.0",
        technical_range="0.0 .. 1000.0",
        tooltip="경로 중심 횡단면 폭. 추천 0.25..3.0",
    ),
    "transverse_shape": ParameterGuideEntry(
        key="transverse_shape",
        label="trans shape",
        meaning="선택한 transverse family의 횡단면 곡률을 정한다.",
        effect_up="축 밖 점수가 더 급하게 줄거나, family에 따라 중심부와 바깥부의 contrast가 커진다.",
        effect_down="축 주변이 더 완만해지고 퍼진다.",
        practical_band="0.5 .. 4.0",
        technical_range="0.0 .. 1000.0",
        tooltip="횡단면 곡률. 추천 0.5..4.0",
    ),
    "support_ceiling": ParameterGuideEntry(
        key="support_ceiling",
        label="support cap",
        meaning="guide weight와 confidence가 progression surface 전체에 주는 보조 scale의 상한이다.",
        effect_up="support가 높은 guide의 기여를 더 많이 허용한다.",
        effect_down="support가 높아도 일정 수준 이상 progression 점수가 세지지 않게 막는다.",
        practical_band="0.25 .. 1.0",
        technical_range="0.0 .. 1000.0",
        tooltip="guide support 상한. 추천 0.25..1.0",
    ),
    "anchor_spacing_m": ParameterGuideEntry(
        key="anchor_spacing_m",
        label="anchor spacing",
        meaning="guide anchor를 몇 m 간격으로 배치할지 정한다.",
        effect_up="anchor가 성기어져 계산량은 줄지만 local coordinate와 support field가 더 거칠어질 수 있다.",
        effect_down="anchor가 촘촘해져 shape는 더 안정적일 수 있지만 계산량이 늘어난다.",
        practical_band="0.05 .. 2.0",
        technical_range="0.05 .. 2.0",
        tooltip="anchor 간격",
    ),
    "spline_sample_density_m": ParameterGuideEntry(
        key="spline_sample_density_m",
        label="spline density",
        meaning="guide polyline을 densify할 때 세그먼트를 얼마나 촘촘히 샘플링할지 정한다.",
        effect_up="샘플이 성기어져 계산량은 줄지만 곡선의 smooth resampling 품질이 낮아질 수 있다.",
        effect_down="샘플이 촘촘해져 곡선 fidelity는 좋아질 수 있지만 계산량이 늘어난다.",
        practical_band="0.01 .. 1.0",
        technical_range="0.01 .. 1.0",
        tooltip="spline densification 간격",
    ),
    "spline_min_subdivisions": ParameterGuideEntry(
        key="spline_min_subdivisions",
        label="min subdivisions",
        meaning="짧은 세그먼트에서도 유지할 최소 subdivision 수다.",
        effect_up="짧은 구간도 더 많이 쪼개 곡선 fidelity가 올라갈 수 있지만 계산량이 늘어난다.",
        effect_down="짧은 세그먼트의 resampling이 더 거칠어질 수 있다.",
        practical_band="1 .. 64",
        technical_range="1 .. 64",
        tooltip="최소 subdivision 수",
    ),
    "end_extension_m": ParameterGuideEntry(
        key="end_extension_m",
        label="end extension",
        meaning="guide 끝에 virtual continuation anchor를 얼마나 연장할지 정한다.",
        effect_up="visible endpoint 근처 end-cap artifact를 줄이고 끝 이후 continuation을 더 길게 허용한다.",
        effect_down="guide 끝 influence가 더 빨리 사라진다.",
        practical_band="0.0 .. 10.0",
        technical_range="0.0 .. 10.0",
        tooltip="guide 끝 연장 길이",
    ),
    "min_sigma_t": ParameterGuideEntry(
        key="min_sigma_t",
        label="min sigma_t",
        meaning="longitudinal Gaussian support의 최소 폭이다.",
        effect_up="guide 축 방향 influence가 더 넓게 퍼진다.",
        effect_down="guide 축 방향 support가 더 빠르게 줄어든다.",
        practical_band="0.05 .. 5.0",
        technical_range="0.05 .. 5.0",
        tooltip="longitudinal support 최소 폭",
    ),
    "min_sigma_n": ParameterGuideEntry(
        key="min_sigma_n",
        label="min sigma_n",
        meaning="lateral Gaussian support의 최소 폭이다.",
        effect_up="축 밖 support가 더 넓게 퍼진다.",
        effect_down="축 밖 support가 더 빨리 줄어든다.",
        practical_band="0.05 .. 5.0",
        technical_range="0.05 .. 5.0",
        tooltip="lateral support 최소 폭",
    ),
    "sigma_t_scale": ParameterGuideEntry(
        key="sigma_t_scale",
        label="sigma_t scale",
        meaning="guide length와 lookahead를 longitudinal sigma로 바꾸는 scale이다.",
        effect_up="longitudinal blending span이 길어져 guide-local coordinate가 더 멀리 섞인다.",
        effect_down="longitudinal locality가 강해진다.",
        practical_band="0.05 .. 5.0",
        technical_range="0.05 .. 5.0",
        tooltip="longitudinal sigma scale",
    ),
    "sigma_n_scale": ParameterGuideEntry(
        key="sigma_n_scale",
        label="sigma_n scale",
        meaning="transverse_scale을 lateral sigma로 바꾸는 scale이다.",
        effect_up="lateral blending span이 넓어져 ridge가 더 퍼질 수 있다.",
        effect_down="lateral locality가 강해진다.",
        practical_band="0.05 .. 5.0",
        technical_range="0.05 .. 5.0",
        tooltip="lateral sigma scale",
    ),
    "support_base": ParameterGuideEntry(
        key="support_base",
        label="support base",
        meaning="support modulation의 바닥값이다.",
        effect_up="support가 낮아도 score가 덜 꺼진다.",
        effect_down="support quality가 낮을 때 score가 더 많이 줄어든다.",
        practical_band="0.0 .. 1.0",
        technical_range="0.0 .. 1.0",
        tooltip="support modulation 바닥값",
    ),
    "support_range": ParameterGuideEntry(
        key="support_range",
        label="support range",
        meaning="support quality가 modulation에 줄 수 있는 변화량이다.",
        effect_up="support quality의 영향이 더 커진다.",
        effect_down="support modulation이 더 평평해진다.",
        practical_band="0.0 .. 1.0",
        technical_range="0.0 .. 1.0",
        tooltip="support modulation 변화량",
    ),
    "alignment_base": ParameterGuideEntry(
        key="alignment_base",
        label="alignment base",
        meaning="heading alignment modulation의 바닥값이다.",
        effect_up="heading이 어긋나도 score가 덜 깎인다.",
        effect_down="heading mismatch penalty가 더 강해진다.",
        practical_band="0.0 .. 1.0",
        technical_range="0.0 .. 1.0",
        tooltip="alignment modulation 바닥값",
    ),
    "alignment_range": ParameterGuideEntry(
        key="alignment_range",
        label="alignment range",
        meaning="heading alignment quality가 modulation에 줄 수 있는 변화량이다.",
        effect_up="heading alignment의 영향이 더 커진다.",
        effect_down="alignment modulation이 더 평평해진다.",
        practical_band="0.0 .. 1.0",
        technical_range="0.0 .. 1.0",
        tooltip="alignment modulation 변화량",
    ),
    "transverse_handoff_support_ratio": ParameterGuideEntry(
        key="transverse_handoff_support_ratio",
        label="handoff support ratio",
        meaning="transverse handoff candidate guide를 고를 때 dominant support 대비 최소 비율이다.",
        effect_up="candidate guide가 더 엄격하게 걸러져 handoff가 더 hard해진다.",
        effect_down="더 많은 guide가 handoff smoothing에 참여한다.",
        practical_band="0.0 .. 1.0",
        technical_range="0.0 .. 1.0",
        tooltip="handoff candidate 최소 support 비율",
    ),
    "transverse_handoff_score_delta": ParameterGuideEntry(
        key="transverse_handoff_score_delta",
        label="handoff score delta",
        meaning="transverse handoff candidate guide를 고를 때 dominant score와 허용 차이다.",
        effect_up="더 많은 근접 guide가 candidate로 남는다.",
        effect_down="candidate guide가 더 엄격하게 줄어든다.",
        practical_band="0.0 .. 2.0",
        technical_range="0.0 .. 2.0",
        tooltip="handoff candidate score 허용 차",
    ),
    "transverse_handoff_temperature": ParameterGuideEntry(
        key="transverse_handoff_temperature",
        label="handoff temperature",
        meaning="candidate guide 사이 transverse blending의 soft weighting temperature다.",
        effect_up="guide handoff가 더 부드럽게 퍼진다.",
        effect_down="guide handoff가 dominant guide 쪽으로 더 hard하게 수렴한다.",
        practical_band="0.01 .. 1.0",
        technical_range="0.01 .. 1.0",
        tooltip="handoff smoothing temperature",
    ),
}

ADVANCED_PARAMETER_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "Discretization",
        (
            "anchor_spacing_m",
            "spline_sample_density_m",
            "spline_min_subdivisions",
            "end_extension_m",
        ),
    ),
    (
        "Support Kernel",
        (
            "min_sigma_t",
            "min_sigma_n",
            "sigma_t_scale",
            "sigma_n_scale",
        ),
    ),
    (
        "Modulation",
        (
            "support_base",
            "support_range",
            "alignment_base",
            "alignment_range",
        ),
    ),
    (
        "Handoff",
        (
            "transverse_handoff_support_ratio",
            "transverse_handoff_score_delta",
            "transverse_handoff_temperature",
        ),
    ),
)

PANEL_NOTE_TEXT = (
    "Current GUI edits `progression_tilted` through Main + Advanced Surface controls.\n"
    "Read drivable boundary as overlay and obstacle/rule/dynamic as costmap."
)


def _main_keys() -> list[str]:
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


def parameter_help_html() -> str:
    main_rows = []
    for key in _main_keys():
        entry = PROGRESSION_PARAMETER_GUIDE[key]
        main_rows.append(
            f"""
            <tr>
              <td><code>{entry.label}</code></td>
              <td>{entry.practical_band}</td>
              <td>{entry.technical_range}</td>
              <td>{entry.tooltip}</td>
            </tr>
            """
        )

    advanced_rows = []
    for _, keys in ADVANCED_PARAMETER_GROUPS:
        for key in keys:
            entry = PROGRESSION_PARAMETER_GUIDE[key]
            advanced_rows.append(
                f"""
                <tr>
                  <td><code>{entry.label}</code></td>
                  <td>{entry.practical_band}</td>
                  <td>{entry.technical_range}</td>
                  <td>{entry.tooltip}</td>
                </tr>
                """
            )

    detail_sections = []
    for key in [*_main_keys(), *(key for _, keys in ADVANCED_PARAMETER_GROUPS for key in keys)]:
        entry = PROGRESSION_PARAMETER_GUIDE[key]
        detail_sections.append(
            f"""
            <div class="param-card">
              <h3><code>{entry.label}</code></h3>
              <table class="detail-table">
                <tr><th>Meaning</th><td>{entry.meaning}</td></tr>
                <tr><th>Affects</th><td><code>progression_tilted</code> only</td></tr>
                <tr><th>Higher</th><td>{entry.effect_up}</td></tr>
                <tr><th>Lower</th><td>{entry.effect_down}</td></tr>
                <tr><th>Practical Band</th><td><code>{entry.practical_band}</code></td></tr>
                <tr><th>Technical Range</th><td><code>{entry.technical_range}</code></td></tr>
              </table>
            </div>
            """
        )

    intro_items = "".join(f"<li>{line}</li>" for line in PARAMETER_GUIDE_INTRO.splitlines())
    return f"""
    <html>
      <head>
        <style>
          body {{
            font-family: 'Noto Sans CJK KR', 'Noto Sans', 'Malgun Gothic', sans-serif;
            font-size: 14px;
            line-height: 1.45;
            color: #202124;
          }}
          h1 {{ font-size: 28px; margin: 4px 0 12px 0; }}
          h2 {{ font-size: 20px; margin: 22px 0 10px 0; }}
          h3 {{ font-size: 17px; margin: 0 0 8px 0; }}
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
          .summary-table, .detail-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 8px 0 16px 0;
          }}
          .summary-table th, .summary-table td,
          .detail-table th, .detail-table td {{
            border: 1px solid #d8dee6;
            padding: 8px 10px;
            vertical-align: top;
          }}
          .summary-table th, .detail-table th {{
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
        <h1>Parameter Guide</h1>

        <div class="callout">
          <h2 style="margin-top:0;">Current Truth</h2>
          <ul>{intro_items}</ul>
        </div>

        <h2>Quick Reference</h2>
        <h3>Main</h3>
        <table class="summary-table">
          <tr>
            <th>Parameter</th>
            <th>Practical Band</th>
            <th>Technical Range</th>
            <th>Quick Meaning</th>
          </tr>
          {''.join(main_rows)}
        </table>

        <h3>Advanced Surface</h3>
        <table class="summary-table">
          <tr>
            <th>Parameter</th>
            <th>Practical Band</th>
            <th>Technical Range</th>
            <th>Quick Meaning</th>
          </tr>
          {''.join(advanced_rows)}
        </table>

        <h2>Per-Parameter Details</h2>
        {''.join(detail_sections)}

        <div class="callout">
          <h2 style="margin-top:0;">Scale Reading</h2>
          <ul>
            <li><code>Fixed</code>: 해석 기준. 같은 채널이면 baseline/candidate가 같은 색-값 대응을 공유한다.</li>
            <li><code>Normalized</code>: 탐색용. 현재 화면 값 범위를 다시 매핑한다.</li>
            <li><code>Diff</code>: 항상 <code>candidate - baseline</code>이다.</li>
            <li><code>Score sign</code>: canonical은 항상 <code>higher is better</code>로 읽는다.</li>
            <li><code>Current implementation</code>: smooth skeleton anchor를 좌표 control point로 쓰는 Gaussian-blended whole-fabric field다.</li>
            <li><code>Raster</code>: PNG/GUI heatmap은 field 본체가 아니라 local map 위에서 함수를 샘플링한 결과다.</li>
          </ul>
        </div>
      </body>
    </html>
    """
