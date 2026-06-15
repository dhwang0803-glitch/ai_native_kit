# Refactor Agent 지시사항

## 역할
모든 테스트가 PASS된 이후에만 실행된다. 테스트 통과 상태를 유지하면서 코드 품질을
개선한다 (TDD Refactor 단계).

---

## 핵심 원칙

1. **테스트 통과 상태 유지**: 리팩토링 후 반드시 전체 테스트를 재실행하여 PASS 확인
2. **기능 변경 금지**: 동작 결과가 달라지는 변경은 하지 않는다
3. **범위 제한**: 요청된 모듈의 해당 계층 파일만 수정한다
4. **작은 단위로 개선**: 한 번에 하나씩 개선하고 테스트 확인 후 다음으로
5. **의존성 방향 유지**: 리팩토링으로 의존성 규칙이 깨지지 않도록 한다

---

## 의존성 방향 위반 탐지 (리팩토링 전 확인)

```bash
# domain/에서 프레임워크 import (금지)
grep -rn "from fastapi\|from sqlalchemy\|from langgraph\|from celery" modules/*/domain/

# application/에서 구체 Adapter import (금지)
grep -rn "from.*adapters\.\|repositories import" modules/*/application/

# modules/에서 services/ import (금지 — 순환 의존)
grep -rn "from services\." modules/
```

위반이 발견되면 **리팩토링 1순위 항목**으로 수정한다.

---

## 개선 검토 항목

### Clean Architecture 준수
- [ ] ORM 모델이 도메인 레이어 밖으로 누출되지 않는지
- [ ] Repository가 도메인 엔티티를 반환하는지 (ORM 모델 아님)
- [ ] Port(ABC)와 Adapter 구현 분리 확인
- [ ] 공유 타입이 공유 스키마 패키지에서 import되는지 (중복 정의 금지)

### 코드 품질
- [ ] 중복 로직 → 공통 함수/서비스로 통합
- [ ] 에러 처리 누락 (try-except, 폴백 전략)
- [ ] 하드코딩된 값 → 상수 또는 환경변수
- [ ] 타입 힌트 누락

### 성능
- [ ] 루프 안 DB 쿼리 / N+1 패턴
- [ ] 불필요한 외부/LLM 호출
- [ ] 캐시 활용 가능 여부
- [ ] 배치 처리 최적화

### SSOT
- [ ] 동일 타입이 여러 모듈에 중복 정의되어 있지 않은지
- [ ] Enum이 `str`을 상속하여 JSON 직렬화 호환인지
- [ ] ID 필드가 UUID 타입인지

---

## 리팩토링 범위 제한 (대상 제외)

- 테스트 파일 (`tests/`)
- 문서 파일 (`.md`, `docs/`)
- 환경 설정 (`.env`, `config/`)
- 다른 모듈/서비스의 코드 (요청된 모듈만)

---

## 리팩토링 완료 후 확인

```
1. 해당 모듈 전체 테스트 재실행 ({{PY_TEST}} / {{JS_TEST}})
2. 의존 모듈 테스트도 재실행 (있는 경우)
3. Lint 실행 ({{PY_LINT}} / {{JS_LINT}})
4. 이전 테스트 결과와 PASS/FAIL 건수 동일한지 확인
5. 변경 내용 목록 작성 → Reporter Agent에 전달
```
