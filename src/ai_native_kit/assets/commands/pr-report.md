커밋부터 PR 생성까지 전 과정을 자동으로 수행한다.

---

## 0. 커밋 경로 판별 (최우선)

현재 브랜치를 확인하고 경로를 결정한다. **원칙**: 모든 변경은 PR 리뷰를 거친다.

| 현재 브랜치 | 경로 |
|------------|------|
| `feature/*` | 현재 브랜치에서 커밋 → `{{INTEGRATION_BRANCH}}` PR |
| `{{INTEGRATION_BRANCH}}` | 현재 브랜치에서 커밋 → 기존/신규 PR (별도 feature 브랜치 생성 안 함) |

안정화/배포 단계 버그는 `hotfix/*` 브랜치 생성.

---

## 1. 현재 브랜치 및 변경 파일 확인

```bash
git branch --show-current
git status
git diff --stat
```

변경 파일이 **현재 브랜치 작업 폴더** 내에 있는지 확인한다. 다른 브랜치 작업 폴더의
파일은 절대 스테이징하지 않는다.

---

## 2. 보안 점검 (커밋 전 필수)

```bash
git diff | grep -iE "(password|secret|api_key|token)\s*=\s*['\"][^'\"]{4,}"
git diff | grep -E "os\.getenv\(.+,\s*['\"]"
```

| 점검 항목 | 기준 |
|-----------|------|
| 하드코딩된 자격증명 | 없어야 함 |
| os.getenv() 기본값 | 실제 IP/DB명/사용자명 없어야 함 |
| `.env` gitignore | 포함되어 있어야 함 |

탐지 시 → **커밋 중단, 즉시 수정 요청**. 이상 없으면 "보안 점검 통과" 보고 후 진행.

> 상세 점검은 `_agent_templates/SECURITY_AUDITOR.md`를 따른다.

---

## 2-b. 위키(docs/context) 갱신 점검 (Decision Audit)

**위키(`docs/context/*`)는 현재 코드 브랜치에서 절대 수정·커밋하지 않는다.**
위키 갱신은 전용 `docs` 브랜치에서만 이뤄지며, 별도 PR로 분리한다.

### Step 1 — 결정 감사 (필수 선행)

> ⚠️ "diff에 `docs/context/`가 없다"만 보고 "갱신 불요"라고 보고하는 것은 금지.
> 그건 "건드렸냐" 체크지 "최신이냐" 체크가 아니다.

이 PR이 포함하는 **모든 결정**을 나열한다. "결정"이란 코드·문서·설정 변경을 유발한
**판단**이다 (단순 리팩토링/버그 수정은 결정 아님). 자문 체크리스트:

- 새 기술/라이브러리/도구를 추가했는가?
- 타 브랜치가 의존할 **계약 형상**(JSON 키, DTO 필드, API 시그니처, 상태 값 집합)을 정했는가?
- 두 개 이상 모듈이 공유하는 **데이터 흐름**이 바뀌었는가?
- 보안 정책(저장/전송/로깅)이 바뀌었는가?
- 운영 절차(스케줄러/백업/마이그레이션)가 바뀌거나 새로 생겼는가?

각 결정마다: **(Q1)** 이 결정을 모르면 다른 작업자가 잘못된 전제로 작업할 가능성이 있는가?
**(Q2)** 현재 위키만 읽어 이 결정을 파악할 수 있는가? → **Q1=Yes & Q2=No면 위키 갱신 필요.**

### Step 2 — 트리거 매핑

| 변경 유형 | 갱신 대상 (docs 브랜치에서) |
|-----------|--------------------------|
| 새 최상위 폴더 추가, 파일 배치 규칙 변경 | `docs/context/MAP.md` |
| 데이터 경로 / 새 실행 모드 / 모듈 간 쓰기 순서 | `docs/context/architecture.md` |
| 기술 스택 교체·추가, 보안 정책, 타 모듈이 의존할 계약 형상 | `docs/context/decisions.md` (`/adr`로 새 ADR) |

### Step 3 — diff 사고 방지

현재 브랜치 diff에 `docs/context/`가 실수로 포함됐으면 → **stash/복원 후 중단**, `docs`
브랜치로 별도 PR을 만들도록 안내.

### 보고 형식 (한 줄 "갱신 불요" 금지 — 감사 내용 필수)

- **Case A 갱신 불요**: `결정 N건: <…> / 각 Q1·Q2 판정: <모두 브랜치-로컬 또는 기존 위키로 커버> → 갱신 불요`
- **Case B 갱신 필요**: `갱신 필요 결정: <…> → docs 브랜치 PR 필요. 코드 PR 본문 '사후 영향 평가'에 "위키 갱신 PR 필요: <설명>" 행 추가`
- **Case C 갱신 완료**: 같은 주기에 만든 `docs` 브랜치 PR 번호를 본 PR 본문에 참조.

---

## 3. 현재 브랜치 파일만 스테이징 및 커밋

```bash
git add {현재 브랜치 폴더}/
git commit -m "..."
```

**커밋 금지 파일**: `.env`, `*.pem`, `credentials.json`, 데이터/모델 산출물

---

## 4. base 브랜치 최신화

```bash
git fetch origin
git log HEAD..origin/{{INTEGRATION_BRANCH}} --oneline   # base에 내 브랜치에 없는 커밋?
git log origin/{{INTEGRATION_BRANCH}}..HEAD --oneline
```

- base에 새 커밋이 있으면 → `git pull origin {{INTEGRATION_BRANCH}}` 먼저
- 충돌 발생 시 → 충돌 파일 목록 알리고 **중단**, 해결 후 재실행 요청

---

## 5. 변경사항 분석

```bash
git diff --name-status origin/{{INTEGRATION_BRANCH}}...HEAD
git log origin/{{INTEGRATION_BRANCH}}..HEAD --oneline
```

---

## 6. 이전 PR 내용 확인

```bash
gh pr list --head {현재 브랜치} --state all --limit 1
gh pr view {PR번호} --json body
```

이전 PR이 있으면 중복 항목은 최신으로 덮어쓰고, 새 항목은 추가한다.

---

## 7. PR 생성

base는 항상 `{{INTEGRATION_BRANCH}}`. 본문은 아래 형식으로 작성 후 `gh pr create`.

```
## 변경사항 요약
<!-- 변경 파일별로 무엇을 왜 (bullet 3개 이내) -->

## 사후 영향 평가
| 영향 범위 | 내용 | 조치 필요 |
|-----------|------|----------|
| 업스트림 의존성 | ... | Yes/No |
| 다운스트림 의존성 | ... | Yes/No |
| DB 스키마 변경 | ... | Yes/No |
| API 인터페이스 변경 | ... | Yes/No |

## 보안 평가
| 점검 항목 | 결과 |
|-----------|------|
| 하드코딩 자격증명 | ✅/❌ |
| os.getenv() 기본값 인프라 노출 | ✅/❌ |
| .env gitignore | ✅/❌ |
| 외부 입력값 검증 | ✅/❌ |

## 테스트 체크리스트
- [ ] 로컬 실행 확인
- [ ] 주요 변경 함수 단위 테스트

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

---

## ⛔ 절대 금지 규칙 (명시적 승인 없이 실행 금지)

1. `git push origin {{BASE_BRANCH}}` — base 브랜치 직접 push 금지
2. PR 없이 `{{BASE_BRANCH}}`/`{{INTEGRATION_BRANCH}}`에 직접 merge 금지
3. PR 리뷰(Approve) 없이 merge 금지
4. 다른 브랜치 폴더 파일을 현재 커밋에 포함 금지
5. 요청하지 않은 파일을 추가로 커밋·push 금지
6. 일상 PR을 `{{BASE_BRANCH}}`에 직접 올리지 않는다 — base는 `{{INTEGRATION_BRANCH}}`

> 사용자가 "push해줘"/"merge해줘"라고 명시하기 전까지 유효. 위반 시 즉시 중단·보고.
