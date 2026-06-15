# {{PROJECT_NAME}} — Claude Code 지침

> 이 파일은 AI_Native_Kit가 생성한 골격입니다. 프로젝트 도메인에 맞게 채우세요.
> TODO 표시는 프로젝트별로 작성이 필요한 부분입니다.

## 프로젝트 개요

TODO: 이 프로젝트가 무엇을 하는지 2~3문장으로 서술하세요.

---

## 브랜치 전략

| 브랜치 | 용도 |
|--------|------|
| `{{BASE_BRANCH}}` | 안정 브랜치 (protected, 릴리즈 시점에만 merge) |
| `{{INTEGRATION_BRANCH}}` | 통합 브랜치 — feature PR의 base |
| `feature/*` | 기능 단위 개발 |
| `hotfix/*` | 안정화/배포 단계 버그 |
| `docs` | 문서 전용 |

| 변경 유형 | 방식 |
|----------|------|
| 기능 구현/변경 | `feature/*` → `{{INTEGRATION_BRANCH}}` PR (리뷰 후 merge) |
| 자잘한 수정 (문서/설정/오타) | 현재 브랜치에서 커밋 → PR (리뷰 필수) |
| 릴리즈 | `{{INTEGRATION_BRANCH}}` → `{{BASE_BRANCH}}` PR |

---

## 에이전트 템플릿

TDD 사이클 및 코드 리뷰에 사용하는 에이전트 템플릿은 `_agent_templates/`에 위치한다.
새 브랜치 체크아웃 시 `.githooks/post-checkout`이 `{브랜치}/agents/`로 자동 복사한다.

| 에이전트 | 역할 |
|---------|------|
| `ORCHESTRATOR` | TDD 사이클 전체 관리, 에이전트 순서 호출 |
| `TEST_WRITER` | TDD Red — 실패 테스트 작성 |
| `DEVELOPER` | TDD Green — 테스트 통과 최소 구현 |
| `TESTER` | 테스트 실행 및 결과 수집 |
| `REFACTOR` | TDD Refactor — 코드 품질 개선 |
| `REVIEW` | 방어적 코드 리뷰 (8축 점검) |
| `SECURITY_AUDITOR` | 보안 감사 (자격증명/PII 노출 탐지) |
| `IMPACT_ASSESSOR` | PR 전 사후영향 평가 |
| `REPORTER` | 결과 보고서 생성 |

---

## 아키텍처: Clean Architecture (의존성 방향 절대 위반 금지)

```
packages/<shared_schemas>/   ← 최내곽 (Pydantic 등 순수 타입만 의존)
        ↑ import
modules/*/domain/            ← shared_schemas + 자기 도메인만 import
        ↑ import
modules/*/application/        ← domain/* (Port 인터페이스만) + shared_schemas
        ↑ import
modules/*/adapters/           ← domain/ports + 외부 라이브러리
modules/<storage>/            ← 영속화 인프라 — 다른 모듈의 Port ABC 구현
        ↑ import
services/*/                   ← 모든 modules/* 조립 (Composition Root)
```

### 금지 사항

- `domain/` 레이어에서 프레임워크 import 금지 (FastAPI, SQLAlchemy, LangGraph, Celery 등)
- `application/` 레이어에서 구체 Adapter 직접 import 금지 (Port ABC만 참조)
- ORM 모델이 도메인 경계를 넘어가는 것 금지
- `modules/` 간 직접 import 시 상대 모듈의 `domain/ports/`·`domain/entities/`·`domain/value_objects/`만 참조
- `modules/` → `services/` 역방향 의존 금지 (services만 modules 조립)

### Port → Adapter 매핑 (DI 참조표)

> 새 Port를 추가하면 이 표에 행을 추가하세요.

| Port (ABC) 정의 위치 | Adapter 구현 위치 |
|--------------------|----------------|
| TODO `<module>/domain/ports/<Port>` | TODO `<storage>/repositories/` 또는 `<module>/adapters/` |

### 공유 타입은 단일 정의 (SSOT)

- 여러 모듈이 공유하는 엔티티/VO/Enum은 **공유 스키마 패키지**에 단일 정의
- 모듈별 자체 재정의 금지
- Enum은 `str` 상속으로 JSON 직렬화 호환 (`class RiskLevel(str, Enum)`)

---

## 구현 명세 (docs/specs) — 무엇/어떻게의 SSOT

설계 SSOT는 두 겹이다. `docs/context`(위키 = "왜")와 별개:

| 위치 | 역할 | 갱신 규칙 |
|------|------|----------|
| `docs/specs/<module>.md` | 모듈 설계 SSOT (계층별 클래스·시그니처·의존성·환경변수) | **코드 PR과 함께** 갱신 |
| `modules/<module>/README.md` | 모듈 사용 계약(Public API) SSOT | 공개 API 변경 시 |

> use case 시그니처·엔티티 필드·enum이 코드와 spec 사이에서 어긋나면 결함이다.
> 신규 모듈/기능은 `/spec-design`으로 PRD에서 spec + 스캐폴드를 먼저 만든다.

---

## 새 코드 작성 절차

1. **spec·README 읽기**: 작업할 모듈의 `docs/specs/<module>.md`와 `README.md`를 먼저 읽는다
2. **의존성 확인**: 의존성 방향 규칙에 따라 import 가능 여부 확인
3. **레이어 배치**: `domain` / `application` / `adapters` 중 어디인지 판단
4. **공유 타입 사용**: 도메인 엔티티/VO/Enum은 공유 스키마 패키지에서 import
5. **Port 정의/구현 분리**: 인터페이스는 소유 모듈 `domain/ports/`, 구현은 영속화 모듈 또는 자체 `adapters/`
6. **보안 점검**: 하드코딩 금지, `.env` 읽기 금지

---

## 보안 규칙 (필수)

- API 키/비밀번호/토큰 하드코딩 금지 → `os.getenv()` / `process.env` 경유
- `os.getenv("X", "기본값")`의 기본값에 실제 IP·DB명·계정 금지 (표준 포트만 허용)
- `.env`, `*.pem`, `*.key`, `credentials.json`, `.claude/settings.local.json`은 `.gitignore`에 필수
- 자세한 점검 항목은 `_agent_templates/SECURITY_AUDITOR.md` 참조

---

## 컨벤션

- **Python** ≥ {{PYTHON_MIN}}, lint: `{{PY_LINT}}` (line-length={{PY_LINE_LENGTH}}), test: `{{PY_TEST}}`
- **JS/TS** lint: `{{JS_LINT}}`, test: `{{JS_TEST}}`
- 타입 힌트/타입 명시 필수
- 파일명 `snake_case` (Python) / 컨벤션 준수 (JS/TS)
- ID 필드는 `UUID` 타입
- Optional은 `T | None`

---

## 프로젝트 위키 (docs/context) — 공용 지식 베이스 SSOT

`docs/context/`는 팀/에이전트가 공유하는 **단일 진실 공급원(SSOT) 지식 베이스**다.
코드만 봐서는 알 수 없는 "왜"와 "전제"를 여기에 남겨 drift를 막는다.

| 파일 | 역할 | 갱신 시점 |
|------|------|----------|
| `docs/context/MAP.md` | 최상위 폴더 지도 | 새 최상위 폴더 생길 때만 |
| `docs/context/architecture.md` | 레이어/데이터 흐름/경계·계약 | 데이터 경로·실행 모드 변경 시 |
| `docs/context/decisions.md` | ADR 인덱스 + 비-ADR 결정 메모 | 결정 추가/반전 시 |
| `docs/context/adr/ADR-NNNN-*.md` | 개별 결정 기록 (1결정 1파일) | 결정마다 (`/adr`로 생성) |

### 운영 규칙 (필수)

1. **위키는 `docs` 브랜치에서만 편집한다.** 코드 브랜치 PR에 `docs/context/`를 절대
   섞지 않는다 (섞였으면 stash/복원 후 중단, `docs` 브랜치로 별도 PR).
2. **ADR 불변성**: 결정을 뒤집어도 원본 ADR을 삭제하지 않는다. 원본에
   `Superseded by ADR-NNNN` 표기 + 새 ADR 추가.
3. **Decision Audit** (PR 직전): "이 변경의 결정을 모르면 다른 작업자가 잘못된 전제로
   일하는가? + 현재 위키만 읽어 파악 가능한가?" → 전자 Yes·후자 No면 위키 갱신 필요.
   `/pr-report`가 이 감사를 수행한다.
4. `.githooks/post-checkout`은 `docs` 브랜치를 작업 폴더 스캐폴딩에서 제외한다.

> `docs` 브랜치가 없으면 `git branch docs`로 먼저 만든다.

---

## 슬래시 커맨드

`.claude/commands/`에 위치. (AI_Native_Kit 제공 재사용 커맨드)

| 커맨드 | 용도 |
|--------|------|
| `/spec-design` | PRD → 아키텍처 설계 → 모듈 분해 → 모듈별 spec + 모노레포 스캐폴딩 |
| `/pr-report` | 커밋 → 보안 점검 → 위키 감사 → PR 생성 자동화 |
| `/pr-3axis-review` | PR 3축 리뷰 (Clean Architecture / SSOT / 크로스 모듈 안전성) |
| `/release-sync` | `{{INTEGRATION_BRANCH}}` → `release` 충돌 없는 동기화 |
| `/adr` | 새 ADR 생성 + `decisions.md` 인덱스 갱신 (`docs` 브랜치 전용) |

---

## 설치 점검

Claude Code 버전 업데이트 후 하니스가 멀쩡한지 `ai-native-kit doctor`로 점검한다
(에셋·git 훅·.gitignore·CC 버전·알려진 quirk).
