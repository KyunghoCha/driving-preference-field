from driving_preference_field.ui.help.render import parameter_help_html
from driving_preference_field.ui.locale import LANG_EN, LANG_KO


def test_parameter_help_html_has_reference_first_sections_in_english_and_korean() -> None:
    help_en = parameter_help_html(LANG_EN)
    help_ko = parameter_help_html(LANG_KO)

    assert "What This Page Is For" in help_en
    assert "When to Use Main" in help_en
    assert "When to Open Advanced Surface" in help_en
    assert "Parameter Groups" in help_en
    assert "Detailed Reference" in help_en

    assert "이 페이지의 역할" in help_ko
    assert "`Main`을 먼저 볼 때" in help_ko
    assert "`Advanced Surface`를 여는 때" in help_ko
    assert "Parameter groups" in help_ko
    assert "세부 참고" in help_ko


def test_parameter_help_keeps_main_and_advanced_surface_distinct() -> None:
    help_en = parameter_help_html(LANG_EN)
    help_ko = parameter_help_html(LANG_KO)

    assert "Guide" in help_en and "Parameters" in help_en
    assert "Guide" in help_ko and "Parameters" in help_ko
    assert "anchor spacing" in help_en
    assert "anchor spacing" in help_ko
    assert "candidate - baseline" in help_en
    assert "candidate - baseline" in help_ko
