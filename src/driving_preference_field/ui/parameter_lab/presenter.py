from __future__ import annotations

from dataclasses import fields

from driving_preference_field.comparison_session import ComparisonSession
from driving_preference_field.visualization_scale import display_unit, resolve_display_range


def summarize_diff_array(data) -> dict[str, float]:
    return {
        "min": float(data.min()),
        "max": float(data.max()),
        "mean": float(data.mean()),
    }


def selected_diff_array(comparison_result, selected_channel: str):
    return (
        comparison_result.candidate_raster.channels[selected_channel]
        - comparison_result.baseline_raster.channels[selected_channel]
    )


def effective_context_payload(context) -> dict[str, object]:
    return {
        "effective_ego_pose": {
            "x": context.ego_pose.x,
            "y": context.ego_pose.y,
            "yaw": context.ego_pose.yaw,
        },
        "effective_local_window": {
            "x_min": context.local_window.x_min,
            "x_max": context.local_window.x_max,
            "y_min": context.local_window.y_min,
            "y_max": context.local_window.y_max,
        },
    }


def state_channel_value(state_result, channel_name: str) -> float | None:
    if channel_name in state_result.base_preference_channels:
        return state_result.base_preference_channels[channel_name]
    debug_key_map = {
        "progression_s_hat": "progression_s_hat",
        "progression_center_distance": "progression_center_distance",
        "progression_longitudinal_component": "progression_longitudinal_component",
        "progression_transverse_term": "progression_transverse_term",
        "progression_support_mod": "progression_support_mod",
        "progression_alignment_mod": "progression_alignment_mod",
    }
    if channel_name in debug_key_map:
        return float(state_result.diagnostics[debug_key_map[channel_name]])
    return None


def state_summary_payload(state_result, selected_channel: str) -> dict[str, float]:
    return {
        "progression_total": state_result.base_preference_total,
        "selected_channel_value": state_channel_value(state_result, selected_channel),
    }


def diff_summary_payload(baseline_state, candidate_state, *, selected_channel: str, diff_array) -> dict[str, object]:
    baseline_selected = state_channel_value(baseline_state, selected_channel)
    candidate_selected = state_channel_value(candidate_state, selected_channel)
    return {
        "selected_channel_delta": (
            None
            if baseline_selected is None or candidate_selected is None
            else candidate_selected - baseline_selected
        ),
        "progression_total_delta": candidate_state.base_preference_total - baseline_state.base_preference_total,
        "diff_raster_summary": summarize_diff_array(diff_array),
    }


def display_range(data, *, channel_name: str, scale_mode: str, diff: bool) -> tuple[float, float]:
    return resolve_display_range(
        data,
        channel_name=channel_name,
        scale_mode=scale_mode,
        diff=diff,
    )


def visualization_payload(comparison_result, *, selected_channel: str, scale_mode: str) -> dict[str, object]:
    baseline_data = comparison_result.baseline_raster.channels[selected_channel]
    candidate_data = comparison_result.candidate_raster.channels[selected_channel]
    diff_data = selected_diff_array(comparison_result, selected_channel)
    return {
        "scale_mode": scale_mode,
        "score_sign": "higher is better",
        "progression_surface_kind": "guide-local blended progress coordinates + exact raw-guide distance transverse term + hard max envelope",
        "raster_role": "visualization only",
        "selected_channel_unit": display_unit(selected_channel),
        "diff_unit": display_unit(selected_channel, diff=True),
        "baseline_range": display_range(baseline_data, channel_name=selected_channel, scale_mode=scale_mode, diff=False),
        "candidate_range": display_range(candidate_data, channel_name=selected_channel, scale_mode=scale_mode, diff=False),
        "diff_range": display_range(diff_data, channel_name=selected_channel, scale_mode=scale_mode, diff=True),
    }


def profile_summary_payload(profile_result, *, selected_channel: str) -> dict[str, object]:
    if profile_result is None:
        return {
            "available": False,
            "selected_channel": selected_channel,
        }
    from driving_preference_field.profile_inspection import summarize_profile_result

    summary = summarize_profile_result(profile_result, selected_channel=selected_channel)
    return {
        "available": True,
        **summary,
    }


def progression_target_payload(snapshot) -> dict[str, object] | None:
    guides = snapshot.progression_support.guides
    future_anchor = snapshot.progression_support.future_anchor
    guide_endpoints = [
        {
            "guide_id": guide.guide_id,
            "point": [float(guide.points[-1][0]), float(guide.points[-1][1])],
            "closed_loop": bool(guide.points[0] == guide.points[-1]),
        }
        for guide in guides
    ]
    if future_anchor is not None:
        return {
            "kind": "future_anchor",
            "point": [float(future_anchor[0]), float(future_anchor[1])],
            "guide_endpoints": guide_endpoints,
        }
    if not guide_endpoints:
        return None
    if len(guide_endpoints) == 1:
        return {
            "kind": "guide_endpoint",
            **guide_endpoints[0],
        }
    return {
        "kind": "guide_endpoints",
        "guide_endpoints": guide_endpoints,
    }


def summary_payload(
    *,
    state,
    comparison_result,
    selected_channel: str,
    scale_mode: str,
    profile_result,
    qualitative_note: str,
) -> dict[str, object]:
    baseline_state = comparison_result.baseline_state
    candidate_state = comparison_result.candidate_state
    diff_array = selected_diff_array(comparison_result, selected_channel)
    snapshot_metadata = {} if state.snapshot is None else dict(state.snapshot.metadata)
    return {
        "case": str(state.current_case_path),
        "input_kind": state.current_input_kind,
        "selected_channel": selected_channel,
        "selected_channel_unit": display_unit(selected_channel),
        "scale_mode": scale_mode,
        "score_sign": "higher is better",
        "diff_meaning": "candidate - baseline",
        "progression_surface_kind": "guide-local blended progress coordinates + exact raw-guide distance transverse term + hard max envelope",
        "raster_role": "visualization only",
        "snapshot_metadata": snapshot_metadata,
        "progression_normalization": snapshot_metadata.get("progression_normalization"),
        "progression_target": progression_target_payload(state.snapshot),
        **effective_context_payload(state.working_context),
        "baseline_preset_name": state.baseline_state.preset_name,
        "baseline_preset_display": state.baseline_state.display_name(),
        "baseline_preset_origin": state.baseline_state.metadata.get("origin", "user"),
        "baseline_preset_unsaved": state.baseline_state.unsaved,
        "baseline_longitudinal_frame": state.baseline_config.progression.longitudinal_frame,
        "candidate_preset_name": state.candidate_state.preset_name,
        "candidate_preset_display": state.candidate_state.display_name(),
        "candidate_preset_origin": state.candidate_state.metadata.get("origin", "user"),
        "candidate_preset_unsaved": state.candidate_state.unsaved,
        "candidate_longitudinal_frame": state.candidate_config.progression.longitudinal_frame,
        "baseline": state_summary_payload(baseline_state, selected_channel),
        "candidate": state_summary_payload(candidate_state, selected_channel),
        "baseline_selected_channel_value": state_channel_value(baseline_state, selected_channel),
        "candidate_selected_channel_value": state_channel_value(candidate_state, selected_channel),
        "difference": diff_summary_payload(
            baseline_state,
            candidate_state,
            selected_channel=selected_channel,
            diff_array=diff_array,
        ),
        "profile": profile_summary_payload(profile_result, selected_channel=selected_channel),
        "visualization": visualization_payload(
            comparison_result,
            selected_channel=selected_channel,
            scale_mode=scale_mode,
        ),
        "qualitative_note": qualitative_note,
    }


def build_comparison_session(
    *,
    state,
    comparison_result,
    selected_channel: str,
    scale_mode: str,
    qualitative_note: str,
    baseline_render_summary: dict[str, object],
    candidate_render_summary: dict[str, object],
    profile_summary: dict[str, object],
    exported_at: str,
) -> ComparisonSession:
    baseline_state = comparison_result.baseline_state
    candidate_state = comparison_result.candidate_state
    diff_array = selected_diff_array(comparison_result, selected_channel)
    return ComparisonSession(
        case_path=str(state.current_case_path),
        selected_channel=selected_channel,
        effective_ego_pose=effective_context_payload(state.working_context)["effective_ego_pose"],
        effective_local_window=effective_context_payload(state.working_context)["effective_local_window"],
        baseline_preset=state.current_baseline_preset(),
        candidate_preset=state.current_candidate_preset(),
        baseline_state_summary=state_summary_payload(baseline_state, selected_channel),
        candidate_state_summary=state_summary_payload(candidate_state, selected_channel),
        diff_summary={
            **diff_summary_payload(
                baseline_state,
                candidate_state,
                selected_channel=selected_channel,
                diff_array=diff_array,
            ),
            "raster": summarize_diff_array(diff_array),
            "visualization": visualization_payload(
                comparison_result,
                selected_channel=selected_channel,
                scale_mode=scale_mode,
            ),
        },
        profile_summary=profile_summary,
        baseline_render_summary=baseline_render_summary,
        candidate_render_summary=candidate_render_summary,
        note=qualitative_note,
        exported_at=exported_at,
    )
