# CI/CD

The initial CI/CD direction is Jenkins-centered.

Pipeline stages:

1. Checkout
2. Lint
3. Unit test
4. Docker image build
5. Image vulnerability scan
6. Helm template validation
7. Optional staging deploy

Production deployment is intentionally not enabled in the initial pipeline. Production rollout and rollback should require manual approval.
