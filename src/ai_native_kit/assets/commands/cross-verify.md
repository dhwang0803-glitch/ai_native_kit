Claude Code가 생성한 산출물(plan, spec, 코드, PR)을 Codex MCP를 통해 독립적으로 교차 검증한다. 자기 편향(self-bias)을 방지하기 위해 **작성자와 다른 모델이 검증**하는 것이 핵심이다. 인자: 검증 대상 유형 또는 파일 경로. 예: `/cross-verify plan`, `/cross-verify docs/specs/auth.md`, `/cross-verify diff`

> **사전 요구사항**: Codex MCP 서버가 `.claude/settings.json`에 설정되어 있어야 한다. 설정 가이드: `docs/context/cross-verify-guide.md`

---

## 원칙

1. **같은 모델이 만든 것을 같은 모델이 검증하지 않는다.** Claude가 작성한 산출물은 Codex가 검증하고, Codex가 수정한 것은 Claude가 재검증한다.
2. **같은 세션에서 자기 코드를 평가하지 않는다.** 자기 편향이 발생해 "잘했습니다"만 반복한다.
3. **검증 결과에서 불일치(disagreement)가 있으면 사람이 최종 판단한다.** 어느 모델도 절대적 권위를 갖지 않는다.

---

## Step 0. 검증 대상 판별

인자로 유형을 받거나 자동 판별한다:

| 인자 | 대상 | 수집 파일 |
|------|------|----------|
| `plan` | 실행 계획 | `docs/specs/plan/*.md` 중 최근 변경 |
| `spec` | 모듈 설계 명세 | `docs/specs/<module>.md` |
| `code` | 구현 코드 | 현재 브랜치의 변경 파일 (`git diff --name-only`) |
| `diff` | PR diff | `git diff origin/{{INTEGRATION_BRANCH}}...HEAD` |
| `pr` | PR 전체 | diff + spec + plan 통합 검증 |
| 파일 경로 | 특정 파일 | 해당 파일 + 관련 spec/test |
| (생략) | 자동 판별 | 가장 최근 변경된 산출물 유형으로 추정 |

## Step 1. 컨텍스트 수집

검증 대상에 따라 다음을 패키징한다:

### plan/spec 검증 시
```bash
# 검증 대상 파일
cat docs/specs/plan/<module>.md   # 또는 docs/specs/<module>.md

# 참조 컨텍스트 (Codex에 함께 전달)
cat CLAUDE.md                      # 아키텍처 규칙·제약 사항
cat docs/context/architecture.md   # 현재 아키텍처
```

### code/diff 검증 시
```bash
# 변경된 파일 목록
git diff --name-only origin/{{INTEGRATION_BRANCH}}...HEAD

# 변경 내용
git diff origin/{{INTEGRATION_BRANCH}}...HEAD

# 관련 spec (변경 파일의 모듈에 해당하는 spec)
cat docs/specs/<module>.md

# 관련 테스트 결과 (있다면)
{{PY_TEST}} <관련 테스트> --tb=short 2>&1 | tail -30
```

## Step 2. Codex MCP 검증 요청

Codex MCP 도구를 호출하여 독립적 검증을 요청한다. MCP 도구가 사용 불가능하면 **Step 2-b(수동 모드)** 로 전환.

### Step 2-a. MCP 자동 모드

Codex MCP 서버의 task 생성 도구를 호출한다. 프롬프트는 검증 유형별로 다르게 구성:

#### plan/spec 검증 프롬프트
```
당신은 독립적인 코드 리뷰어입니다. 다른 AI가 작성한 실행 계획/설계 명세를 검증하세요.

## 검증 기준
1. **실현 가능성**: 이 계획대로 구현하면 실제로 동작하는 코드가 나오는가?
2. **완전성**: 빠진 단계, 고려하지 않은 엣지 케이스가 있는가?
3. **아키텍처 정합성**: 아래 아키텍처 규칙을 위반하는 설계가 있는가?
4. **모호성**: 구현자가 해석을 달리할 수 있는 모호한 서술이 있는가?
5. **의존성 순서**: Phase 간 의존성이 올바른가, 병렬 실행 가능한 것이 직렬로 되어 있지 않은가?

## 아키텍처 규칙
{CLAUDE.md의 아키텍처 섹션}

## 검증 대상
{plan 또는 spec 내용}

## 출력 형식
각 기준에 대해: PASS/WARN/FAIL + 근거 + 수정 제안. 불확실한 부분은 "확인 필요"로 표시.
```

#### code/diff 검증 프롬프트
```
당신은 독립적인 코드 리뷰어입니다. 다른 AI가 작성한 코드 변경을 검증하세요.

## 검증 기준
1. **정확성**: 로직 오류, off-by-one, race condition, null 처리 누락
2. **하드코딩/회피 패턴**: 테스트 통과만을 위한 하드코딩, mock 남용, 빈 except 블록
3. **아키텍처 위반**: 의존성 방향, 레이어 침범, SSOT 위반
4. **보안**: 하드코딩 자격증명, 인젝션, 입력 미검증
5. **spec 정합성**: 명세와 구현이 일치하는가

## 아키텍처 규칙
{CLAUDE.md의 아키텍처 + 보안 섹션}

## 관련 Spec
{해당 모듈의 spec}

## 코드 변경 (diff)
{git diff 내용}

## 출력 형식
파일:라인 단위로 지적. 각 지적에 심각도(CRITICAL/HIGH/MEDIUM/LOW) + 근거 + 수정 제안.
하드코딩/회피 패턴은 반드시 별도 섹션으로 분리.
```

### Step 2-b. 수동 모드 (MCP 미설정 시)

Codex MCP를 사용할 수 없는 경우:

1. 위 프롬프트를 **파일로 저장** (`docs/specs/plan/cross-verify-prompt-{timestamp}.md`)
2. 사용자에게 안내:
   ```
   Codex MCP가 설정되어 있지 않습니다.
   검증 프롬프트가 아래 파일에 저장되었습니다:
     docs/specs/plan/cross-verify-prompt-{timestamp}.md

   수동 검증 방법:
   1. 위 파일 내용을 Codex/ChatGPT에 붙여넣기
   2. 결과를 이 세션에 다시 붙여넣기
   3. 또는: Codex MCP 설정 후 다시 /cross-verify 실행

   설정 가이드: docs/context/cross-verify-guide.md
   ```
3. 사용자가 외부 검증 결과를 붙여넣으면 Step 3으로 진행.

## Step 3. 결과 비교 및 보고

Codex 검증 결과를 Claude의 원본 산출물과 비교한다.

### 3-1. 불일치(Disagreement) 추출

| 항목 | Claude 판단 | Codex 판단 | 심각도 | 사람 판단 필요 |
|------|-----------|-----------|--------|--------------|

### 3-2. 합의(Agreement) 요약

양쪽 모델이 동의하는 부분은 신뢰도가 높다. 간략히 요약.

### 3-3. Codex 단독 지적

Claude가 놓친 부분을 Codex가 발견한 경우. 이 항목이 가장 가치 있다.

### 3-4. 종합 판정

```
## 교차 검증 결과

- 검증 대상: {유형} — {파일/범위}
- 검증 모델: Codex (via MCP)
- 불일치 항목: N건 (CRITICAL: n, HIGH: n, MEDIUM: n)
- Codex 단독 지적: N건
- 합의 항목: N건

### 사람이 결정해야 할 항목
1. {불일치 항목 — 양쪽 근거 제시}

### 권고 조치
- [ ] {수정 필요 항목}
- [ ] {확인 필요 항목}
```

## Step 4. 보고서 저장

검증 보고서를 `docs/specs/plan/cross-verify-{target}-{date}.md`에 저장한다. 이 기록은 하네스 개선(`/session-retro`)의 입력이 된다.

---

## 교차 검증 파이프라인 전체 흐름

```
Claude Code 산출물 생성
    ↓
/cross-verify [target]
    ↓
컨텍스트 수집 (산출물 + 아키텍처 규칙 + spec)
    ↓
Codex MCP 호출 (독립 검증 요청)
    ↓
결과 수신
    ↓
불일치/합의/단독지적 분류
    ↓
사용자에게 보고 (사람이 최종 판단)
    ↓
보고서 저장 → /session-retro 입력
```

---

## ⛔ 금지

- Codex 검증 결과를 Claude가 임의로 무시하거나 반박하지 않는다. 불일치는 사람에게 양쪽 근거를 제시한다.
- Codex 결과가 없는 상태에서 "검증 완료"를 보고하지 않는다.
- 같은 세션에서 Claude가 작성한 코드를 Claude 자신이 "교차 검증"하지 않는다 — 그것은 자기 평가이지 교차 검증이 아니다.
