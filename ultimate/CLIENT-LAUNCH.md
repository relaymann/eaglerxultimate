# Ultimate browser client launch configuration

This document records the launch behavior observed in the supplied `ultimate.zip`.

## WASM-GC JSPI build

File: `wasm_gc_jspi_web/index.html`

The page initializes `window.eaglercraftXOpts` with an empty `servers` array. It also reads the URL query parameter named `server`; when present, it assigns the value to `window.eaglercraftXOpts.joinServer` before calling `main()`.

The legacy WASM build has the same structure.

Once a working gateway URL exists, a test launch can therefore be made with:

```text
https://<your-client-site>/?server=wss://<your-gateway-host>/
```

This is only a client launch/configuration mechanism. It does not prove that the gateway speaks the required protocol.

## JavaScript web build

File: `javascript_web/index.html`

The JavaScript build currently has a placeholder server entry:

```javascript
{ addr: "ws://localhost:8081/", name: "Local test server" }
```

It also supports the `?server=` query parameter and assigns it to `joinServer`.

## Hosting requirements

- Serve the client over HTTPS.
- Use `wss://` for a public gateway from an HTTPS page; browsers block insecure mixed-content WebSocket connections.
- Configure the host/proxy to support WebSocket upgrades and long-lived connections.
- Do not publish a launch link until a real protocol handshake has passed.
- The WASM `servers: []` list is not evidence that multiplayer is disabled; the URL `joinServer` override is present in the supplied HTML.
