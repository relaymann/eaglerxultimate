# UltimateXServer architecture decision

**Status:** Proposed architecture; implementation not yet proven.

## The target is two separate responsibilities

Ultimate is a browser client for a Forge 1.6.4 modpack. The server must both accept the browser's Eagler transport and run the actual Forge 1.6.4 world with matching server-side mods. These responsibilities must not be conflated.

### A. UltimateXServer browser gateway

Responsibilities:

- Accept the browser's WebSocket connection.
- Negotiate the exact Eagler handshake family used by this client build.
- Decode Eagler game-message framing.
- Translate/forward Minecraft 1.6.4 packets without dropping unknown custom payloads.
- Preserve connection identity and disconnect reasons.
- Enforce frame sizes, timeouts, rate limits, and safe close behavior.
- Produce packet traces with sensitive player/session data redacted.

EaglerXServer is the foundation for investigating and reusing Eagler handshake and game-message components. Its current rewind API is a protocol translator extension inside an EaglerXServer runtime; it is not a generic TCP proxy API.

### B. Forge 1.6.4 dedicated backend

Responsibilities:

- Run the actual Minecraft 1.6.4 dedicated server.
- Load the server-compatible versions of the Ultimate mods.
- Own world state, player state, inventories, entities, tile entities, dimensions, and mod progression.
- Perform the FML mod-list/registry handshake.
- Handle mod-specific custom payload packets.

The uploaded browser ZIP contains client code and assets, but not the original mod JARs or a dedicated server distribution. A matching server mod set and configurations are still required.

## Proposed connection flow

1. Browser opens a WebSocket to the UltimateXServer gateway.
2. Gateway performs the Eagler handshake expected by the exact client build.
3. Gateway establishes the browser-side game-message channel.
4. Gateway connects to the Forge 1.6.4 backend.
5. Gateway translates only the framing/protocol differences proven by packet captures.
6. FML handshake and registered mod channels are forwarded or translated without silently stripping unknown messages.
7. The Forge backend remains authoritative for all world and mod state.

## Why not simply install EaglerXServer as a Forge plugin?

The existing EaglerXServer rewind extension point injects handlers into EaglerXServer's Netty pipeline and rewrites the Eagler handshake. The existing 1.5.2 implementation then speaks the EaglerXRewind login protocol and Minecraft 1.8 protocol 47. That is not equivalent to accepting a raw Forge 1.6.4 connection (Minecraft protocol 78) or forwarding Forge's FML handshake.

Therefore, the first implementation milestone is a protocol trace and a minimal gateway/backend bridge, not a claimed full-modpack translator.

## Deployment shapes to evaluate for MCServerHost

### Single host instance

One Java process hosts the gateway and launches/connects to the Forge backend as a child or embedded service. This is only acceptable if the host allows the required custom runtime, process management, memory, ports, and persistent storage.

### Two host instances

One instance runs the Forge 1.6.4 server and another runs the gateway. This is operationally cleaner, but depends on the provider allowing two free instances and private/public networking between them.

Do not assume either topology is supported by the selected host until its current plan and runtime restrictions are verified.

## Non-negotiable compatibility rules

- Do not translate Forge 1.6.4 to vanilla 1.8 and claim mod support.
- Do not drop unknown `FML`, `REGISTER`, `UNREGISTER`, or mod custom payload channels.
- Do not accept a mod list that differs from the backend unless the client/server mod compatibility rules explicitly permit it.
- Do not mark a feature supported based only on client-side class names.
- Keep unknown packet handling fail-closed until the packet boundary and state are known.
- Validate login, movement, chunk data, inventories, entities, tile entities, dimensions, and each mod network family independently.

## Required test gates

1. Capture the exact browser-to-gateway handshake.
2. Verify browser login against an instrumented protocol test server.
3. Verify gateway-to-Forge 1.6.4 connection.
4. Complete the FML mod-list and registry exchange.
5. Join a clean test world and verify movement/chunk streaming.
6. Verify a container and inventory round-trip.
7. Verify one modded tile entity and one modded entity.
8. Verify a dimension transition.
9. Repeat with multiple players and reconnects.
10. Verify save/restart persistence.
