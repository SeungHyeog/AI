# Safe EKS MCP

Safe EKS MCP는 OpenCode에서 Amazon EKS를 안전하게 조회, 모니터링, 변경 계획 수립까지 할 수 있도록 만든 로컬 TypeScript MCP 서버와 프로젝트 전용 OpenCode 설정 모음입니다.

기본 동작은 항상 읽기 전용입니다. 실제 클러스터를 변경하는 `kubectl apply`나 `helm upgrade` 계열 작업은 기본 모드에서 차단되며, 별도의 control 모드와 plan 기반 확인 토큰이 있어야만 실행됩니다.

## 주요 기능

### 1. EKS 클러스터 관리 조회

AWS CLI를 안전한 MCP tool로 감싸서 EKS 제어 plane 정보를 조회합니다.

지원 기능:

- 리전별 EKS 클러스터 목록 조회
- 특정 EKS 클러스터 상세 조회
- 노드그룹 목록 조회
- 노드그룹 상세 조회
- EKS add-on 목록 조회
- EKS add-on 상세 조회
- `aws eks update-kubeconfig --dry-run` 결과 확인

관련 MCP tools:

- `aws_eks_list_clusters`
- `aws_eks_describe_cluster`
- `aws_eks_list_nodegroups`
- `aws_eks_describe_nodegroup`
- `aws_eks_list_addons`
- `aws_eks_describe_addon`
- `eks_generate_kubeconfig_dry_run`

### 2. Kubernetes 워크로드 모니터링

`kubectl`을 직접 실행하지 않고 MCP tool을 통해 명시적인 클러스터 context와 namespace를 지정해서 조회합니다.

지원 기능:

- Kubernetes 리소스 조회
- 리소스 상세 설명 조회
- pod 로그 조회
- 이벤트 조회
- RBAC 권한 확인
- Secret 리소스 조회 차단
- `kubectl --raw`를 통한 Secret API 우회 차단

관련 MCP tools:

- `kubectl_get`
- `kubectl_describe`
- `kubectl_logs`
- `kubectl_events`
- `kubectl_auth_can_i`

### 3. Helm 릴리스 조회와 렌더링

Helm 릴리스 상태와 히스토리를 읽고, chart를 설치하지 않고 로컬 렌더링 또는 lint할 수 있습니다.

지원 기능:

- Helm release 목록 조회
- Helm release 상태 조회
- Helm release 히스토리 조회
- Helm chart template 렌더링
- Helm chart lint

관련 MCP tools:

- `helm_list`
- `helm_status`
- `helm_history`
- `helm_template`
- `helm_lint`

### 4. 변경 작업 제어 workflow

실제 변경 작업은 plan-first 방식으로만 설계되어 있습니다.

지원 흐름:

1. `plan_kubectl_apply` 또는 `plan_helm_upgrade`로 실행될 명령과 출력 결과를 먼저 확인합니다.
2. plan 결과에 포함된 `confirmationHash`와 `confirmationToken`을 검토합니다.
3. 서버가 `EKS_OPS_MODE=control`로 실행 중일 때만 apply 계열 tool이 동작할 수 있습니다.
4. apply 요청은 plan과 동일한 cluster, namespace, release, chart, values, manifest path를 사용해야 합니다.
5. hash/token이 plan과 일치하지 않으면 실행하지 않습니다.

관련 MCP tools:

- `plan_kubectl_apply`
- `apply_kubectl_apply_confirmed`
- `plan_helm_upgrade`
- `apply_helm_upgrade_confirmed`

## 안전 모델

이 프로젝트의 핵심은 EKS 작업을 자동화하되, 실수로 클러스터를 변경하거나 민감정보를 노출하지 않도록 막는 것입니다.

적용된 안전장치:

- 기본 모드는 `readonly`입니다.
- 테스트는 실제 AWS credential, kubeconfig, live cluster 없이 동작합니다.
- MCP 서버는 credential을 저장하거나 요청하지 않습니다.
- 명령 실행은 shell 문자열이 아니라 argv 배열로 처리합니다.
- Node `spawn` 실행 시 `shell: false`를 사용합니다.
- command timeout과 최대 출력 크기를 제한합니다.
- AWS access key, session token, bearer token 등 일반적인 credential 패턴을 redaction합니다.
- cluster-scoped tool은 명시적인 `region`과 `cluster`를 요구합니다.
- Kubernetes Secret 조회를 정책 레벨에서 차단합니다.
- mutating `kubectl`, `helm`, `aws` 명령은 기본적으로 차단합니다.
- apply/upgrade 계열은 control mode와 confirmation hash/token이 모두 필요합니다.

## 설치와 빌드

```bash
npm install
npm run build
npm test
```

OpenCode MCP 설정은 `opencode.jsonc`에 들어 있습니다.

```jsonc
{
  "mcp": {
    "safe-eks": {
      "type": "local",
      "command": ["node", "./dist/index.js"],
      "enabled": true,
      "environment": {
        "EKS_OPS_MODE": "readonly"
      }
    }
  }
}
```

## OpenCode skills

프로젝트에는 EKS 작업과 학습 루프를 위한 skills가 포함되어 있습니다.

- `.opencode/skills/hermes-closed-loop/SKILL.md`
  - 모든 비단순 작업에서 사용하는 폐쇄형 학습 루프입니다.
  - Observe, Plan, Act, Verify, Reflect, Update Skills 순서로 작업합니다.
  - 검증된 재사용 가능한 교훈만 skill에 반영합니다.

- `.opencode/skills/eks-management/SKILL.md`
  - EKS 클러스터, 노드그룹, add-on, kubeconfig dry-run 등 관리성 조회에 사용합니다.
  - 기본적으로 read-only MCP tool을 우선 사용합니다.

- `.opencode/skills/eks-monitoring/SKILL.md`
  - workload 상태, 이벤트, 로그, Helm release 상태, RBAC 확인 등 모니터링과 장애 조사에 사용합니다.
  - 로그 조회는 반드시 `tail` 또는 `since`로 범위를 제한합니다.

- `.opencode/skills/eks-control/SKILL.md`
  - `kubectl apply`와 `helm upgrade`처럼 클러스터를 변경할 수 있는 작업에 사용합니다.
  - plan-first, confirmation-gated workflow를 강제합니다.

## OpenCode commands

프로젝트에는 반복 작업을 쉽게 수행하기 위한 command 문서도 포함되어 있습니다.

- `.opencode/commands/eks-status.md`
  - EKS 상태 스냅샷 수집
  - cluster, nodegroup, add-on, workload, Helm release, 이벤트를 read-only로 확인

- `.opencode/commands/eks-incident.md`
  - EKS incident를 read-only 방식으로 조사
  - 이벤트, pod 상태, 로그, Helm 상태, RBAC 등을 순차적으로 확인

- `.opencode/commands/eks-change-plan.md`
  - 변경 적용 없이 안전한 변경 계획만 작성
  - apply/upgrade 실행은 하지 않음

- `.opencode/commands/hermes-loop.md`
  - Hermes-inspired closed learning loop 전체 실행

- `.opencode/commands/hermes-reflect.md`
  - 완료된 작업을 돌아보고 skill 업데이트가 필요한지 판단

- `.opencode/commands/hermes-update-skills.md`
  - 검증된 교훈만 프로젝트 skill에 반영

## Hermes 스타일 폐쇄형 학습 루프

이 프로젝트는 Nous Research의 Hermes Agent에서 참고한 closed learning loop 원칙을 OpenCode 프로젝트 구조로 옮겼습니다.

여기서 말하는 학습은 모델 weight를 직접 학습시키는 것이 아닙니다. 작업 과정에서 검증된 절차적 지식을 skill에 반영하고, 다음 요청에서 더 나은 방식으로 재사용하는 운영 루프입니다.

루프 단계:

1. **Observe**
   - 사용자의 목표를 한 줄로 정리합니다.
   - 관련 파일과 기존 skill을 먼저 읽습니다.
   - EKS 작업이면 `eks-management`, `eks-monitoring`, `eks-control` 중 맞는 skill을 함께 사용합니다.

2. **Plan**
   - 작업을 검증 가능한 단계로 나눕니다.
   - 외부 부작용, 승인 필요 여부, EKS safety gate를 확인합니다.

3. **Act**
   - 가장 작은 안전한 변경 또는 read-only 조사를 수행합니다.
   - EKS 작업은 가능한 한 raw shell보다 `safe-eks` MCP tool을 사용합니다.

4. **Verify**
   - 코드 변경 후 기본적으로 `npm test`, `npm run typecheck`, `npm run build`를 실행합니다.
   - skill/command 문서 변경은 frontmatter와 안전 규칙을 확인합니다.

5. **Reflect**
   - 이번 작업에서 다음에도 재사용할 만한 절차, 실수 방지 규칙, 검증 방법이 있었는지 확인합니다.

6. **Update Skills**
   - 검증된 교훈만 `.opencode/skills/*/SKILL.md`에 반영합니다.
   - 미검증 아이디어는 `.opencode/learning/skill-backlog.md`에 보류합니다.

Skill 업데이트 금지 대상:

- kubeconfig 내용
- Kubernetes Secret 값
- AWS credential
- access token
- private incident payload
- 단발성 workaround
- 검증되지 않은 추측

## Graphify

Graphify는 코드베이스 구조를 그래프로 만들어 탐색할 수 있게 해주는 도구입니다.

현재 구성:

- `.graphify-venv/`
  - Graphify 실행을 위한 로컬 Python 가상환경입니다.
  - 커밋하지 않습니다.

- `graphify-out/`
  - Graphify가 생성한 코드 그래프 산출물입니다.
  - `graph.json`, `graph.html`, `GRAPH_REPORT.md` 등이 들어 있습니다.
  - 팀에서 코드 그래프를 공유하고 싶다면 커밋할 수 있습니다.

유용한 명령:

```bash
.graphify-venv/bin/graphify update . --force
.graphify-venv/bin/graphify hook status
```

현재 Graphify hook 상태:

- `post-commit`: installed
- `post-checkout`: installed

## 테스트 방식

테스트는 실제 AWS나 Kubernetes cluster에 접근하지 않습니다.

Vitest가 임시 디렉터리에 fake `aws`, `kubectl`, `helm` 바이너리를 만들고, 해당 경로를 `PATH` 앞에 붙입니다. MCP 호출은 in-memory MCP client/server transport를 통해 실행됩니다.

검증하는 내용:

- AWS EKS tool이 명시적 region과 argv 배열을 사용하는지
- credential redaction이 동작하는지
- Secret 조회가 실행 전에 차단되는지
- `kubectl --raw` Secret API 우회가 차단되는지
- `kubectl apply` plan이 client dry-run을 사용하는지
- readonly mode에서 apply가 차단되는지
- control mode에서도 confirmation token mismatch가 차단되는지
- mutating `kubectl`, `helm`, `aws` 명령이 policy에서 차단되는지

실행:

```bash
npm test
npm run typecheck
npm run build
```

## 커밋하지 않는 로컬 산출물

일반적으로 아래 항목은 커밋하지 않습니다.

- `node_modules/`
- `dist/`
- `.tsbuildinfo/`
- `*.tsbuildinfo`
- `.omo/`
- `.graphify-venv/`

`graphify-out/`은 팀이 코드 그래프를 공유하려는 경우에만 커밋합니다.
