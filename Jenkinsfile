pipeline {
  agent any

  options {
    // Jenkins declarative ya hace checkout SCM; si lo dejas en false y además haces checkout scm
    // tendrás checkout duplicado (no es grave). Para evitarlo:
    skipDefaultCheckout(true)
  }

  environment {
    DATABRICKS_HOST  = credentials('DATABRICKS_HOST')
    DATABRICKS_TOKEN = credentials('DATABRICKS_TOKEN')

    // Target del bundle (databricks.yml -> targets: dev:)
    DATABRICKS_BUNDLE_TARGET = 'dev'

    // Auth del CLI v2 por env vars
    DATABRICKS_AUTH_TYPE = 'pat'
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build wheel + prepare artifacts') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail

          test -f pyproject.toml
          test -f databricks.yml

          rm -rf .venv dist build *.egg-info artifacts wheel_path.txt

          python3.12 -m venv .venv
          source .venv/bin/activate

          python -m pip install -U pip setuptools wheel build

          python -m build --wheel
          ls -la dist

          ls -1 dist/*.whl | head -n 1 > wheel_path.txt
          mkdir -p artifacts
          cp -f "$(cat wheel_path.txt)" artifacts/cloudutils.whl

          echo "Wheel: $(cat wheel_path.txt)"
          ls -la artifacts
        '''
      }
    }

    stage('Install Databricks CLI v2 (no sudo)') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail

          # Forzamos al install.sh a instalar en $HOME/bin (en vez de /usr/local/bin)
          export DATABRICKS_RUNTIME_VERSION="jenkins"
          mkdir -p "$HOME/bin"

          curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh

          export PATH="$HOME/bin:$PATH"
          databricks version
          databricks bundle --help >/dev/null
          which databricks
        '''
      }
    }

    stage('Bundle validate') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail
          export PATH="$HOME/bin:$PATH"

          databricks bundle validate -t "${DATABRICKS_BUNDLE_TARGET}"
        '''
      }
    }

    stage('Bundle deploy') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail
          export PATH="$HOME/bin:$PATH"

          databricks bundle deploy -t "${DATABRICKS_BUNDLE_TARGET}"
        '''
      }
    }

    stage('Run integration tests (Databricks Job)') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail
          export PATH="$HOME/bin:$PATH"

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
