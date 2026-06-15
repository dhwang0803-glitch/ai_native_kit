# Project MAP

> 프로젝트 최상위 폴더 **지도**. 파일 인덱스가 아니라 상위 구조 지도다.
> 새 최상위 폴더가 생길 때만 갱신한다. (`docs` 브랜치에서만 편집)

## 최상위 구조

```
TODO: 프로젝트 최상위 폴더 구조를 여기에 기록하세요. 예시(Clean Architecture 모노레포):

<project>/
├── packages/          # 공유 패키지 (공유 스키마/타입 SSOT)
├── services/          # 배포 가능 서비스 (Composition Root)
├── modules/           # 도메인 모듈 (서비스에서 import)
├── database/          # 스키마 / 마이그레이션 / seeds
├── infra/             # IaC (Terraform/Docker 등)
├── docs/              # 프로젝트 문서
│   ├── context/       #   공용 지식 베이스 (이 위키) — docs 브랜치에서만 편집
│   └── specs/         #   모듈별 구현 명세
├── _agent_templates/  # Claude 서브에이전트 템플릿
└── scripts/           # 프로젝트 레벨 스크립트
```

## 브랜치 전략

| 브랜치 | 용도 |
|--------|------|
| `{{BASE_BRANCH}}` | 안정 브랜치 (protected) |
| `{{INTEGRATION_BRANCH}}` | 통합 브랜치 — feature PR의 base |
| `feature/*` | 기능 단위 개발 |
| `release` | 프로덕션 배포 트리거 |
| `docs` | 문서 전용 (`docs/context/` 편집) |

## 관련 문서

- 아키텍처: [`architecture.md`](./architecture.md)
- 설계 결정: [`decisions.md`](./decisions.md)
