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
    "현재 GUI는 `progression_tilted`만 직접 수정한다.\n"
    "drivable boundary와 branch guides는 overlay로만 읽고 base heatmap에 더하지 않는다.\n"
    "safety / rule / dynamic burden은 costmap 성격의 시각화 채널로만 남긴다.\n"
    "차이는 `progression_tilted` 채널에서 먼저 확인하는 것이 맞다.\n"
    "현재 progression 파라미터는 longitudinal frame/term, transverse profile, support ceiling을 다룬다.\n"
    "current implementation은 smooth skeleton anchor들을 공간 좌표 추정용 control point로 쓰고, Gaussian elliptical blend로 whole-fabric continuous function over local space를 만든다.\n"
    "보이는 guide 끝은 semantic start/end가 아니라 virtual continuation이 붙은 local patch로 읽는다.\n"
    "현재 exact formula는 `score = support_mod * alignment_mod * (transverse_component + longitudinal_gain * longitudinal_component)`다.\n"
    "support / alignment는 shape를 주도하지 않는 약한 secondary modulation이다.\n"
    "같은 진행 slice에서는 중심이 가장 높고, longitudinal tilt가 충분히 강하면 더 먼 좋은 영역이 가까운 중심보다 더 높은 ordering을 만들 수 있다.\n"
    "branch 사이도 nearest-winner 없이 fabric-like surface로 이어지며, raster는 이 함수를 샘플링한 시각화일 뿐이다."
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
        meaning="같은 진행 slice에서 중심이 가장 높게 보이는 횡단면 profile의 함수 family를 고른다. branch 사이는 Gaussian-blended space coordinates 위에서 자동으로 메워진다.",
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
}


PANEL_NOTE_TEXT = (
    "Current GUI edits `progression_tilted` only.\n"
    "Read drivable/branch as overlays and safety as costmap burden."
)


def _ordered_keys() -> list[str]:
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
    rows = []
    for key in _ordered_keys():
        entry = PROGRESSION_PARAMETER_GUIDE[key]
        rows.append(
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
    for key in _ordered_keys():
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
        <table class="summary-table">
          <tr>
            <th>Parameter</th>
            <th>Practical Band</th>
            <th>Technical Range</th>
            <th>Quick Meaning</th>
          </tr>
          {''.join(rows)}
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
