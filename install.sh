#!/usr/bin/env bash
#
# 🕐 Time Context — universal installer
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Alfnnnnyy/Time-Awareness-Plugin/main/install.sh | bash
#
set -euo pipefail

REPO="https://raw.githubusercontent.com/Alfnnnnyy/Time-Awareness-Plugin/main"
INSTALL_DIR="${HOME}/.time-context"
INSTALL_HERMES=false
HERMES_PLUGIN_DIR="${HOME}/.hermes/plugins/time-awareness"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dir) INSTALL_DIR="$2"; shift 2 ;;
        --hermes) INSTALL_HERMES=true; shift ;;
        --help)
            echo "Usage: install.sh [--dir PATH] [--hermes]"
            echo "  --dir PATH    Install to custom directory (default: ~/.time-context)"
            echo "  --hermes      Also install as Hermes Agent plugin"
            exit 0 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

echo "🕐 Time Context Installer"
echo "═══════════════════════════"

mkdir -p "${INSTALL_DIR}"
echo "📥 Downloading time_context.py..."
if command -v curl &>/dev/null; then
    curl -fsSL "${REPO}/time_context.py" -o "${INSTALL_DIR}/time_context.py"
elif command -v wget &>/dev/null; then
    wget -q "${REPO}/time_context.py" -O "${INSTALL_DIR}/time_context.py"
else
    echo "❌ Neither curl nor wget found."
    exit 1
fi
chmod +x "${INSTALL_DIR}/time_context.py"
echo "✅ Installed to ${INSTALL_DIR}/time_context.py"

# Shell integration
SHELL_RC="${HOME}/.bashrc"
[[ "${SHELL-}" == *zsh* ]] && SHELL_RC="${HOME}/.zshrc"

if ! grep -q "USER_TIMEZONE=" "${SHELL_RC}" 2>/dev/null; then
    echo ""
    echo "🔧 Set your timezone:"
    read -r -p "   IANA timezone (e.g. Asia/Jayapura) [UTC]: " TZ
    TZ="${TZ:-UTC}"
    {
        echo ""
        echo "# 🕐 Time Context"
        echo "export USER_TIMEZONE=\"${TZ}\""
        echo "export PATH=\"\${PATH}:${INSTALL_DIR}\""
    } >> "${SHELL_RC}"
    echo "✅ Added USER_TIMEZONE=${TZ} to ${SHELL_RC}"
fi

if [[ "${INSTALL_HERMES}" == true ]]; then
    echo "🔌 Installing Hermes plugin..."
    mkdir -p "${HERMES_PLUGIN_DIR}"
    curl -fsSL "${REPO}/plugin.yaml" -o "${HERMES_PLUGIN_DIR}/plugin.yaml"
    curl -fsSL "${REPO}/__init__.py"  -o "${HERMES_PLUGIN_DIR}/__init__.py"
    echo "✅ Hermes plugin installed"
    echo "   Run: hermes plugins enable time-awareness"
    echo "   Then: hermes config set plugins.entries.time-awareness.user_timezone \"${TZ}\""
fi

echo ""
echo "═══════════════════════════"
echo "✅ Done"
echo "Usage: time_context.py [--format markdown|json] [--session <id>]"
echo "See: https://github.com/Alfnnnnyy/Time-Awareness-Plugin"
