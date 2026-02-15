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
        '''
      }
    }

    stage('Install Databricks CLI v2 (no sudo)') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail

          mkdir -p "$HOME/.local/bin"
          export PATH="$HOME/.local/bin:$PATH"

          ARCH="$(uname -m)"
          if [ "$ARCH" = "x86_64" ]; then
            ASSET="databricks_linux_amd64"
          elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
            ASSET="databricks_linux_arm64"
          else
            echo "Unsupported architecture: $ARCH"
            exit 1
          fi

          curl -fsSL -o "$HOME/.local/bin/databricks" \
            "https://github.com/databricks/cli/releases/latest/download/${ASSET}"
          chmod +x "$HOME/.local/bin/databricks"

          databricks version
          databricks bundle --help >/dev/null
        '''
      }
    }

    stage('Bundle validate') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail
          export PATH="$HOME/.local/bin:$PATH"

          databricks bundle validate -t "${DATABRICKS_BUNDLE_TARGET}"
        '''
      }
    }

    stage('Bundle deploy') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail
          export PATH="$HOME/.local/bin:$PATH"

          databricks bundle deploy -t "${DATABRICKS_BUNDLE_TARGET}"
        '''
      }
    }

    stage('Run integration tests (Databricks Job)') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail
          export PATH="$HOME/.local/bin:$PATH"

          # Debe coincidir con resources.jobs.<nombre> en databricks.yml
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
