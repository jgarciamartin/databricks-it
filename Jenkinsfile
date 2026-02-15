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
        sh '''#!/usr/bin/env bash
          set -euxo pipefail
          python3.12 -m venv .venv
          . .venv/bin/activate
          pip install -U pip
          pip install -e ".[dev]"
        '''
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
