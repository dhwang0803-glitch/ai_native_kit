# <MODULE_NAME> — 구현 명세

- **작성일**: YYYY-MM-DD
- **상태**: Draft | Reviewed | Implemented
- **참조**: `docs/context/adr/ADR-NNNN`, 관련 PRD 섹션

> 이 파일은 모듈의 **설계 SSOT**다. 구현 전에 채우고, 구현하며 갱신한다.
> 시그니처/필드/enum이 코드와 어긋나면 같은 PR에서 이 파일을 고친다.

---

## 모듈 역할

이 모듈이 담당하는 기능을 2~3문장으로. 어떤 입력을 받아 무엇을 내보내는가.

---

## 공유 스키마에서 import할 타입

| 타입 | 소스 | 용도 |
|------|------|------|
| `SomeSchema` | `common_schemas` | … |
| `SomeEnum` | `common_schemas.enums` | … |

```python
from common_schemas import SomeSchema
from common_schemas.enums import SomeEnum
```

---

## 이 모듈에서 구현할 클래스

### Domain Layer (`modules/<module>/domain/`)

#### entities/<entity>.py — `Entity`

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | `UUID` | PK |
| … | … | … |

메서드:
- `method() -> ReturnType` — …

#### value_objects/<vo>.py — `SomeVO`

| 필드 | 타입 | 설명 |
|------|------|------|

#### services/<service>.py — `SomeService`

```python
class SomeService:
    def do(self, arg: Type) -> Result: ...
```

#### ports/<port>.py — `SomePort` (ABC)

```python
from abc import ABC, abstractmethod

class SomePort(ABC):
    @abstractmethod
    async def fetch(self, id: UUID) -> Entity | None: ...
```

### Application Layer (`modules/<module>/application/`)

#### use_cases/<use_case>.py — `SomeUseCase`

| Input | Output | 설명 |
|-------|--------|------|
| `arg: Type` | `Result` | … |

의존성: `SomePort`, …

### Adapters Layer (`modules/<module>/adapters/`)

#### <adapter>.py — `SomeAdapter(SomePort)`

구현 노트: 외부 라이브러리, 재시도/타임아웃 정책 등.

---

## 환경 변수

| 변수명 | 필수 | 설명 |
|--------|------|------|
| `SOME_KEY` | Y | … (실제 기본값 하드코딩 금지) |

---

## 의존성 관계

```
Upstream (이 모듈이 의존):
  ├── packages/<shared_schemas>
  └── modules/<other>/domain/ports  (참조 사유)

Downstream (이 모듈에 의존):
  └── services/<service>  (사용 사유)
```

> Clean Architecture 의존성 방향(`domain → application → adapters`, `modules → services` 금지)을 위반하지 않는지 확인.

---

## 디렉토리 구조 (목표)

```
modules/<module>/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── services/
│   └── ports/
├── application/
│   └── use_cases/
├── adapters/
├── tests/
│   ├── unit/domain/
│   ├── unit/application/
│   └── integration/
└── README.md
```

---

## 공개 API (모듈 README로 요약될 부분)

다른 모듈이 import할 수 있는 안정 계약만 나열 (domain/ports·entities·value_objects, application/use_cases). adapters는 비공개.
