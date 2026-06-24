# Changelog

이 프로젝트의 주요 변경 사항을 기록한다.
형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)를 따르며,
버전 관리는 [Semantic Versioning](https://semver.org/lang/ko/)을 따른다.

---

## [Unreleased]

### Added
- **자동 스킬 호출 규칙** — CLAUDE.md 템플릿(clean/frontend)에 트리거→스킬 매핑 테이블 추가. 훅 기반 자동화에서 CLAUDE.md 지침 기반으로 전환 (Windows 호환성 해결)
  - PR 생성 → `/pr-report` → `/session-retro` → `/cross-verify pr` 체인 자동 실행
  - 수동 `gh pr create` 금지 규칙 명시
- **탐색 결과 검증 절차** — "새 코드 작성 절차"에 sub-agent(Explore) 보고 결과를 Grep으로 교차 확인하는 단계 추가 (channeltalk에서 잘못된 클래스명 사용으로 ImportError 발생 방지)
- **크로스 모듈 일관성 검증** — ORCHESTRATOR에 병렬 sub-agent 실행 후 Port↔Adapter 시그니처 일치, 공유 스키마 일관성, 의존성 방향을 점검하는 7-b 단계 추가
- **DEVELOPER 린트 의무화** — 구현 완료 후 커밋 전에 `{{PY_LINT}} --fix` / `{{JS_LINT}} --fix` 실행 필수 (sub-agent가 린트 미실행하여 42건 누적 방지)
- **ExitPlanMode 교차검증 훅** — 세션 훅에 ExitPlanMode PostToolUse 리마인더 추가, 계획 단계에서 아키텍처 문제(dual-write 등) 사전 발견

### Changed
- CLAUDE.md 세션 훅: `Bash` matcher → `Bash|PowerShell` (Windows 호환)
- CLAUDE.md 세션 훅 역할: "강제 게이트" → "백업 리마인더" (실제 자동화는 자동 스킬 호출 규칙이 담당)
- 교차 검증 의무 시점 테이블: 2열→3열 (자동화 컬럼 추가)
- REVIEW 에이전트 축7: sub-agent 탐색 결과 불일치 검증 항목 + Major 판정 추가

## [0.2.0] - 2026-06-23

### Added
- `/pr-report` 자동 트리거 — PR 생성 후 `/session-retro` 자동 실행 + `/cross-verify` 실행 여부 제안
  - 세션 회고: PR 생성 직후 자동 (별도 질문 없이)
  - 교차 검증: 코드 변경 포함 PR은 실행 권장, 문서만 변경 시 건너뛰기 기본

## [0.1.0] - 2026-06-23

### Added
- **교차 모델 검증 파이프라인** (`/cross-verify`) — Codex를 통한 독립적 교차 검증
  - 3단계 우선순위: CLI 직접 실행 → MCP 폴백 → 수동 모드
  - CLI 모드(`codex review --base main`)에서 Codex가 파일 시스템 직접 접근, 컨텍스트 손실 없음
  - MCP 모드 트러블슈팅 5항목 문서화 (auth.json 우선순위, BOM 인코딩, .env 변수명 등)
  - 교차 검증 가이드 (`docs/context/cross-verify-guide.md`)
- **세션 회고** (`/session-retro`) — 계획 vs 실제 비교, Keep/Drop/Try 패턴 분석, 하네스 개선 제안
- **pre-commit 훅** (`.githooks/pre-commit`) — 보안 점검(하드코딩/`.env*` 누출) + 린트(ruff/eslint), 실패 시 커밋 차단
- **코드 설계 품질 규칙** — CLAUDE.md에 클래스 기반 설계 필수, SOLID 5원칙, 디자인 패턴 7종, 복잡도 제한 추가
- **REVIEW 에이전트 9축** — 기존 8축에 "코드 설계 품질" 축 추가 (함수 기반 감지, SRP/OCP/DIP 위반, God Object)
- **DEVELOPER 에이전트** — 클래스 기반+SOLID 구현 원칙, 금지 패턴 코드 예시, 복잡도 제한 표
- **REFACTOR 에이전트** — "코드 설계 품질" 카테고리 신설, SOLID 위반별 전환 가이드
- **SPEC_TEMPLATE** — 클래스 관계 다이어그램 + 디자인 패턴 표 섹션 의무화
- **`/spec-design`** — 클래스 다이어그램 + 디자인 패턴 명시 필수 단계 추가
- **doctor** — pre-commit 훅 존재/LF/shebang 점검 항목 추가
- **자기 편향 방지 규칙** — CLAUDE.md에 자기 평가 금지 + 교차 검증 의무 시점 명시

### Fixed
- pre-commit `.env` 변형 파일(`.env.local`, `.env.production`) 보안 게이트 누락 — Codex 교차 검증으로 발견
- pre-commit `ai-native-kit.toml` 린트 설정 무시 문제 (ruff 항상 우선 실행) — Codex 교차 검증으로 발견

## [0.0.1] - 2026-06-22

### Added
- **초기 패키지 릴리즈** — `pip install ai-native-kit`
- `ai-native-kit init` — 에셋을 프로젝트에 설치 (프리셋: `clean`/`frontend`)
- `ai-native-kit doctor` — 설치된 하니스 자가 진단
- `ai-native-kit doctor --drift` — docs ↔ 코드 drift 감지 (MAP.md, spec, CLAUDE.md 경로)
- `ai-native-kit list` — 번들 에셋 목록 출력
- TDD/리뷰 서브에이전트 9종 (ORCHESTRATOR, TEST_WRITER, DEVELOPER, TESTER, REFACTOR, REVIEW, SECURITY_AUDITOR, IMPACT_ASSESSOR, REPORTER)
- 슬래시 커맨드 5종 (spec-design, pr-report, pr-3axis-review, release-sync, adr)
- post-checkout 훅 (브랜치 자동 스캐폴딩)
- 3계층 컨텍스트 엔지니어링 구조 (Schema → Wiki → Source)
- README 문서화 — 설치, 사용법, 3계층 구조 설명, drift 감지

---

[Unreleased]: https://github.com/dhwang0803-glitch/ai_native_kit/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/dhwang0803-glitch/ai_native_kit/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/dhwang0803-glitch/ai_native_kit/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/dhwang0803-glitch/ai_native_kit/releases/tag/v0.0.1
