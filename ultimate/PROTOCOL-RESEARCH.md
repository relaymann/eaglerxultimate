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
