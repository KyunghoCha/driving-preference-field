# 입력 Capability Tier 문서

작성일: 2026-04-08

## 문서 목적

이 문서는 canonical input contract를 구현 관점에서 어떤 입력 사례가 어느 정도까지 채울 수 있는지 reading 수준으로 정리한다.

이 문서는 canonical 정의 문서가 아니다.

## Tier 1. Sensor-Only Local Input

이 tier는 map이나 global route 없이 local perception 중심으로 semantic slot을 채우는 경우다.

- 상대적으로 잘 채우는 slot:
  - drivable support
  - boundary / interior support
  - exception-layer support
- 상대적으로 약한 slot:
  - progression support
  - branch / continuity support

즉 sensor-only는 local field를 만드는 데는 충분할 수 있지만, 강한 progression structure는 약할 수 있다.

현재 toy 예시:

- `sensor_patch_open.yaml`
- `sensor_patch_narrow.yaml`
- `sensor_patch_blocked.yaml`
- `merge_like_patch.yaml`

## Tier 2. Map-Assisted Input

이 tier는 local perception에 lane, route, map continuity 같은 구조가 더해진 경우다.

- 잘 채우는 slot:
  - drivable support
  - progression support
  - boundary / interior support
- 보강되는 slot:
  - branch / continuity support

즉 map-assisted는 local geometry와 progression structure를 함께 제공할 수 있다.

## Tier 3. Rich Structured Input

이 tier는 local perception, map semantics, route continuity, branch relation, operational context가 함께 존재하는 경우다.

- 잘 채우는 slot:
  - drivable support
  - progression support
  - boundary / interior support
  - branch / continuity support
  - exception-layer support

즉 canonical input contract를 가장 풍부하게 채울 수 있는 경우다.

## 현재 기준 결론

capability tier는 canonical 정의가 아니라, 어떤 입력 사례가 semantic slot을 어느 정도까지 채울 수 있는지를 설명하는 reading 구조다.
