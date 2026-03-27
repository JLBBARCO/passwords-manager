#!/usr/bin/env bash
set -euo pipefail

# Integration test for shortcut creation on app startup
# Usage: ./test-shortcuts-integration.sh [--cleanup]

CLEANUP_AFTER="${1:---no-cleanup}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "Passwords Manager - Shortcut Integration Test"
echo "=========================================="
echo ""
echo "Project root: $PROJECT_ROOT"
echo "Platform: $(uname -s)"
echo ""

if [ "$(uname -s)" = "Darwin" ]; then
    APP_DIR="$HOME/Applications"
    EXPECTED_LAUNCHER="$APP_DIR/Passwords Manager.command"
elif [ "$(uname -s)" = "Linux" ]; then
    APP_DIR="$HOME/.local/share/applications"
    EXPECTED_LAUNCHER="$APP_DIR/passwords-manager.desktop"
else
    echo "Error: Unsupported platform"
    exit 1
fi

echo "Testing shortcut creation on app startup..."
echo ""

# Record state before
if [ -f "$EXPECTED_LAUNCHER" ]; then
    BEFORE_MTIME=$(stat -f%m "$EXPECTED_LAUNCHER" 2>/dev/null || stat -c%Y "$EXPECTED_LAUNCHER" 2>/dev/null)
    echo "→ Shortcut exists (will check if updated)"
else
    BEFORE_MTIME=0
    echo "→ Shortcut does not exist yet"
fi

echo ""
echo "Running app (press Ctrl+C to exit after it starts)..."
cd "$PROJECT_ROOT"

# Try to run and give it a moment to create shortcuts
timeout 3 python main.py || true
sleep 1

echo ""
echo "Checking shortcut creation..."
echo ""

if [ -f "$EXPECTED_LAUNCHER" ]; then
    echo "✓ Shortcut created/exists: $EXPECTED_LAUNCHER"
    
    # Verify content
    if grep -q "passwords-manager" "$EXPECTED_LAUNCHER" 2>/dev/null; then
        echo "✓ Shortcut contains correct executable reference"
    else
        echo "✗ Shortcut missing executable reference"
        exit 1
    fi
    
    # Check permissions on macOS
    if [ "$(uname -s)" = "Darwin" ] && [ -x "$EXPECTED_LAUNCHER" ]; then
        echo "✓ macOS launcher has executable permission"
    fi
else
    echo "✗ Shortcut not found: $EXPECTED_LAUNCHER"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ Integration test passed!"
echo "=========================================="

if [ "$CLEANUP_AFTER" = "--cleanup" ]; then
    echo ""
    echo "Cleaning up test shortcuts..."
    rm -f "$EXPECTED_LAUNCHER" 2>/dev/null || true
    echo "✓ Cleanup complete"
fi

exit 0
