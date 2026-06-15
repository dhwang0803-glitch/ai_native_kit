# Architecture

> 레이어/흐름/경계를 기술. (`docs` 브랜치에서만 편집)

## 레이어 (의존성 방향: 안쪽 ← 바깥쪽)

Clean Architecture의 **의존성 방향 원칙**을 프론트엔드 규모로 적용한다.
(packages/modules/services 모노레포는 단일 배포에 과해 채택하지 않음.)

```
src/domain/        타입·모델 SSOT                     ← 최내곽, 프레임워크 무관
   ↑
src/data/          데이터 접근 (API/콘텐츠 → domain)   ← domain만 의존
   ↑
src/components/    UI 프레젠테이션 (domain 타입 props)  ← data 직접 호출 금지
   ↑
src/app/ (pages)   라우트/페이지 (Composition Root)     ← data 호출 + components 조립
```

- **규칙**: `components`는 `data`를 import하지 않는다. 데이터는 **페이지가 주입**한다.

## 데이터 흐름

```
TODO: 대표 화면의 데이터 흐름을 기록하세요. 예:
[데이터 소스(API/콘텐츠)] → src/data(로더/클라이언트) → domain 타입
  → src/app 페이지(로드+조립) → src/components(렌더) → 배포 산출물
```

## 경계 및 계약

| 경계 | 인터페이스 | SSOT |
|------|-----------|------|
| TODO 데이터 소스 ↔ 코드 | API 스키마 / 콘텐츠 frontmatter | `docs/specs/data.md` |
| data ↔ ui | domain 타입(props) | `docs/specs/domain.md` |
| 라우팅 | 페이지 경로 | `docs/specs/ui.md` |

## 관련 문서

- 설계 결정: [`decisions.md`](./decisions.md) · 파일 맵: [`MAP.md`](./MAP.md)
