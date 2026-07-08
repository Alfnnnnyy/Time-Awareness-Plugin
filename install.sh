#!/usr/bin/env bash
#
# 🕐 Time Context Installer
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Alfnnnnyy/Time-Awareness-Plugin/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/Alfnnnnyy/Time-Awareness-Plugin/main/install.sh | bash -s -- --hermes
#
set -euo pipefail

REPO="https://raw.githubusercontent.com/Alfnnnnyy/Time-Awareness-Plugin/main"
INSTALL_DIR="${HOME}/.time-context"
MODE="cli"  # cli or hermes

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dir) INSTALL_DIR="$2"; shift 2 ;;
        --hermes) MODE="hermes"; shift ;;
        --help)
            echo "Usage: install.sh [--hermes] [--dir PATH]"
            exit 0 ;;
        *) echo "Unknown: $1"; exit 1 ;;
    esac
done

echo "🕐 Time Context Installer"
echo "══════════════════════════"

mkdir -p "${INSTALL_DIR}"

# Download core script
echo "📥 Downloading time_context.py..."
if command -v curl &>/dev/null; then
    curl -fsSL "${REPO}/time_context.py" -o "${INSTALL_DIR}/time_context.py"
else
    wget -q "${REPO}/time_context.py" -O "${INSTALL_DIR}/time_context.py"
fi
chmod +x "${INSTALL_DIR}/time_context.py"
echo "✅ time_context.py installed"

# Set timezone
SHELL_RC="${HOME}/.bashrc"
[[ "${SHELL-}" == *zsh* ]] && SHELL_RC="${HOME}/.zshrc"
if ! grep -q "USER_TIMEZONE=" "${SHELL_RC}" 2>/dev/null; then
    read -r -p "🔧 IANA timezone (e.g. Asia/Jayapura) [UTC]: " TZ
    TZ="${TZ:-UTC}"
    {
        echo ""
        echo "# 🕐 Time Context"
        echo "export USER_TIMEZONE=\"${TZ}\""
    } >> "${SHELL_RC}"
    echo "✅ USER_TIMEZONE=${TZ} added to ${SHELL_RC}"
fi

# Hermes plugin
if [[ "${MODE}" == "hermes" ]]; then
    echo "🔌 Installing Hermes plugin..."
    mkdir -p "${HOME}/.hermes/plugins/time-awareness"
    curl -fsSL "${REPO}/plugin.yaml" -o "${HOME}/.hermes/plugins/time-awareness/plugin.yaml"
    curl -fsSL "${REPO}/__init__.py" -o "${HOME}/.hermes/plugins/time-awareness/__init__.py"
    echo "✅ Hermes plugin installed"
    echo "   Run: hermes plugins enable time-awareness"
    echo "   Run: hermes config set plugins.entries.time-awareness.user_timezone \"${TZ}\""
fi

echo ""
echo "══════════════════════════"
echo "✅ Done"
echo "Usage: python3 ${INSTALL_DIR}/time_context.py [--format markdown|json] [--session <id>]"
