# Project MAP

> 프로젝트 최상위 폴더 **지도**. 새 최상위 폴더가 생길 때만 갱신. (`docs` 브랜치에서만 편집)

## 최상위 구조 (프론트엔드 — 단일 배포)

```
TODO: 실제 구조로 채우세요. 예시(정적/SPA 프론트엔드):

<project>/
├── public/                  # 정적 자산 (이미지/PDF 등)
├── src/
│   ├── domain/              #   타입·모델 SSOT (프레임워크 무관)
│   ├── data/               #   데이터 접근 (API/콘텐츠 로딩) — content/ 기반이면 src/content/
│   ├── components/         #   UI 프레젠테이션
│   └── app/                #   라우트/페이지 (Composition Root)
├── content/                 # (선택) 파일 기반 콘텐츠 SSOT
├── docs/
│   ├── context/             #   위키 (결정/아키텍처) — docs 브랜치 전용
│   └── specs/               #   구현 명세 (영역별)
├── _agent_templates/        # TDD/리뷰 서브에이전트
└── _module_templates/       # 컴포넌트/영역 README 템플릿
```

## 브랜치 전략

| 브랜치 | 용도 |
|--------|------|
| `{{BASE_BRANCH}}` | 안정 브랜치 (프로덕션) |
| `{{INTEGRATION_BRANCH}}` | 통합 브랜치 — feature PR base |
| `feature/*` | 기능 단위 개발 |
| `docs` | 위키 편집 전용 |

## 관련 문서

- 아키텍처: [`architecture.md`](./architecture.md)
- 설계 결정: [`decisions.md`](./decisions.md)
