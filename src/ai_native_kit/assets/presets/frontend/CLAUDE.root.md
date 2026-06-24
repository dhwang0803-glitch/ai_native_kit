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

## 코드 설계 품질 규칙 (필수)

### 클래스/컴포넌트 기반 설계

- 도메인 모델(`src/domain/`)은 **클래스 또는 타입으로 정의**. 인라인 객체 리터럴로 도메인을 표현하지 않는다.
- 데이터 접근(`src/data/`)은 클래스(Repository/Client) 또는 커스텀 훅으로. 컴포넌트에서 `fetch` 직접 호출 금지.
- 컴포넌트는 프레젠테이션 책임만. 비즈니스 로직은 `src/domain/`에, 데이터 로딩은 `src/data/`에.

### 복잡도 규칙

| 규칙 | 기준 |
|------|------|
| 조건문 깊이 | if/else 3단 이상 중첩 금지 → Early return, 다형성 |
| 컴포넌트 크기 | 200줄 초과 시 분리 |
| Props 수 | 7개 초과 시 합성 컴포넌트 패턴 또는 Context 검토 |
| 반복 로직 | 3곳 이상 반복 시 커스텀 훅 또는 유틸로 추출 |

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

## 보안

- 비밀키/토큰 하드코딩 금지. 클라이언트 번들에 시크릿을 넣지 않는다 (공개됨).
- `.env`, `*.pem`, `*.key`, `credentials.json`, `.claude/settings.local.json`은 `.gitignore`에 필수.
- 공개 가능한 값만 클라이언트 노출 (예: 공개 API 베이스 URL).

---

## 자기 편향 방지 규칙 (필수)

LLM은 같은 세션에서 자기 산출물을 평가하면 **자기 편향(self-bias)** 이 발생한다.

### 금지

- **같은 세션에서 자기 코드를 "잘 짰다"고 평가하지 않는다.** 테스트 통과 여부는 보고하되, 품질 판정은 교차 검증이나 사람에게 맡긴다.
- **하드코딩/회피 패턴**: 테스트 통과만을 위한 하드코딩, `return true`, 빈 `catch {}`, 임시 값 고정 — 감지 즉시 수정.

### 교차 검증 (opt-in)

`/cross-verify`로 Codex(외부 모델)의 독립 검증을 실행할 수 있다. Codex MCP 설정이 필요하며, 가이드는 `docs/context/cross-verify-guide.md`를 참조.

| 시점 | 명령 | 자동화 |
|------|------|--------|
| 설계 완료 후 | `/cross-verify spec` | `ExitPlanMode` PostToolUse 훅이 리마인더 자동 출력 |
| 구현 1차 완료 후 | `/cross-verify code` | 수동 |
| PR 생성 전 | `/cross-verify pr` | `/pr-report`에서 자동 제안 |

> 계획 확정 시 `ExitPlanMode` 훅이 자동으로 교차검증 리마인더를 출력한다 (`.claude/settings.json`).

---

## 검증 훅 (Evaluation Loop)

| 훅 | 트리거 | 동작 |
|----|--------|------|
| `.githooks/pre-commit` | `git commit` | 보안 점검 + 린트 자동 실행. 실패 시 커밋 차단 |
| `.githooks/post-checkout` | 새 브랜치 생성 | 에이전트 템플릿 + 폴더 스캐폴딩 자동 생성 |

### 세션 훅 (`.claude/settings.json`)

| 이벤트 | 동작 |
|--------|------|
| `UserPromptSubmit` | 세션 컨텍스트 로드 (아키텍처·보안 규칙 + 교차 검증 리마인더) |
| `PostToolUse` (Bash\|PowerShell, `git commit` 포함) | 세션 회고 리마인더 출력 |
| `PostToolUse` (ExitPlanMode) | 계획 교차검증 리마인더 출력 |

> 훅은 백업 리마인더다. 실제 자동화는 아래의 "자동 스킬 호출 규칙"이 담당한다.

---

## 슬래시 커맨드 (스킬)

`.claude/commands/`에 위치. Claude Code가 Skill 도구로 호출한다.

| 커맨드 | 용도 |
|--------|------|
| `/spec-design` | PRD → 아키텍처 → 영역 분해 → spec → 스캐폴딩 |
| `/pr-report` | 커밋 → 보안점검 → 위키감사 → PR |
| `/pr-3axis-review` | PR 3축 리뷰 |
| `/cross-verify` | 교차 모델 검증 — Claude 산출물을 Codex가 독립 검증 (opt-in, MCP 필요) |
| `/session-retro` | 세션 회고 — 계획 vs 실제 비교, 패턴 분석, 하네스 개선 제안 |
| `/release-sync` | `{{INTEGRATION_BRANCH}}` → `release` 동기화 |
| `/adr` | 새 ADR 생성 + 인덱스 갱신 (`docs` 브랜치) |

---

## 자동 스킬 호출 규칙 (MANDATORY)

아래 트리거 조건이 충족되면 Claude는 **사용자 확인 없이** 해당 스킬을 Skill 도구로 자동 실행한다. "리마인더만 출력"이 아니라 **실제 스킬을 invoke**하는 것이 핵심이다. 훅은 백업 리마인더일 뿐, 진짜 자동화는 이 규칙이다.

### 트리거 → 스킬 매핑

| 트리거 (사용자 의도) | 자동 실행 스킬 | 체인 |
|---------------------|--------------|------|
| "PR 만들어줘", "PR 생성", "PR 올려줘" 등 PR 생성 요청 | `/pr-report` | → `/session-retro` → `/cross-verify pr` 제안 |
| "리뷰해줘", "PR 리뷰", PR 번호 언급 + 리뷰 | `/pr-3axis-review {PR번호}` | 단독 |
| "설계해줘", PRD 제시 + 구조 설계 | `/spec-design` | 단독 |
| "릴리즈", "release 동기화" | `/release-sync` | 단독 |
| "ADR 작성", 아키텍처 결정 기록 | `/adr {제목}` | 단독 |
| "교차 검증", "cross-verify" | `/cross-verify` | 단독 |
| "회고", "세션 회고", "retro" | `/session-retro` | 단독 |

### 체인 실행 규칙

`/pr-report`는 다음 체인을 포함한다 (pr-report.md Step 3~4에 명시됨):

1. 보안 점검 + 위키 감사 (Step 2~2b)
2. **`/session-retro` 자동 실행** (Step 3) — PR 생성 전에 회고를 먼저 수행
3. **`/cross-verify` 실행 여부를 사용자에게 제안** (Step 4)
   - 코드 파일 변경 포함 → "실행 권장"
   - 문서만 변경 → "건너뛰기 기본"
   - P1/P2 지적 시 즉시 수정 후 커밋에 포함
4. 커밋 → push → **PR 생성** (Step 5~7) — 회고·검증 결과를 PR 본문에 포함

### 매칭 규칙

- 사용자가 한국어/영어 어느 쪽으로 요청하든 의도를 파악하여 매칭한다
- 부분 매칭도 허용: "이거 커밋하고 PR까지" → `/pr-report` 트리거
- 명시적으로 `/커맨드명`을 타이핑하면 해당 스킬을 그대로 실행한다
- **수동 PR 생성 금지**: 사용자가 PR을 요청하면 `gh pr create`를 직접 쓰지 말고 반드시 `/pr-report`를 통해 생성한다

---

## 설치 점검

Claude Code 버전 업데이트 후 하니스가 멀쩡한지 `ai-native-kit doctor`로 점검한다.
