# {{PROJECT_NAME}} — Claude Code 지침

> AI_Native_Kit `frontend` 프리셋으로 생성된 골격입니다. 프로젝트에 맞게 채우세요.
> 정적/SPA 프론트엔드용 — 모노레포(packages/modules/services) 대신 **레이어 구조**.

## 프로젝트 개요

TODO: 이 프론트엔드가 무엇을 하는지 2~3문장으로. (예: 정적 사이트 / SPA / 대시보드)

---

## 아키텍처 (의존성 방향 — 절대 위반 금지)

Clean Architecture의 **의존성 방향 원칙**을 프론트엔드 규모로 적용한다. 단일 배포이므로
packages/modules/services 모노레포는 쓰지 않고 `src/` 레이어로 나눈다.

```
src/domain/       타입·모델 SSOT (Entity, ViewModel)       ← 최내곽, 프레임워크 무관
   ↑
src/data/         데이터 접근 (API 클라이언트 / 콘텐츠 로딩) ← domain만 의존
   ↑
src/components/   UI 프레젠테이션 (재사용 컴포넌트)          ← domain 타입을 props로
   ↑
src/app/ (pages)  라우트/페이지 (Composition Root)          ← data 호출 + components 조립
```

> `content`/파일 기반 사이트면 `src/data/`를 `src/content/`로 불러도 된다.

### 금지
- `src/components/`에서 `src/data/`(또는 `fetch`/`fs`)를 직접 호출 금지 — 데이터는 **페이지가 주입**.
- `src/domain/`에 UI 프레임워크(React 등) import 금지 (순수 타입).
- 컴포넌트가 자체 타입을 재정의 금지 — `src/domain` SSOT 사용.

---

## 구현 명세 (docs/specs) — SSOT

| 위치 | 역할 |
|------|------|
| `docs/specs/<area>.md` | 영역(도메인/데이터/UI)별 설계 SSOT — 코드 PR과 함께 갱신 |
| `<area> 컴포넌트의 props 계약` | `docs/specs/ui.md` |

> 신규 화면/기능은 `/spec-design`으로 PRD에서 영역 분해 + spec + 스캐폴드를 먼저 만든다.

---

## 기술 스택 / 컨벤션

- **JS/TS** lint: `{{JS_LINT}}`, test/build: `{{JS_TEST}}`
- (서버리스 함수/스크립트에 Python 사용 시) lint: `{{PY_LINT}}`, test: `{{PY_TEST}}`
- 컴포넌트 PascalCase, 그 외 camelCase. props/함수에 타입 명시.
- 경로 별칭 권장: `@/*` → `src/*`.

---

## 위키 (docs/context) — 결정/아키텍처 SSOT

- `MAP.md`(구조) · `architecture.md`(레이어/흐름) · `decisions.md`(ADR 인덱스).
- **`docs/context/`는 `docs` 브랜치에서만 편집** (코드 PR과 분리). `docs/specs/`는 코드와 함께 갱신.

---

## 브랜치 전략

| 브랜치 | 용도 |
|--------|------|
| `{{BASE_BRANCH}}` | 안정 브랜치 (프로덕션 배포) |
| `{{INTEGRATION_BRANCH}}` | 통합 브랜치 — feature PR base |
| `feature/*` | 기능 단위 개발 |
| `docs` | 위키 편집 전용 |

---

## 슬래시 커맨드 (`.claude/commands/`)

| 커맨드 | 용도 |
|--------|------|
| `/spec-design` | PRD → 아키텍처 → 영역 분해 → spec → 스캐폴딩 |
| `/pr-report` | 커밋 → 보안점검 → 위키감사 → PR |
| `/pr-3axis-review` | PR 3축 리뷰 |
| `/release-sync` | `{{INTEGRATION_BRANCH}}` → `release` 동기화 |
| `/adr` | 새 ADR 생성 + 인덱스 갱신 (`docs` 브랜치) |

---

## 보안

- 비밀키/토큰 하드코딩 금지. 클라이언트 번들에 시크릿을 넣지 않는다 (공개됨).
- `.env`, `*.pem`, `*.key`, `credentials.json`, `.claude/settings.local.json`은 `.gitignore`에 필수.
- 공개 가능한 값만 클라이언트 노출 (예: 공개 API 베이스 URL).

---

## 설치 점검

Claude Code 버전 업데이트 후 하니스가 멀쩡한지 `ai-native-kit doctor`로 점검한다.
