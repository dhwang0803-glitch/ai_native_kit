# AI_Native_Kit

매 프로젝트마다 손으로 다시 세팅하던 **AI-Native Engineering 하니스(harness)** 를
한 번의 명령으로 새 프로젝트에 주입하는 라이브러리.

Claude Code 작업에 항상 깔던 ① TDD/리뷰 서브에이전트 템플릿, ② 브랜치 자동
스캐폴딩 git 훅, ③ 재사용 PR/리뷰 슬래시 커맨드, ④ Clean Architecture 프리셋
`CLAUDE.md` 골격을 패키징해 둔다. `ai-native-kit init` 한 줄이면 현재 프로젝트에
복사 + 렌더링 + git 훅 설정까지 끝난다.

---

## 설치

```bash
pip install ai-native-kit
# 또는 개발 중인 로컬 체크아웃에서:
pip install -e .
```

런타임 의존성 0개 (stdlib `tomllib`만 사용, Python ≥ 3.11).

## 사용법

```bash
cd my-new-project
ai-native-kit init            # 현재 디렉토리에 주입
```

명령어:

| 명령 | 설명 |
|------|------|
| `ai-native-kit init [경로]` | 에셋을 프로젝트에 설치 (기본 경로: 현재 디렉토리) |
| `ai-native-kit doctor [경로]` | 설치된 하니스 자가 진단 (CC 버전 업데이트 후 권장) |
| `ai-native-kit doctor --drift` | 자가 진단 + **docs ↔ 코드 drift 감지** |
| `ai-native-kit list` | 번들된 에셋 + 프리셋 목록 출력 |
| `ai-native-kit --version` | 버전 출력 |

`init` 옵션:

| 옵션 | 설명 |
|------|------|
| `--preset <name>` | 아키텍처 프리셋 (`clean` 기본 / `frontend`). config보다 우선 |
| `--force` | 이미 존재하는 파일도 덮어쓰기 (기본은 건너뜀) |
| `--with-config` | 편집용 `ai-native-kit.toml`도 함께 생성 |
| `--no-claude` | 루트 `CLAUDE.md` 골격 생성 생략 |
| `--no-hook` | git `core.hooksPath` 자동 설정 생략 |

짧은 별칭 `aink`도 동일하게 동작한다.

### 아키텍처 프리셋

| 프리셋 | 적합 | 차이 |
|--------|------|------|
| `clean` (기본) | 백엔드/멀티서비스 | Clean Architecture **모노레포** (packages/modules/services + domain/application/adapters) |
| `frontend` | 정적/SPA 단일 배포 | CA **레이어 구조** (`src/{domain,data,components,app}`) — 모노레포 오버헤드 제거, 의존성 방향 원칙 유지 |

프리셋은 `CLAUDE.md`와 `docs/context/{MAP,architecture}.md`를 프로젝트 성격에 맞게 바꾼다.
나머지 에셋(에이전트·커맨드·훅·spec 템플릿)은 공유된다. 예: `ai-native-kit init --preset frontend`

---

## 핵심 설계: 3계층 컨텍스트 엔지니어링

AI_Native_Kit의 컨텍스트 관리는 Andrej Karpathy의 **LLM Wiki 패턴**과 동일한 3계층 구조다.
LLM이 매번 전체 코드베이스를 다시 읽지 않도록, 압축된 지식 계층을 유지해 **토큰 사용량을 최대 85% 절감**한다.

```
┌─────────────────────────────────────────────────────────┐
│  Layer 3 — 스키마 (CLAUDE.md)                           │
│  "지식의 헌법" — 아키텍처 규칙, 의존성 방향, 보안 정책,   │
│  컨벤션을 한 파일에 집약. LLM이 매 세션 시작 시 로드.     │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Layer 2 — 위키 (docs/context/)                   │  │
│  │  "축적되는 장기 기억" — MAP, architecture, ADR로    │  │
│  │  코드만 봐서는 알 수 없는 "왜"와 "전제"를 기록.     │  │
│  │  ┌─────────────────────────────────────────────┐  │  │
│  │  │  Layer 1 — 원본 (코드 + docs/specs/)         │  │  │
│  │  │  "진실의 원천" — 실제 코드와 모듈별 설계 명세. │  │  │
│  │  │  LLM이 필요할 때만 참조 (Read/Grep).          │  │  │
│  │  └─────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 왜 이 구조가 토큰을 절감하는가

| 전통적 방식 | AI_Native_Kit |
|------------|---------------|
| 매 세션마다 코드를 처음부터 탐색 | CLAUDE.md가 아키텍처·규칙·경로를 즉시 제공 |
| 과거 결정을 매번 재추론 | docs/context/ 위키가 결정 이력을 축적 |
| 전체 파일을 읽어야 구조 파악 | MAP.md 한 파일로 프로젝트 지형도 전달 |
| 반복 질문 "이건 왜 이렇게?" | ADR이 결정 배경을 영구 보존 |

실제 프로젝트(FlowIt — 5인 멀티에이전트 플랫폼)에서 컨텍스트 엔지니어링 적용 결과,
세션당 컨텍스트 토큰이 **5,350 → 800 토큰으로 85% 감소** — 성능은 유지하면서 비용과
응답 지연이 대폭 줄었다.

### Layer 3: 스키마 — `CLAUDE.md`

프로젝트의 **통제 센터**. LLM이 세션 시작 시 자동으로 읽는 단일 파일에 다음을 집약:

| 섹션 | 역할 |
|------|------|
| 프로젝트 개요 | 무엇을 하는 프로젝트인지 2-3문장 |
| 아키텍처 규칙 | 의존성 방향, 레이어 간 import 금지 사항 (위반 즉시 감지) |
| 보안 규칙 | 하드코딩 금지, `.env` 읽기 금지, gitignore 필수 항목 |
| 컨벤션 | 린트/테스트 명령, 타입 힌트 필수, 파일명 규칙 |
| 에이전트 참조 | TDD 사이클에 사용할 에이전트와 순서 |
| 위키 운영 규칙 | docs 브랜치 분리, ADR 불변성, Decision Audit |

프리셋(`clean`/`frontend`)에 따라 아키텍처 섹션이 자동으로 달라진다.

### Layer 2: 위키 — `docs/context/`

코드만 봐서는 알 수 없는 **"왜"와 "전제"** 를 기록하는 지식 베이스.
코드 PR과 분리해 `docs` 브랜치에서만 편집하여 drift를 방지한다.

| 파일 | 역할 | 갱신 시점 |
|------|------|----------|
| `MAP.md` | 최상위 폴더 지도 — LLM이 프로젝트 구조를 즉시 파악 | 새 최상위 폴더 추가 시 |
| `architecture.md` | 레이어/데이터 흐름/경계·계약 | 데이터 경로·실행 모드 변경 시 |
| `decisions.md` | ADR 인덱스 + 비-ADR 결정 메모 | 결정 추가/반전 시 |
| `adr/ADR-NNNN-*.md` | 개별 결정 기록 (1결정 1파일, 불변) | `/adr`로 생성 |

#### 위키 운영 규칙

1. **docs 브랜치 분리**: 위키는 코드 브랜치에서 절대 수정하지 않는다.
   코드 PR에 `docs/context/`가 섞이면 stash/복원 후 별도 PR로 분리.
2. **ADR 불변성**: 결정을 뒤집어도 원본을 삭제하지 않고 `Superseded by ADR-NNNN` 표기.
3. **Decision Audit**: `/pr-report`가 PR 직전 "이 결정을 모르면 다른 작업자가 잘못된
   전제로 작업하는가?" 자문 → Yes이면 위키 갱신 필요 판정.
4. `post-checkout` 훅은 `docs` 브랜치를 폴더 스캐폴딩에서 자동 제외.

### Layer 1: 원본 — 코드 + `docs/specs/`

실제 코드와 모듈별 설계 명세. LLM은 Layer 3(CLAUDE.md) → Layer 2(위키)로
필요한 맥락을 확보한 뒤, Layer 1은 **필요한 파일만 선택적으로** 읽는다.

SSOT는 **두 겹**이다:
- `docs/specs/<module>.md` — 모듈 설계 SSOT (계층별 클래스·시그니처·의존성)
- `modules/<module>/README.md` — 모듈 공개 API 계약 SSOT

> Spec ↔ 코드가 어긋나면 결함이다. `/pr-3axis-review`가 이 정합성을 3축으로 검증한다.

---

## Drift 감지 (`doctor --drift`)

프로젝트가 커지면 문서와 코드가 어긋난다. `doctor --drift`는 이 staleness를 자동 감지한다.

```bash
ai-native-kit doctor --drift
```

| 점검 항목 | 감지 내용 |
|-----------|----------|
| **MAP.md drift** | MAP.md에 기록된 디렉토리 vs 실제 파일시스템 비교 — 신규 폴더 누락, 삭제된 폴더 잔존 |
| **Spec drift** | `docs/specs/`의 spec 파일 vs `modules/`의 모듈 디렉토리 비교 — spec 없는 모듈, 모듈 없는 orphan spec |
| **CLAUDE.md paths** | CLAUDE.md에서 참조하는 경로(`modules/`, `services/` 등)가 실제로 존재하는지 확인 |

```
$ ai-native-kit doctor --drift
  [ OK ] agent templates: 9 file(s) at _agent_templates/
  [ OK ] slash commands: 5 file(s) at commands/
  ...
  [WARN] MAP.md drift: dirs exist but not in MAP.md: new_service
  [WARN] spec drift: modules without spec: payment
  [WARN] CLAUDE.md paths: 1 path(s) not found on disk: modules/legacy/
```

기존 `doctor`(에셋 존재·git 훅·.gitignore·CC 버전)는 `--drift` 없이도 항상 실행된다.

---

## 무엇이 설치되나

```
<project>/
├── _agent_templates/          # TDD/리뷰 서브에이전트 9종
│   ├── ORCHESTRATOR.md            (TDD 사이클 전체 관리)
│   ├── TEST_WRITER.md / DEVELOPER.md / TESTER.md / REFACTOR.md
│   ├── REVIEW.md                  (8축 방어적 코드 리뷰)
│   ├── SECURITY_AUDITOR.md        (S01~S09 보안 스캔)
│   ├── IMPACT_ASSESSOR.md         (PR 전 사후영향 평가)
│   └── REPORTER.md
├── _claude_templates/
│   └── CLAUDE_DEFAULT.md       # 브랜치별 CLAUDE.md 기본 템플릿
├── _module_templates/
│   └── README.md                  # 모듈 공개 API(Public API) README 템플릿
├── .claude/commands/          # 재사용 슬래시 커맨드 5종
│   ├── spec-design.md            (PRD → 아키텍처 → 모듈 분해 → spec → 스캐폴딩)
│   ├── pr-report.md               (커밋 → 보안점검 → 위키 감사 → PR 자동화)
│   ├── pr-3axis-review.md         (Clean Architecture/SSOT/크로스모듈 3축 리뷰)
│   ├── release-sync.md           (충돌 없는 release 동기화)
│   └── adr.md                     (새 ADR 생성 + 인덱스 갱신)
├── docs/
│   ├── context/               # 위키 — Layer 2 (결정/아키텍처 = "왜")
│   │   ├── MAP.md                 (프로젝트 구조 지도)
│   │   ├── architecture.md        (레이어/데이터 흐름/경계)
│   │   ├── decisions.md           (ADR 인덱스 + 결정 메모)
│   │   └── adr/ADR-0000-template.md
│   └── specs/                 # 원본 — Layer 1 (모듈 설계 SSOT)
│       ├── README.md / SPEC_TEMPLATE.md
│       └── plan/PLAN_TEMPLATE.md
├── .githooks/post-checkout    # 새 브랜치 체크아웃 시 자동 스캐폴딩
└── CLAUDE.md                  # 스키마 — Layer 3 (프로젝트 지침 골격)
```

### Spec 기반 설계 흐름 (PRD → 모듈 SSOT → 구현)

```
PRD ──/spec-design──▶ 아키텍처 설계(Clean Architecture+모노레포)
                     ─▶ 기능별 모듈 분해 (의존성 방향 검증)
                     ─▶ 모듈별 docs/specs/<module>.md 생성 (설계 SSOT)
                     ─▶ packages/modules/services 골격 + 모듈 README 스캐폴딩
                          │
   feature/<module> 브랜치 ─(post-checkout)─▶ agents/ 자동 배치
                          │
                     ─▶ ORCHESTRATOR로 모듈별 TDD 구현
                     ─▶ /pr-report → /pr-3axis-review (spec ↔ 코드 정합 점검)
```

### PR 자동화 — Decision Audit

`/pr-report`는 커밋 → PR 생성 과정에서 3단계 자동 감사를 수행한다:

1. **보안 점검**: 하드코딩 자격증명, `os.getenv()` 기본값 인프라 노출, `.gitignore` 누락 탐지
2. **Decision Audit**: 이 PR에 포함된 결정을 나열하고, 위키 갱신 필요 여부를 Q1(다른 작업자
   영향)·Q2(위키 커버 여부)로 판정. "갱신 불요" 한 줄로 넘기는 것을 금지.
3. **사후 영향 평가**: 업/다운스트림 의존성, DB 스키마, API 인터페이스 변경 영향 보고

---

## 설정 (`ai-native-kit.toml`)

프로젝트 루트에 두면 `init`이 에셋의 `{{VAR}}` 자리표시자에 값을 채워 렌더링한다.
생략한 키는 기본값을 따른다.

```toml
[project]
name = "My Project"

[git]
base_branch = "main"            # 보호 릴리즈 브랜치
integration_branch = "development"  # PR base

[stack]
languages = ["python", "javascript"]

[stack.python]
min_version = "3.12"
test = "pytest"
lint = "ruff check"
line_length = 120

[stack.javascript]
test = "npm run test"
lint = "npm run lint"

[architecture]
preset = "clean"                # Clean Architecture 프리셋
```

`ai-native-kit init --with-config`로 이 파일의 예시본을 생성한 뒤 편집하고
다시 `init`을 돌리면 된다.

## 동작 방식

- 에셋은 패키지 안(`ai_native_kit/assets/`)에 동봉되어 배포된다.
- `init`은 각 에셋을 읽어 `{{VAR}}`를 설정값으로 치환한 뒤 대상 경로에 쓴다.
- 기존 파일은 보존(`--force` 시에만 덮어씀)되어 안전하게 재실행할 수 있다.
- git 훅은 항상 LF 줄바꿈으로 기록되고 실행 권한이 부여된다.

## 라이선스

MIT
