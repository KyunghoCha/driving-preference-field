# 설계 문서 형태와 current-thread-first source 범위

## Date

- 2026-04-18

## Topic

- `owner design doc shape and current-thread-first source`

## Source sessions

- current active DPF thread after the gate-intuition cluster; later portions of the thread were not yet materialized under `$HOME/.codex/sessions/...` at edit time
- early source anchor confirmed in `$HOME/.codex/sessions/2026/03/18/rollout-2026-03-18T03-56-06-019cfd27-be1f-7671-a901-4be788cca7bd.jsonl`

## User original messages

> 저거밖에 없어? 예전 저저번주부터 한 대화가 엄청 많을텐데 그리고 내가 생각한 총 정리는 저거보다는 design문서? 그런 느낌? 너가 정리를 해서 철학이나 개념이나 그런 섹션들을 최신화 하고 필요하면 추가하고 그런거지 이해가 됬나? 그니까 선호장 섹션 수식섹션 이런것들 내가 한거는 거의 철학이나 개념이겠지만 가장 최신에 내 생각들을 추적해서 정리를 하는 느낌이었어 이해가 됬나? 내가 설명을 잘 못하겠네

> 그리고 설계 문서는 저런 메타는 필요 없고 설계만 깔끔하게 정리를 해줘

> 그리고 raw에 보니까 1번 2번 이런게 대화에 있는데 그게 뭔지 안보여서 그거도 조치가 필요할듯 /home/ckh/Projects/driving-preference-field/docs/raw/notes/2026-04-17-dpf-as-progress-preference-device.md 이런거 skill도 업데이트 하고 내 프롬프트에 매몰되서 최대한 똑같게 안해도 되 그건 알지?

> 대화를 다 뽑아온게 아니구나 아직 할거야 아니면 못하는거야?

> /home/ckh/Projects/driving-preference-field/docs/raw/owner_design_notebook.md 얘는 raw/notes 를 기준으로 해야되 꼭 그러고 있어?

> 그리고 이 세션의 대화만 뽑으면 될거 같은데 그게 뭔지는 알잖아 그거기 열어서 쭉 올라가면 되지 딱히 다른데서 설계나 개념 대화를 하진 않았어

## Assistant context (optional)

- 당시 대화에서 assistant는 `owner_design_notebook.md`가 raw나 tracker와 다른 역할을 가져야 한다는 점을 분리했다. raw는 원문 보존, tracker는 변화 추적, design 문서는 최신 사용자 설계 thinking의 clean prose라는 식으로 역할을 나눴다.
- 이후 사용자가 design 문서는 raw/notes를 기준으로 해야 하고, broad historical archaeology보다 현재 세션 자체를 authoritative source로 쓰는 쪽이 맞다고 더 명확히 잠갔다.

## Open questions at the time

- active thread later segment가 materialize된 뒤 source 표기를 언제 갱신할지
- design 문서와 canonical explanation 사이의 거리를 얼마나 유지할지
- raw/tracker/design의 세 층을 앞으로 어떤 주기로 같이 갱신할지
