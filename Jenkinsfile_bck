pipeline {
  agent any

  options {
    skipDefaultCheckout(false)
  }

  environment {
    DATABRICKS_HOST = credentials('DATABRICKS_HOST')
    DATABRICKS_TOKEN = credentials('DATABRICKS_TOKEN')
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

  stage('Setup Python 3.12') {
    steps {
      dir('.') {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail
          pwd
          ls -la
          test -f pyproject.toml

          rm -rf .venv
          python3.12 -m venv .venv
          source .venv/bin/activate
          python -m pip install -U pip setuptools wheel
  
          python -m pip install -e ".[dev]"
          pip show databricks-connect
        '''
      }
    }
  }

    stage('Unit tests') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail
          . .venv/bin/activate
          pytest -q tests/unit
        '''
      }
    }

    stage('Integration tests (Serverless)') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail
          . .venv/bin/activate
          # Fuerza serverless en Connect

          export DATABRICKS_HOST="${DATABRICKS_HOST}"
          export DATABRICKS_TOKEN="${DATABRICKS_TOKEN}"
          export DATABRICKS_SERVERLESS_COMPUTE_ID="auto"
          mkdir -p ~/.databricks
          cat > ~/.databricks/config << EOF
[DEFAULT]
host = ${DATABRICKS_HOST}
token = ${DATABRICKS_TOKEN}
serverless_compute_id = auto
EOF

          pytest -q -m integration tests/integration
        '''
      }
    }
  }
}
