import sys
import subprocess

# Ejecuta solo los tests de integración
raise SystemExit(
    subprocess.call([sys.executable, "-m", "pytest", "-q", "-m", "integration", "tests/integration"])
)
