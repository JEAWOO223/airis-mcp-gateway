# Troubleshooting

## Check Status

```bash
docker compose ps
docker compose logs --tail 50 api
curl http://localhost:9400/metrics
```

## Verify Installation

```bash
# Check health
curl http://localhost:9400/health

# List all tools
curl http://localhost:9400/api/tools/combined | jq '.tools_count'

# Check server status
curl http://localhost:9400/api/tools/status | jq '.servers[] | {name, status}'
```

## Reset

```bash
docker compose down -v
docker compose up -d
```

## Process Server Issues

```bash
# Check specific server status
curl http://localhost:9400/process/servers/memory | jq

# View server logs
docker compose logs api | grep -i memory
```

## Common Issues

### "Server not found"

```bash
# Check mcp-config.json
cat mcp-config.json | jq '.mcpServers | keys'

# Restart after config changes
docker compose restart api
```

### "Connection timeout"

```bash
# Check gateway connectivity
docker compose logs gateway

# Verify internal network
docker compose exec api curl -v http://gateway:9390/health
```

### "Rate limit exceeded"

```bash
# Check current limits
curl http://localhost:9400/metrics | grep rate

# Increase limits (see DEPLOYMENT.md for details)
export RATE_LIMIT_PER_IP=200
docker compose up -d
```
