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

### 버전 업데이트 후 안정화 (doctor)

Claude Code는 버전이 오를 때 도구/동작이 가끔 깨진다(예: AskUserQuestion 도구 실패).
`ai-native-kit doctor`로 하니스가 멀쩡한지 한 번에 점검한다 — 에셋 존재, git `core.hooksPath`,
post-checkout(LF/실행권한), `.gitignore` 필수 항목, 현재 CC 버전, 알려진 quirk 경고.
`[FAIL]`이 있으면 종료 코드 1 (대개 `init --force`로 복구).

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
│   ├── context/               # 내부 위키 (결정/아키텍처 = "왜", docs 브랜치 전용)
│   │   ├── MAP.md / architecture.md / decisions.md
│   │   └── adr/ADR-0000-template.md
│   └── specs/                 # 구현 명세 (모듈 SSOT = "무엇/어떻게", 코드와 함께 갱신)
│       ├── README.md / SPEC_TEMPLATE.md
│       └── plan/PLAN_TEMPLATE.md
├── .githooks/post-checkout    # 새 브랜치 체크아웃 시 자동 스캐폴딩
└── CLAUDE.md                  # Clean Architecture 프리셋 프로젝트 지침 골격
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

SSOT는 **두 겹**이다: `docs/specs/<module>.md`(설계) + `modules/<module>/README.md`
(공개 API 계약). 결정의 "왜"는 `docs/context` 위키가 따로 보관한다.

### 프로젝트 위키 (docs/context) — 컨텍스트 엔지니어링

`docs/context/`는 코드만으로는 알 수 없는 "왜"와 "전제"를 남기는 **단일 진실
공급원(SSOT)** 이다. 운영 규칙:

- 위키는 **`docs` 브랜치에서만 편집** — 코드 PR과 분리해 drift를 막는다.
- **ADR 불변성**: 결정을 뒤집어도 원본을 삭제하지 않고 `Superseded by ADR-NNNN` 표기.
- `/pr-report`가 PR 직전 **Decision Audit**(이 변경이 위키 갱신을 요구하는지)을 수행한다.
- `/adr <제목>`으로 새 ADR을 템플릿에서 생성하고 인덱스를 갱신한다.
- `post-checkout` 훅은 `docs` 브랜치를 폴더 스캐폴딩에서 제외한다.

설치 후 git 저장소면 `core.hooksPath`가 `.githooks`로 자동 설정된다. 이후
`git checkout -b <BranchName>` 하면 훅이 `<BranchName>/`에 표준 폴더 구조 +
`agents/` 복사 + `CLAUDE.md`를 자동 생성한다 (보호 브랜치·`feature/*` 등은 제외).

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
