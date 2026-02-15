pipeline {
  agent any

  options {
    skipDefaultCheckout(false)
  }

  environment {
    DATABRICKS_HOST = credentials('DATABRICKS_HOST')
    DATABRICKS_TOKEN = credentials('DATABRICKS_TOKEN')

    // Target del bundle (si en databricks.yml tienes targets: dev:)
    DATABRICKS_BUNDLE_TARGET = 'dev'

    // Fuerza auth por env vars para el CLI moderno
    DATABRICKS_AUTH_TYPE = 'pat'
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
          python -m pip install -U build          
  
        '''
      }
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

          # Guardar ruta del wheel para siguientes stages
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

    stage('Install Databricks CLI (bundle)') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail

          # Instala el Databricks CLI moderno (soporta `databricks bundle ...`)
          # Se instala en ~/.databricks/bin/databricks
          curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | bash

          # Asegura que está en PATH para este build
          export PATH="$HOME/.databricks/bin:$PATH"

          databricks version
        '''
      }
    }

    stage('Bundle validate') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail
          export PATH="$HOME/.databricks/bin:$PATH"

          # Validar bundle
          databricks bundle validate -t "${DATABRICKS_BUNDLE_TARGET}"
        '''
      }
    }

    stage('Bundle deploy') {
      steps {
        sh '''#!/usr/bin/env bash
          set -euxo pipefail
          export PATH="$HOME/.databricks/bin:$PATH"

          # Deploy bundle al workspace
          databricks bundle deploy -t "${DATABRICKS_BUNDLE_TARGET}"
        '''
      }
    }


    stage('Run integration tests (Databricks Job)') {
          steps {
            sh '''#!/usr/bin/env bash
              set -euxo pipefail
              export PATH="$HOME/.databricks/bin:$PATH"

              # Ejecuta el job definido en databricks.yml.
              # Cambia "cloudutils_integration_tests" por el nombre real en resources.jobs.<NOMBRE>
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
