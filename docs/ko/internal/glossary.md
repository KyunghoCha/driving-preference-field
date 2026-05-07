# 내부 용어집

## base local reference path cost

obstacle / rule exception을 적용하기 전에, 공간적으로 “어디가 더 바람직한가”를 담는 기본 ordering 구조다.

## input semantics

reference-path cost model를 만들기 위해 외부 source가 제공하는 drivable semantics와 progression semantics 전체를 뜻한다.

## progression semantics

field generator가 progression-tilted ordering structure를 만들 수 있게 해 주는 방향, continuity, branch 관련 의미다.

## local analytic evaluation

조밀한 raster 전체를 만들지 않고도 ego-centric local region에서 field를 직접 평가하는 runtime 방식이다.

## exception layers

reference-path cost model와 동일시하지 않는 safety, rule, dynamic-interaction layer다.

## semantic slots

drivable support, progression support 같은 source-independent canonical 입력 슬롯을 가리키는 내부 용어다.

## hard violation flags

candidate state나 trajectory가 safety/rule/dynamic restriction을 어겼는지 나타내는 boolean 또는 categorical indicator다. base ordering로 상쇄할 수 없는 제한을 뜻한다.
