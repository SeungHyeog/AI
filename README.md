# Safe EKS MCP

Safe EKS MCP는 OpenCode에서 Amazon EKS를 안전하게 조회, 모니터링, 변경 계획 수립까지 할 수 있도록 만든 로컬 Python MCP 서버입니다.

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
- Python `subprocess.run` 실행 시 `shell=False`를 사용합니다.
- command timeout과 최대 출력 크기를 제한합니다.
- AWS access key, session token, bearer token 등 일반적인 credential 패턴을 redaction합니다.
- cluster-scoped tool은 명시적인 `region`과 `cluster`를 요구합니다.
- Kubernetes Secret 조회를 정책 레벨에서 차단합니다.
- mutating `kubectl`, `helm`, `aws` 명령은 기본적으로 차단합니다.
- apply/upgrade 계열은 control mode와 confirmation hash/token이 모두 필요합니다.

## 설치와 실행

```bash
uv sync
uv run safe-eks-mcp
uv run pytest
uv run basedpyright
uv run ruff check .
```

OpenCode MCP 설정은 `opencode.jsonc`에 들어 있습니다.

```jsonc
{
  "mcp": {
    "safe-eks": {
      "type": "local",
      "command": ["uv", "run", "safe-eks-mcp"],
      "enabled": true,
      "environment": {
        "EKS_OPS_MODE": "readonly"
      }
    }
  }
}
```

## 테스트 방식

테스트는 실제 AWS나 Kubernetes cluster에 접근하지 않습니다.

Pytest가 임시 디렉터리에 fake `aws`, `kubectl`, `helm` 바이너리를 만들고, 해당 경로를 `PATH` 앞에 붙입니다. Python tool 함수는 fake CLI를 통해 안전 정책과 argv 생성을 검증합니다.

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
uv run pytest
uv run basedpyright
uv run ruff check .
```

## 커밋하지 않는 로컬 산출물

일반적으로 아래 항목은 커밋하지 않습니다.

- `.venv/`
- `.tsbuildinfo/`
- `*.tsbuildinfo`
- `.omo/`
- `.graphify-venv/`
- `graphify-out/`
