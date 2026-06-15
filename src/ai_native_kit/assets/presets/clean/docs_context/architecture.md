# Architecture

> 프로젝트 전체 아키텍처(레이어/흐름/경계)를 기술한다. (`docs` 브랜치에서만 편집)
> 데이터 경로·실행 모드·Repository 간 쓰기 순서가 바뀌면 갱신한다.

## 레이어 개요

```
TODO: 레이어 구조를 기록하세요. 예시(Clean Architecture):

┌────────────────────────────────────────────┐
│ Frontend Layer    services/frontend/        │
├────────────────────────────────────────────┤
│ Core API Layer    services/api_server/      │
├────────────────────────────────────────────┤
│ Domain Layer      modules/*                  │
├────────────────────────────────────────────┤
│ Persistence Layer database/ · modules/storage/ │
├────────────────────────────────────────────┤
│ Foundation        packages/<shared_schemas> │
└────────────────────────────────────────────┘
```

## 데이터 흐름 (대표 시나리오)

```
TODO: 가장 대표적인 end-to-end 시나리오 한두 개의 데이터 흐름을 기록하세요.
[사용자 요청] → [API] → [도메인] → [영속화] → [응답] 형태로,
어느 모듈이 누구를 호출하고 무엇을 쓰/읽는지 명시.
```

## 경계 및 계약

| 경계 | 인터페이스 | 스키마 SSOT |
|------|-----------|-------------|
| TODO Frontend ↔ API | REST / SSE | 공유 스키마 (TS) |
| TODO API ↔ Domain | import | 공유 스키마 (Python) |
| TODO Domain ↔ Persistence | Repository 패턴 | `storage/repositories/` |

## 관련 문서

- 설계 결정 배경: [`decisions.md`](./decisions.md)
- 파일 맵: [`MAP.md`](./MAP.md)
