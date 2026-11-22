#!/usr/bin/env python3
"""Inspect an Eaglercraft Ultimate client bundle for multiplayer/protocol clues.

This is a fingerprinting aid, not a protocol compatibility validator. It scans
large compiled JavaScript files incrementally so the 100+ MB client need not be
loaded into memory.
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from typing import BinaryIO, Iterable

MARKERS: dict[str, tuple[bytes, ...]] = {
    "minecraft_1_6_4": (
        b"Minecraft 1.6.4",
        b"Starting integrated eaglercraft server version 1.6.4",
    ),
    "eaglercraftx_1_8_based_client": (
        b"based on EaglercraftX 1.8",
    ),
    "forge_mod_loader": (
        b"Forge Mod Loader",
        b"FMLMainChannel",
        b"fml.modStates",
    ),
    "forge_connection_failure_text": (
        b"Forge Mod Loader could not connect to this server",
    ),
    "lan_disabled_marker": (
        b"LAN NOT SUPPORTED",
    ),
    "eagler_handshake_families": (
        b"STANDARD_OFFLINE_V1",
        b"EAGLERX_V1",
        b"EAGLERX_SIGNED_V1",
        b"EAGLER_1_5_V1",
        b"EAGLER_1_5_V2",
        b"EAGLER_BETA_V1",
        b"PEYTON_V1",
        b"PEYTON_V2",
    ),
    "forge_world_import_marker": (
        b"epk/world164forge",
        b"singleplayer 1.6.4 forge world",
    ),
}

CLIENT_CANDIDATES = (
    "javascript_web/classes.js",
    "javascript_offline/Eaglercraft_Offline.html",
)


def scan_stream(stream: BinaryIO, chunk_size: int = 1024 * 1024) -> dict[str, bool]:
    """Find known byte markers without loading the complete client into memory."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")

    found = {name: False for name in MARKERS}
    all_markers = [
        (name, marker)
        for name, values in MARKERS.items()
        for marker in values
    ]
    overlap = max(len(marker) for _, marker in all_markers) - 1
    tail = b""

    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break

        window = tail + chunk
        for name, marker in all_markers:
            if not found[name] and marker in window:
                found[name] = True

        if all(found.values()):
            break
        tail = window[-overlap:] if overlap else b""

    return found


def scan_path(path: Path) -> tuple[str, dict[str, bool]]:
    """Scan a ZIP bundle or a standalone compiled JavaScript file."""
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            for candidate in CLIENT_CANDIDATES:
                if candidate in names:
                    with archive.open(candidate) as stream:
                        return candidate, scan_stream(stream)
        raise ValueError("No recognized Ultimate JavaScript client found in ZIP")

    with path.open("rb") as stream:
        return str(path), scan_stream(stream)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "client",
        type=Path,
        help="Ultimate ZIP bundle or compiled classes.js",
    )
    args = parser.parse_args(argv)

    try:
        scanned, findings = scan_path(args.client)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"audit failed: {exc}", file=sys.stderr)
        return 2

    report = {
        "scanned_file": scanned,
        "findings": findings,
        "interpretation": [
            "Markers identify client-side code and strings only; they do not prove server compatibility.",
            "A Forge 1.6.4 backend requires matching FML handshake and mod-channel behavior.",
            "The EaglerXServer legacy translator must be tested against this client's actual wire traffic.",
        ],
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
