# Ultimate client protocol research

**Status:** Initial static fingerprint completed. No successful live server handshake has been demonstrated.

## Evidence from the supplied client bundle

The audit utility scans `javascript_web/classes.js` from the uploaded Ultimate ZIP and currently finds all of the following markers:

| Marker | What it establishes | What it does not establish |
|---|---|---|
| `Minecraft 1.6.4` | The client embeds Minecraft 1.6.4 code/metadata | The exact server-side protocol implementation |
| `An Eaglercraft client for Forge 1.6.4 modpacks, based on EaglercraftX 1.8` | The client identifies itself as a Forge 1.6.4 modpack client based on EaglercraftX 1.8 | That it is wire-compatible with stock EaglerXServer |
| `Forge Mod Loader`, `FMLMainChannel`, `fml.modStates` | Forge Mod Loader logic and channel names are present | Which FML handshake variant and packet ordering are used |
| `Forge Mod Loader could not connect to this server` | The client contains a user-facing FML connection failure path | The precise reason a particular server will fail |
| `LAN NOT SUPPORTED` | A LAN-related feature is explicitly unavailable in this client build | That remote dedicated multiplayer is impossible |
| `STANDARD_OFFLINE_V1`, `EAGLERX_V1`, `EAGLERX_SIGNED_V1`, legacy family names | Multiple Eagler connection families are embedded | Which family this build selects for a real remote connection |
| `epk/world164forge` and `singleplayer 1.6.4 forge world` | The client supports importing/exporting a Forge 1.6.4 singleplayer world format | That its integrated server is a standalone dedicated server |

These findings were reproduced with:

```bash
python3 tools/ultimate_client_audit.py /path/to/ultimate.zip
python3 -m unittest discover -s tools/tests -v
```

## Architectural implications

EaglerXServer's existing rewind API is designed to attach a legacy protocol translator to the Netty connection pipeline. The existing `rewind_v1_5` module is a useful implementation reference, but a vanilla protocol translation is not equivalent to Forge modpack support.

A working Ultimate connection may require all of the following:

1. Correct Eaglercraft browser handshake and frame handling.
2. Correct Minecraft 1.6.4 packet framing and packet IDs.
3. Forge Mod Loader handshake negotiation, including the relevant custom payload channels.
4. Mod list and registry compatibility checks.
5. Correct forwarding of mod custom payload packets between the browser client and Forge backend.
6. Server-side Forge 1.6.4 and the required server-compatible mods.
7. Additional protocol or state translation if the browser client uses a different base wire protocol from the Forge server.

Do not mark a mod as supported merely because the client contains its classes or metadata.

## Next engineering tasks

- [ ] Capture the client's actual Eagler handshake family, Minecraft protocol number, brand, and version.
- [ ] Capture a full FML login exchange against a known-compatible Forge 1.6.4 test server.
- [ ] Compare the captured exchange with the current EaglerXServer handshake and rewind pipeline.
- [ ] Build a minimal pass-through/translator prototype before implementing any mod-specific packets.
- [ ] Verify login and movement with a clean Forge 1.6.4 server.
- [ ] Add mods incrementally and record server/client mod-list parity.
- [ ] Test dimensions, tile entities, entities, inventories, and custom payload channels separately.

## Safety and compatibility rule

The first prototype must fail closed on an unknown or incomplete FML handshake. It must not silently strip mod channels or pretend a vanilla login is a successful modded login; doing so can corrupt inventories, block states, entities, or world data.

## Existing rewind implementation checked

The current `rewind_v1_5` source confirms why simply enabling the existing translator is not a solution:

- `RewindProtocol.getLegacyProtocols()` returns protocol ID `69` for its Eaglercraft 1.5.2 client.
- Its initializer rewrites the Eagler handshake to Eagler protocol `5` and Minecraft protocol `47` (Minecraft 1.8), identifying itself as `EaglerXRewind` / `1.5.2`.
- Its handshake codec then negotiates the EaglerXRewind login with the 1.8 backend.

Ultimate identifies itself as a Forge 1.6.4 modpack client. Therefore the 1.5.2 translator is a reference for how to plug a translator into EaglerXServer, not a compatible Ultimate translator. A Forge 1.6.4 backend must receive the correct 1.6.4/FML exchange; translating it to a vanilla 1.8 Paper backend would discard the modpack's server-side requirements.

## Deeper source-map inventory from the supplied 318 MiB ZIP

A second pass inspected `javascript_web/classes.js.map` in the user-provided archive. The map lists 13,726 source paths and contains no `sourcesContent` array, so it exposes class names but not recoverable original Java source text.

The inventory includes these concrete client-side layers:

### Minecraft 1.6-era packet classes

- `net/minecraft/network/packet/Packet.java`
- `Packet2ClientProtocol.java`
- `Packet250CustomPayload.java`
- `NetLoginHandler.java`
- `NetServerHandler.java`

### Forge Mod Loader handshake classes

- `cpw/mods/fml/common/network/FMLNetworkHandler.java`
- `FMLPacket.java`
- `NetworkRegistry.java`
- `ModListRequestPacket.java`
- `ModListResponsePacket.java`
- `ModIdentifiersPacket.java`
- `ModMissingPacket.java`
- `ModIdMapPacket.java`

### Forge custom network classes

- `net/minecraftforge/common/network/ForgeNetworkHandler.java`
- `ForgePacketHandler.java`
- `ForgePacket.java`
- `packet/DimensionRegisterPacket.java`

### Eagler browser transport classes

- `net/lax1dude/eaglercraft/socket/EaglerNetworkManagerClientWS.java`
- `socket/protocol/client/GameProtocolMessageController.java`
- `ClientV3MessageHandler.java`
- `ClientV4MessageHandler.java`

### Mod-specific packet class families

The map also contains packet/network class paths under Applied Energistics (`appeng/common/network/`), BuildCraft (`buildcraft/core/network/`, `buildcraft/transport/network/`), Galacticraft (`micdoodle8/mods/galacticraft/core/network/`), Aether (`net/aetherteam/aether/packets/`), Railcraft (`mods/railcraft/common/util/network/`), and Waila (`mcp/mobius/waila/network/`), among others.

This is strong evidence that the browser bundle includes the client-side implementations for a number of mod network handlers. It is **not** evidence that an EaglerXServer or a generic Forge server already supports those packets. A compatible backend must run matching server-side mods and honor their registration, packet direction, payload formats, and world state.

## EaglerXServer extension-point constraints

Inspection of the fork's actual rewind API shows:

- `IEaglerXRewindProtocol` registers handlers by a one-byte legacy Eagler protocol ID.
- `IEaglerXRewindInitializer` can rewrite the initial Eagler handshake and inject Netty handlers.
- The rewind message controller operates on Eagler game-message packets, not an arbitrary raw TCP socket.
- The existing `rewind_v1_5` implementation rewrites its client to Eagler protocol 5 / Minecraft protocol 47 and performs the EaglerXRewind login exchange.

Consequently, the existing extension point is useful for Eagler-side protocol negotiation and packet translation, but it is not by itself a generic Forge TCP proxy. A real Ultimate implementation must explicitly bridge the Eagler WebSocket message framing to the 1.6.4 backend's packet framing, and preserve FML/custom-payload traffic end-to-end.

## Next capture needed before writing a packet codec

Static inspection cannot establish the exact runtime wire behavior. The next decisive artifact is a packet trace from this exact browser build connecting to a controlled test endpoint (or a local server harness) that records the initial Eagler handshake, Minecraft protocol selection, custom-payload registration, FML handshake sequence, and disconnect reason. Do not guess packet IDs or strip unknown payloads.
