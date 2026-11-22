#!/usr/bin/env python3
"""Inspect an Eaglercraft Ultimate client bundle for multiplayer/protocol clues.

This is a fingerprinting aid, not a protocol compatibility validator. It scans
large compiled JavaScript files incrementally and reads source-map class names
without loading the 100+ MB JavaScript bundle into memory.
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from typing import BinaryIO, Iterable, TextIO

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
SOURCE_MAP_CANDIDATES = (
    "javascript_web/classes.js.map",
)

# Source-map names are class-path evidence only. Their presence does not prove
# that the classes execute in the browser or that a server supports the mod.
NETWORK_SOURCE_MARKERS: dict[str, tuple[str, ...]] = {
    "minecraft_legacy_packet_layer": (
        "net/minecraft/network/packet/Packet.java",
        "net/minecraft/network/packet/Packet2ClientProtocol.java",
        "net/minecraft/network/packet/Packet250CustomPayload.java",
        "net/minecraft/network/NetLoginHandler.java",
        "net/minecraft/network/NetServerHandler.java",
    ),
    "forge_fml_handshake_layer": (
        "cpw/mods/fml/common/network/FMLNetworkHandler.java",
        "cpw/mods/fml/common/network/NetworkRegistry.java",
        "cpw/mods/fml/common/network/FMLPacket.java",
        "cpw/mods/fml/common/network/ModListRequestPacket.java",
        "cpw/mods/fml/common/network/ModListResponsePacket.java",
        "cpw/mods/fml/common/network/ModIdentifiersPacket.java",
        "cpw/mods/fml/common/network/ModMissingPacket.java",
        "cpw/mods/fml/common/network/ModIdMapPacket.java",
    ),
    "forge_custom_network_layer": (
        "net/minecraftforge/common/network/ForgeNetworkHandler.java",
        "net/minecraftforge/common/network/ForgePacketHandler.java",
        "net/minecraftforge/common/network/ForgePacket.java",
        "net/minecraftforge/common/network/packet/DimensionRegisterPacket.java",
    ),
    "eagler_websocket_client_layer": (
        "net/lax1dude/eaglercraft/socket/EaglerNetworkManagerClientWS.java",
        "net/lax1dude/eaglercraft/socket/protocol/client/GameProtocolMessageController.java",
        "net/lax1dude/eaglercraft/socket/protocol/client/ClientV4MessageHandler.java",
        "net/lax1dude/eaglercraft/socket/protocol/client/ClientV3MessageHandler.java",
    ),
    "integrated_server_layer": (
        "net/lax1dude/eaglercraft/sp/server/EaglerIntegratedServerWorker.java",
        "net/lax1dude/eaglercraft/sp/server/internal/ServerPlatformSingleplayer.java",
    ),
}

MOD_NETWORK_PREFIXES = (
    "appeng/common/network/",
    "buildcraft/core/network/",
    "buildcraft/transport/network/",
    "micdoodle8/mods/galacticraft/core/network/",
    "net/aetherteam/aether/packets/",
    "mods/railcraft/common/util/network/",
    "mcp/mobius/waila/network/",
    "tconstruct/",
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


def scan_source_map(stream: TextIO) -> dict[str, object]:
    """Summarize relevant source-map paths; no original source text is embedded."""
    source_map = json.load(stream)
    sources = source_map.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("source map 'sources' must be an array")

    source_set = {item for item in sources if isinstance(item, str)}
    groups = {
        group: {
            "present": [path for path in paths if path in source_set],
            "missing": [path for path in paths if path not in source_set],
        }
        for group, paths in NETWORK_SOURCE_MARKERS.items()
    }
    mod_network_classes = sorted(
        path for path in source_set
        if path.startswith(MOD_NETWORK_PREFIXES)
        and ("network" in path.lower() or "/packets/" in path.lower())
    )
    return {
        "source_count": len(source_set),
        "groups": groups,
        "mod_network_class_count": len(mod_network_classes),
        "mod_network_classes": mod_network_classes,
        "source_content_embedded": bool(source_map.get("sourcesContent")),
    }


def scan_path(path: Path) -> tuple[str, dict[str, bool], dict[str, object] | None]:
    """Scan a ZIP bundle or standalone compiled JavaScript file."""
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            client_name = next((p for p in CLIENT_CANDIDATES if p in names), None)
            if client_name is None:
                raise ValueError("No recognized Ultimate JavaScript client found in ZIP")
            with archive.open(client_name) as stream:
                findings = scan_stream(stream)

            source_map_name = next((p for p in SOURCE_MAP_CANDIDATES if p in names), None)
            inventory = None
            if source_map_name is not None:
                with archive.open(source_map_name) as raw:
                    import io
                    with io.TextIOWrapper(raw, encoding="utf-8") as text_stream:
                        inventory = scan_source_map(text_stream)
            return client_name, findings, inventory

    with path.open("rb") as stream:
        findings = scan_stream(stream)
    return str(path), findings, None


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "client",
        type=Path,
        help="Ultimate ZIP bundle or compiled classes.js",
    )
    args = parser.parse_args(argv)

    try:
        scanned, findings, inventory = scan_path(args.client)
    except (OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        print(f"audit failed: {exc}", file=sys.stderr)
        return 2

    report = {
        "scanned_file": scanned,
        "findings": findings,
        "source_map_inventory": inventory,
        "interpretation": [
            "Markers and source-map paths identify client-side code only; they do not prove server compatibility.",
            "The bundle includes a legacy Minecraft packet layer, Forge Mod Loader packet classes, and Eagler WebSocket client classes.",
            "A Forge 1.6.4 backend still requires a matching Eagler transport, FML handshake, registries, and mod-specific server behavior.",
            "The source map contains class paths but no embedded original source content.",
        ],
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
