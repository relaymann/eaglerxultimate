# UltimateXServer development log

## 2026-11-22 — client protocol audit and foundation hardening

### Completed

- Confirmed the connected repository is `relaymann/eaglerxultimate` and all work was committed directly to `main`.
- Rebranded the fork and documented the experimental status and scope.
- Added a reproducible client audit utility that scans large JavaScript bundles in chunks and inspects source-map class paths.
- Added unit tests for chunk-boundary matching, empty findings, invalid chunk sizes, malformed source maps, source-map inventories, and ZIP integration.
- Added CI for Python audit tests and the full Java/Gradle build.
- Inspected the supplied `ultimate.zip` and recorded archive/file SHA-256 hashes in `client-inventory.json`.
- Confirmed the source map lists 13,726 source paths and does not embed original source text.
- Found client-side Minecraft packet, Forge FML handshake, Forge custom network, Eagler WebSocket, integrated-server, and mod-specific packet class families.
- Counted 107 class paths in the inspected mod-network families; this is client-side inventory evidence, not server compatibility.
- Documented that the WASM launcher accepts a `?server=` query parameter and starts with an empty server list in its shipped HTML.
- Documented a proposed gateway + Forge 1.6.4 backend architecture and the MCServerHost deployment questions.
- Fixed a registry collision bug in `RewindService.registerLegacyProtocol`: two translators can no longer silently claim the same legacy protocol ID.

### Verification

- GitHub Actions run 7 completed successfully: Python audit tests and full Java/Gradle build.
- GitHub Actions run 8 completed successfully: Python audit tests and full Java/Gradle build.
- GitHub Actions run 9 completed successfully: Python audit tests and full Java/Gradle build.
- Later audit-tool runs also passed after source-map and ZIP integration coverage was added.
- The Java build for the latest registry-collision fix was still running at the time of this log entry; check the Actions page before treating it as verified.

### Important conclusions

- The supplied ZIP is a browser client bundle and assets, not the original mod source/JAR collection or a dedicated server.
- The source map provides class names, not original Java source text.
- The existing EaglerXServer rewind extension point handles Eagler handshake/message translation inside its server pipeline. It is not, by itself, a generic TCP proxy to a Forge 1.6.4 server.
- No successful Ultimate-to-Forge multiplayer handshake has been demonstrated yet.

### Next tasks

1. Inspect the Ultimate client's actual Eagler WebSocket handshake and game-message flow.
2. Capture a real browser connection trace and identify the exact Eagler handshake family and Minecraft protocol selection.
3. Establish a controlled Forge 1.6.4 backend with the exact server-side mod set.
4. Prototype the smallest safe Eagler WebSocket gateway-to-Forge packet bridge.
5. Validate FML handshake and mod registry parity before attempting world play.
6. Test login, movement, chunks, containers, entities, tile entities, dimensions, reconnects, and persistence.
