pipeline {
  agent any

  options {
    // Evita checkout duplicado (Jenkins declarative ya hace checkout SCM)
    skipDefaultCheckout(false)
  }

  environment {
    DATABRICKS_HOST  = credentials('DATABRICKS_HOST')
    DATABRICKS_TOKEN = credentials('DATABRICKS_TOKEN')

    // Target del bundle (databricks.yml -> targets: dev:)
    DATABRICKS_BUNDLE_TARGET = 'dev'

    // Auth del CLI moderno por env vars
    DATABRICKS_AUTH_TYPE = 'pat'
  }

  stages {

    // Si tu job es "Pipeline from SCM", Jenkins ya hace checkout.
    // Puedes borrar este stage si quieres; no rompe nada.
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Setup Python 3.12') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail

          pwd
          ls -la
          test -f pyproject.toml

          rm -rf .venv
          python3.12 -m venv .venv
          source .venv/bin/activate

          python -m pip install -U pip setuptools wheel
          python -m pip install -U build

          # Instala el Databricks CLI moderno dentro del venv (sin sudo)
          python -m pip install -U databricks

          python --version
          databricks version
          which databricks
        '''
      }
    }

    stage('Build wheel') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail
          source .venv/bin/activate

          rm -rf dist build *.egg-info
          python -m build --wheel

          echo "Wheel(s) in dist/:"
          ls -la dist

          ls -1 dist/*.whl | head -n 1 > wheel_path.txt
          echo "Wheel built: $(cat wheel_path.txt)"
        '''
      }
    }

    stage('Prepare bundle artifacts') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail

          WHEEL="$(cat wheel_path.txt)"
          mkdir -p artifacts
          cp -f "$WHEEL" artifacts/cloudutils.whl

          echo "Bundle artifacts:"
          ls -la artifacts
        '''
      }
    }

    stage('Bundle validate') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail
          source .venv/bin/activate

          databricks bundle validate -t "${DATABRICKS_BUNDLE_TARGET}"
        '''
      }
    }

    stage('Bundle deploy') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail
          source .venv/bin/activate

          databricks bundle deploy -t "${DATABRICKS_BUNDLE_TARGET}"
        '''
      }
    }

    stage('Run integration tests (Databricks Job)') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail
          source .venv/bin/activate

          databricks bundle run -t "${DATABRICKS_BUNDLE_TARGET}" cloudutils_integration_tests
        '''
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'dist/*.whl,artifacts/*,wheel_path.txt', fingerprint: true
    }
  }
}
