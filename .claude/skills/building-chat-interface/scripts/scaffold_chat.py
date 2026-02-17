#!/usr/bin/env python3
"""Scaffold a chat interface project structure.

Generates the initial file structure for a production-grade chat interface
based on framework, transport, and feature selections.

Usage:
    python scaffold_chat.py --framework react --transport websocket --output ./src/chat
    python scaffold_chat.py --framework vue --transport sse --output ./src/chat
    python scaffold_chat.py --framework vanilla --transport polling --output ./src/chat
"""

import argparse
import os
import sys
import json
from pathlib import Path

FRAMEWORKS = ["react", "vue", "svelte", "vanilla"]
TRANSPORTS = ["websocket", "sse", "polling"]

# File structure templates per framework
STRUCTURES = {
    "react": {
        "components/ChatProvider.tsx": "// Chat context provider with useReducer state management",
        "components/ChatWindow.tsx": "// Main chat layout container",
        "components/MessageList.tsx": "// Virtualized, accessible message list with aria-live",
        "components/MessageBubble.tsx": "// Individual message with role-based styling",
        "components/InputBar.tsx": "// Auto-resize textarea with Enter to send",
        "components/StatusBar.tsx": "// Connection state indicator",
        "components/TypingIndicator.tsx": "// Typing animation with aria-live announcement",
        "hooks/useChatConnection.ts": "// Transport hook (WebSocket/SSE/polling)",
        "hooks/useChatState.ts": "// Chat state machine hook",
        "hooks/useAutoScroll.ts": "// Smart auto-scroll (only when near bottom)",
        "types/chat.ts": "// ChatMessage, ChatEvent, ConnectionStatus interfaces",
        "transport/adapter.ts": "// ChatTransport interface (transport-agnostic)",
        "styles/chat.css": "/* CSS custom properties for theming + responsive breakpoints */",
        "index.ts": "// Public API exports",
    },
    "vue": {
        "components/ChatWindow.vue": "<!-- Main chat layout container -->",
        "components/MessageList.vue": "<!-- Accessible message list -->",
        "components/MessageBubble.vue": "<!-- Individual message bubble -->",
        "components/InputBar.vue": "<!-- Auto-resize input with keyboard shortcuts -->",
        "components/StatusBar.vue": "<!-- Connection state indicator -->",
        "composables/useChatConnection.ts": "// Transport composable",
        "composables/useChatState.ts": "// State machine composable",
        "types/chat.ts": "// TypeScript interfaces",
        "transport/adapter.ts": "// ChatTransport interface",
        "styles/chat.css": "/* CSS custom properties for theming */",
        "index.ts": "// Public API exports",
    },
    "svelte": {
        "components/ChatWindow.svelte": "<!-- Main chat layout -->",
        "components/MessageList.svelte": "<!-- Accessible message list -->",
        "components/MessageBubble.svelte": "<!-- Message bubble -->",
        "components/InputBar.svelte": "<!-- Input with keyboard shortcuts -->",
        "stores/chat.ts": "// Writable stores for messages, status",
        "transport/adapter.ts": "// ChatTransport interface",
        "types/chat.ts": "// TypeScript interfaces",
        "styles/chat.css": "/* CSS custom properties */",
        "index.ts": "// Public API",
    },
    "vanilla": {
        "chat.ts": "// Main ChatWidget class",
        "components/message-list.ts": "// MessageList Web Component",
        "components/input-bar.ts": "// InputBar Web Component",
        "transport/adapter.ts": "// ChatTransport interface",
        "types/chat.ts": "// TypeScript interfaces",
        "styles/chat.css": "/* CSS custom properties */",
        "index.ts": "// Public API",
    },
}

TRANSPORT_FILES = {
    "websocket": "transport/websocket.ts",
    "sse": "transport/sse.ts",
    "polling": "transport/polling.ts",
}


def scaffold(framework: str, transport: str, output_dir: str) -> list[str]:
    """Generate chat interface file structure."""
    output_path = Path(output_dir)
    created_files = []

    # Create base structure
    files = STRUCTURES[framework].copy()

    # Add transport-specific file
    transport_file = TRANSPORT_FILES[transport]
    files[transport_file] = f"// {transport.title()} transport implementation"

    for filepath, placeholder in sorted(files.items()):
        full_path = output_path / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)

        if full_path.exists():
            print(f"  SKIP  {filepath} (already exists)")
            continue

        full_path.write_text(placeholder + "\n")
        created_files.append(filepath)
        print(f"  CREATE  {filepath}")

    return created_files


def main():
    parser = argparse.ArgumentParser(description="Scaffold a chat interface project")
    parser.add_argument(
        "--framework",
        choices=FRAMEWORKS,
        required=True,
        help="UI framework to use",
    )
    parser.add_argument(
        "--transport",
        choices=TRANSPORTS,
        required=True,
        help="Real-time transport protocol",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory for generated files",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )

    args = parser.parse_args()

    print(f"\nScaffolding {args.framework} chat interface with {args.transport} transport\n")
    print(f"Output: {args.output}\n")

    created = scaffold(args.framework, args.transport, args.output)

    print(f"\nCreated {len(created)} files.")

    if args.json:
        result = {
            "framework": args.framework,
            "transport": args.transport,
            "output_dir": args.output,
            "files_created": created,
            "total": len(created),
        }
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
