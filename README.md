# MCP sse (http) client / server example

## Run:

- server:

```bash
$ FASTMCP_PORT=... python weather_server.py
$ KEYLIGHT_API_BASE=... python keylight_server.py
```

- client:

```bash
$ ANTHROPIC_API_KEY=... python client.py
```

### env vars

- FASTMCP_PORT - (int) port for fastmcp server
- KEYLIGHT_API_BASE - (url) keylight api base url
- ANTHROPIC_API_KEY - (hash) anthropic api key

## Important Links

- [Aentropic MCP Announcement](https://www.anthropic.com/news/model-context-protocol)
- [MCP Spec](https://modelcontextprotocol.io/)
- [MCP API](https://github.com/modelcontextprotocol)
- [MCP Servers Examples](https://github.com/modelcontextprotocol/servers)
- [For Server Developers](https://modelcontextprotocol.io/quickstart/server)
- [Vibing Server Development](https://modelcontextprotocol.io/tutorials/building-mcp-with-llms)
- [For Client Developers](https://modelcontextprotocol.io/quickstart/client)

