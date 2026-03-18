#!/usr/bin/env bash
#
# Setup 4 self-hosted GitHub Actions runners on deploy@2.56.122.47.
#
# Prerequisites:
#   - SSH access: ssh deploy@2.56.122.47
#   - Docker installed and deploy user in docker group
#   - A GitHub runner registration token (from repo Settings > Actions > Runners)
#
# Usage:
#   ./deploy/setup-runners.sh <REGISTRATION_TOKEN>
#
# The runners are already installed and running on the host.
# This script is for reference / re-provisioning only.

set -euo pipefail

TOKEN="${1:?Usage: $0 <GITHUB_RUNNER_REGISTRATION_TOKEN>}"
REPO_URL="https://github.com/gutnikov/trello-clone"
HOST="deploy@2.56.122.47"
RUNNER_DIR="/home/deploy/actions-runners"
RUNNER_VERSION="2.332.0"

echo "=== Setting up 4 GitHub Actions runners on ${HOST} ==="

ssh "${HOST}" bash -s <<REMOTE_SCRIPT
set -euo pipefail

RUNNER_DIR="${RUNNER_DIR}"
RUNNER_VERSION="${RUNNER_VERSION}"
REPO_URL="${REPO_URL}"
TOKEN="${TOKEN}"

# Install tooling needed by CI jobs
echo "--- Installing CI tooling ---"
# uv (Python)
which uv || curl -LsSf https://astral.sh/uv/install.sh | sh
# pnpm (Node.js)
which pnpm || npm install -g pnpm@10
# agent-browser (E2E)
which agent-browser || (npm install -g agent-browser && agent-browser install)

echo "--- Setting up runners ---"
for i in 1 2 3 4; do
  if [ "\$i" -eq 1 ]; then
    NAME="trello-clone"
    AGENT_NAME="trello-clone-runner"
  else
    NAME="trello-clone-\$i"
    AGENT_NAME="trello-clone-runner-\$i"
  fi

  DIR="\${RUNNER_DIR}/\${NAME}"

  if [ -f "\${DIR}/.runner" ]; then
    echo "Runner \${NAME} is already configured, skipping"
    continue
  fi

  echo "--- Configuring runner: \${NAME} ---"
  mkdir -p "\${DIR}"
  cd "\${DIR}"

  # Download runner if not present
  if [ ! -f "./config.sh" ]; then
    curl -o actions-runner.tar.gz -L \
      "https://github.com/actions/runner/releases/download/v\${RUNNER_VERSION}/actions-runner-linux-x64-\${RUNNER_VERSION}.tar.gz"
    tar xzf actions-runner.tar.gz
    rm -f actions-runner.tar.gz
  fi

  # Configure
  ./config.sh \
    --url "\${REPO_URL}" \
    --token "\${TOKEN}" \
    --name "\${AGENT_NAME}" \
    --labels "self-hosted,Linux,X64" \
    --work "_work" \
    --unattended \
    --replace

  # Install as user service
  ./svc.sh install "\$(whoami)" || true
  ./svc.sh start || true

  echo "Runner \${NAME} started"
done

echo "=== All 4 runners configured ==="
REMOTE_SCRIPT
