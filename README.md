# UltimateXServer

**UltimateXServer** is an experimental fork of [EaglerXServer](https://github.com/lax1dude/eaglerxserver) focused on investigating browser multiplayer support for the Eaglercraft Ultimate Forge 1.6.4 modpack.

This repository retains the upstream EaglerXServer networking foundation and its existing platform integrations. Ultimate compatibility is being developed as a separate, explicitly experimental layer so that normal EaglercraftX behavior is not accidentally changed.

## Current status

**Research and compatibility-prototype stage — not yet playable with Ultimate.**

The supplied Ultimate browser bundle contains evidence of:

- Minecraft 1.6.4 and Forge Mod Loader code.
- A client described internally as an Eaglercraft client for Forge 1.6.4 modpacks based on EaglercraftX 1.8.
- Eagler handshake-family identifiers.
- Forge connection failure text and a `LAN NOT SUPPORTED` marker.

These strings establish what is present in the client bundle; they do **not** prove that an existing EaglerXServer translator can connect it to a Forge 1.6.4 dedicated server. The FML handshake, custom payload channels, packet IDs, mod registry synchronization, and mod-specific server behavior still need to be verified.

See [Ultimate protocol research](ultimate/PROTOCOL-RESEARCH.md) and the [modpack inventory](ultimate/MODPACK.md).

## Existing EaglerXServer foundation

The upstream project supports EaglercraftX 1.8, Eaglercraft 1.12.2, and Eaglercraft 1.5.2 clients, with protocol translator modules for older protocol families. It can be installed on Spigot, BungeeCord, or Velocity. Those capabilities are useful foundations, but are not a claim of Forge 1.6.4 modpack compatibility.

- Upstream source: https://github.com/lax1dude/eaglerxserver
- Upstream documentation: https://github.com/lax1dude/eaglerxserver/blob/main/README.md
- Existing translator API: `api/.../api/rewind/`
- Existing legacy translator: `rewind_v1_5/`

## Development setup

Requirements:

- Java 17 or newer
- Git
- Gradle wrapper included in this repository

Build all modules:

```bash
./gradlew build
```

Run the Ultimate client fingerprint audit against the provided ZIP or an extracted `classes.js`:

```bash
python3 tools/ultimate_client_audit.py /path/to/ultimate.zip
```

Run the audit tool's unit tests:

```bash
python3 -m unittest discover -s tools/tests -v
```

The audit is a string-fingerprint aid, not a wire-protocol validator.

## Planned milestones

1. Reproducibly fingerprint the Ultimate client and document its exact handshake behavior.
2. Capture and decode a real Ultimate-to-server connection attempt.
3. Determine whether EaglerXServer's existing rewind API can host a 1.6.4 translator or whether a dedicated adapter is required.
4. Validate a stock Forge 1.6.4 backend before attempting mod-specific behavior.
5. Add compatibility in layers: login, movement/world packets, FML mod handshake, registries, then individual mod systems.
6. Prepare and test a deployable proxy/backend layout for MCServerHost.

## Hosting target

MCServerHost is the intended deployment target, but hosting compatibility is not yet verified. The final deployment will require the host to support the selected proxy runtime, the Forge 1.6.4 backend, required Java versions, persistent world storage, and the necessary WebSocket/public networking configuration.

## Attribution and licensing

This project is a fork of EaglerXServer by lax1dude and contributors. The upstream license and notices are retained. See [LICENSE](LICENSE) and the upstream README for the original project's contribution and forking terms.