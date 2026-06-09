pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        APP_NAME = 'ai-backend'
        IMAGE_REPO = 'kubepilot/ai-backend'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Lint') {
            steps {
                sh 'python3 -m pip install --upgrade pip'
                sh 'python3 -m pip install -e "apps/backend[dev]"'
                sh 'python3 -m ruff check apps/backend'
            }
        }

        stage('Unit Test') {
            steps {
                sh 'python3 -m pytest apps/backend/tests'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ${IMAGE_REPO}:${IMAGE_TAG} -f apps/backend/Dockerfile apps/backend'
            }
        }

        stage('Security Scan') {
            steps {
                sh 'if command -v trivy >/dev/null 2>&1; then trivy image --exit-code 1 --severity HIGH,CRITICAL ${IMAGE_REPO}:${IMAGE_TAG}; else echo "trivy not installed; skipping image scan"; fi'
            }
        }

        stage('Helm Template Validation') {
            steps {
                sh 'helm template ai-backend deploy/helm/ai-backend --set image.repository=${IMAGE_REPO} --set image.tag=${IMAGE_TAG}'
            }
        }

        stage('Deploy to Staging') {
            when {
                expression { env.DEPLOY_STAGING == 'true' }
            }
            steps {
                sh 'helm upgrade --install ai-backend deploy/helm/ai-backend --namespace ai-staging --create-namespace --set image.repository=${IMAGE_REPO} --set image.tag=${IMAGE_TAG}'
            }
        }
    }
}
