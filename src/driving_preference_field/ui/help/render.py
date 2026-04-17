from __future__ import annotations

import html
import re
from dataclasses import dataclass

from driving_preference_field.ui.help.catalog import ADVANCED_PARAMETER_GROUPS, MAIN_PARAMETER_KEYS, PARAMETER_SPECS
from driving_preference_field.ui.help.copy import PANEL_NOTE_TEXT, PARAMETER_GUIDE_INTRO, PARAMETER_TEXTS, SECTION_TITLES
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


def _normalize_language(language: str) -> str:
    return language if language in {LANG_EN, LANG_KO} else DEFAULT_LANGUAGE


def _entry(language: str, key: str) -> ParameterGuideEntry:
    spec = PARAMETER_SPECS[key]
    copy_block = PARAMETER_TEXTS[key][_normalize_language(language)]
    return ParameterGuideEntry(
        key=key,
        label=spec.label,
        meaning=copy_block["meaning"],
        effect_up=copy_block["effect_up"],
        effect_down=copy_block["effect_down"],
        practical_band=spec.practical_band,
        technical_range=spec.technical_range,
        tooltip=copy_block["tooltip"],
    )


def panel_note_text(language: str) -> str:
    return PANEL_NOTE_TEXT[_normalize_language(language)]


def section_title(language: str, key: str) -> str:
    return SECTION_TITLES[_normalize_language(language)][key]


def progression_parameter_guide(language: str) -> dict[str, ParameterGuideEntry]:
    lang = _normalize_language(language)
    return {key: _entry(lang, key) for key in PARAMETER_SPECS}


def main_parameter_keys() -> list[str]:
    return list(MAIN_PARAMETER_KEYS)


def _inline_code_html(text: str) -> str:
    escaped = html.escape(text)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)


def _summary_table(
    guide: dict[str, ParameterGuideEntry],
    keys: list[str] | tuple[str, ...],
    *,
    anchor: str,
    title: str,
    language: str,
) -> str:
    lang = _normalize_language(language)
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


def parameter_help_html(language: str = DEFAULT_LANGUAGE) -> str:
    lang = _normalize_language(language)
    guide = progression_parameter_guide(lang)

    advanced_sections = [
        _summary_table(
            guide,
            keys,
            anchor=f"group-{group_key.replace('_', '-')}",
            title=section_title(lang, group_key),
            language=lang,
        )
        for group_key, keys in ADVANCED_PARAMETER_GROUPS
    ]

    detail_keys = [*MAIN_PARAMETER_KEYS, *(key for _, keys in ADVANCED_PARAMETER_GROUPS for key in keys)]
    detail_sections = []
    for key in detail_keys:
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

    intro_items = "".join(f"<li>{_inline_code_html(line)}</li>" for line in PARAMETER_GUIDE_INTRO[lang].splitlines())
    if lang == LANG_EN:
        title = "Parameter Help"
        intro_paragraph = (
            "This page is the control reference for the right-hand <code>Parameters</code> dock. "
            "<code>Guide</code> covers the workflow; this page explains when to touch a knob and what changes when the value moves."
        )
        page_purpose_title = "What This Page Is For"
        main_title = "When to Use Main"
        main_intro = (
            "Start here when you are deciding field semantics: longitudinal frame, family, gain, transverse profile, and support ceiling. "
            "Read <code>progression_tilted</code> on <code>Fixed</code> scale first."
        )
        advanced_title = "When to Open Advanced Surface"
        advanced_intro = (
            "Open this only after the semantics are clear. "
            "This section tunes discretization, support kernels, and modulation quality."
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
        main_intro = (
            "field semantics를 읽을 때는 여기서 시작한다. longitudinal frame, family, gain, transverse profile, support ceiling을 먼저 본다. "
            "먼저 <code>progression_tilted</code>를 <code>Fixed</code> scale로 읽는다."
        )
        advanced_title = "`Advanced Surface`를 여는 때"
        advanced_intro = (
            "semantics가 먼저 잡힌 뒤에만 연다. 이 섹션은 discretization, support kernel, modulation 품질을 다룬다."
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
        ]
        detail_title = "세부 참고"
        detail_intro = "아래 lookup card는 값을 올릴지 내릴지 빠르게 결정할 때 쓴다."

    interpretation_html = "".join(f"<li>{item}</li>" for item in interpretation_items)
    groups_links_html = "".join(f'<li><a href="{target}">{html.escape(label)}</a></li>' for label, target in groups_links)
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
        <h1>{title}</h1>
        <h2 id="page-purpose">{page_purpose_title}</h2>
        <p>{intro_paragraph}</p>
        <div class="callout">
          <ul>{intro_items}</ul>
        </div>

        <h2 id="when-main">{main_title}</h2>
        <p>{main_intro}</p>
        {_summary_table(guide, MAIN_PARAMETER_KEYS, anchor="group-longitudinal", title=section_title(lang, "longitudinal"), language=lang)}
        {_summary_table(guide, ("transverse_family", "transverse_scale", "transverse_shape"), anchor="group-transverse", title=section_title(lang, "transverse"), language=lang)}
        {_summary_table(guide, ("support_ceiling",), anchor="group-support-gate", title=section_title(lang, "support_gate"), language=lang)}

        <h2 id="when-advanced">{advanced_title}</h2>
        <p>{advanced_intro}</p>
        <h3 id="group-advanced-surface">{section_title(lang, "advanced")}</h3>
        {''.join(advanced_sections)}

        <h2 id="interpret-effects">{interpretation_title}</h2>
        <ul>{interpretation_html}</ul>

        <h2 id="parameter-groups">{groups_title}</h2>
        <p>{groups_intro}</p>
        <ul class="link-list">{groups_links_html}</ul>

        <h2 id="detailed-reference">{detail_title}</h2>
        <p>{detail_intro}</p>
        {''.join(detail_sections)}
      </body>
    </html>
    """


__all__ = [
    "ParameterGuideEntry",
    "main_parameter_keys",
    "panel_note_text",
    "parameter_help_html",
    "progression_parameter_guide",
    "section_title",
]
