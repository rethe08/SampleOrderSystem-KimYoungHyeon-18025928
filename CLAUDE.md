# CLAUDE.md

## 개발 진행 원칙

### 1. 구현 순서
모든 구현은 반드시 아래 순서를 따른다.

```
계획 수립 → 사용자 승인 → 구현
```

- 계획 없이 구현을 시작하지 않는다.
- 사용자의 명시적 승인 없이 구현을 시작하지 않는다.

### 2. 계획 문서 관리
- 전체 계획은 `plan.md` 파일에 저장한다.
- `plan.md`에는 전체 phase 목록과 각 phase의 요약이 포함된다.

### 3. Phase별 세부 문서
- 각 phase의 세부 구현 내용은 별도의 md 파일로 저장한다.
- 파일명 규칙: `phase-{번호}-{이름}.md`
  - 예: `phase-1-mvc-skeleton.md`, `phase-2-data-persistence.md`

### 4. 구현 범위 제한
- 각 phase의 구현은 해당 phase의 세부 md 파일에 명시된 내용만 구현한다.
- 명시되지 않은 추가 구현은 하지 않는다.
- 범위를 벗어나는 작업이 필요한 경우, 별도 계획을 수립하고 사용자 승인을 받은 후 진행한다.

### 5. 기능 명세 기반 개발
- 모든 기능은 반드시 `PRD.md`(기능 명세서)를 기반으로 개발한다.
- PRD.md에 명시되지 않은 기능은 임의로 구현하지 않는다.
- PRD.md의 내용과 충돌하는 구현은 허용되지 않는다.
- 기능 추가 또는 변경이 필요한 경우, PRD.md를 먼저 수정하고 사용자 승인을 받은 후 구현한다.

### 6. Agent 활용 (Verify Harness)
모든 구현은 반드시 `.claude/agents/` 폴더의 agent들을 아래 순서대로 활용한다.

```
consistency-verifier → ai-action → test-verifier
                                 ↘ compliance-verifier (병렬)
```

| 단계 | Agent | 역할 |
|------|-------|------|
| 1 | `consistency-verifier` | 코드 생성 전 PRD/PLAN 문서 간 충돌·누락·모호성 검증 |
| 2 | `ai-action` | 검증 통과 후 실제 코드 및 단위 테스트 생성, REPORT.md 작성 |
| 3 | `test-verifier` | 생성된 코드의 테스트를 실제 실행하여 동작 정확성 검증 |
| 3 | `compliance-verifier` | PLAN 체크리스트와 산출물을 항목 단위로 대조하여 누락 검증 |

- `consistency-verifier` 가 FAIL 이면 구현을 시작하지 않는다.
- `test-verifier` 또는 `compliance-verifier` 가 FAIL 이면 `ai-action` 을 재실행한다.
- 모든 agent 가 PASS 한 후에만 해당 phase 를 완료로 간주한다.

### 7. Git 커밋 규칙
- 각 세부 phase (예: 1-1, 1-2, ...) 완료 시 반드시 git commit 을 수행한다.
- 커밋 타이밍: 모든 agent 가 PASS 한 직후, 다음 phase 진입 전.
- 커밋 메시지 형식:
  ```
  [phase-{번호}] {phase 이름}
  
  - {주요 변경 사항 요약}
  ```
  예: `[phase-1-1] 프로젝트 초기 구조 설정`
- 커밋 범위: 해당 phase에서 생성·수정된 파일만 스테이징한다.
- agent PASS 전 커밋은 허용하지 않는다.

### 8. 진행 상태 문서 반영 규칙
각 세부 phase 완료 시 반드시 상위 개발 문서에 진행 내용을 반영한다.

- **세부 phase 문서** (`phase-{번호}-{이름}.md`):
  - 체크리스트 항목을 `[ ]` → `[x]` 로 업데이트한다.

- **상위 개요 문서** (`phase-{번호}-{상위이름}.md`의 Sub-Phase 목록):
  - 해당 sub-phase 의 상태를 `미착수` → `완료` 로 업데이트한다.

- **전체 계획 문서** (`plan.md`):
  - 해당 phase 전체가 완료된 경우 상태를 `미착수` → `완료` 로 업데이트한다.

- 반영 타이밍: git commit 과 동시에 수행하며, 문서 업데이트도 같은 커밋에 포함한다.
