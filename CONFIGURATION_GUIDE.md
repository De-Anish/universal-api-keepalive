# Configuration Guide

This guide shows you how to customize the keep-alive service for different API structures and requirements.

## Quick Setup for Your API

### Option 1: Environment Variables (Recommended)
Set these environment variables to customize your request:

```bash
# Basic configuration
export TARGET_URL="https://your-api.com/endpoint"
export REQUEST_METHOD="POST"  # GET, POST, PUT, DELETE, etc.
export PING_INTERVAL="300"   # Seconds between pings (minimum 60)

# Custom headers
export CUSTOM_HEADERS='{"Authorization": "Bearer your-token", "Content-Type": "application/json"}'

# Custom payload
export CUSTOM_PAYLOAD='{"ping": true, "service": "keepalive", "timestamp": "auto"}'
```

### Option 2: Modify config.py
Edit the `DEFAULT_CONFIG` in `config.py` to match your API:

```python
DEFAULT_CONFIG = {
    "url": "https://your-api.com/endpoint",
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
    "data": {"your": "custom", "payload": "here"},
    "interval": 180
}
```

## Common API Patterns

### 1. Simple Health Check (GET)
```bash
export TARGET_URL="https://your-api.com/health"
export REQUEST_METHOD="GET"
export CUSTOM_HEADERS='{"User-Agent": "KeepAlive-Service"}'
export CUSTOM_PAYLOAD='null'  # No payload for GET requests
```

### 2. JSON API with Authentication
```bash
export TARGET_URL="https://your-api.com/api/ping"
export REQUEST_METHOD="POST"
export CUSTOM_HEADERS='{"Content-Type": "application/json", "Authorization": "Bearer YOUR_TOKEN"}'
export CUSTOM_PAYLOAD='{"action": "ping", "timestamp": "auto"}'
```

### 3. Form Data Submission
```bash
export TARGET_URL="https://your-api.com/keep-alive"
export REQUEST_METHOD="POST"
export CUSTOM_HEADERS='{"Content-Type": "application/x-www-form-urlencoded"}'
export CUSTOM_PAYLOAD="status=alive&source=keepalive&timestamp=auto"
```

### 4. REST API with Custom Headers
```bash
export TARGET_URL="https://api.example.com/v1/heartbeat"
export REQUEST_METHOD="PUT"
export CUSTOM_HEADERS='{"Content-Type": "application/json", "X-API-Key": "your-key", "X-Client-Version": "1.0"}'
export CUSTOM_PAYLOAD='{"heartbeat": true, "client": "keepalive-service"}'
```

### 5. GraphQL API
```bash
export TARGET_URL="https://your-api.com/graphql"
export REQUEST_METHOD="POST"
export CUSTOM_HEADERS='{"Content-Type": "application/json"}'
export CUSTOM_PAYLOAD='{"query": "mutation { ping { success } }"}'
```

## Advanced Configuration

### Using Different Config Templates
You can use the predefined templates in `config.py`:

```python
from config import EXAMPLE_CONFIGS

# Use a template
config = EXAMPLE_CONFIGS["simple_get"]
config["url"] = "https://your-api.com/health"
```

### Dynamic Timestamps
Use `"auto"` in your payload to automatically insert current timestamp:

```json
{
  "ping": true,
  "timestamp": "auto"  // Will be replaced with current Unix timestamp
}
```

### Multiple Headers
Combine default and custom headers:

```bash
export CUSTOM_HEADERS='{"Authorization": "Bearer token", "X-Custom": "value"}'
```

This will merge with default headers like `Content-Type`.

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `TARGET_URL` | API endpoint to ping | `https://api.example.com/ping` |
| `REQUEST_METHOD` | HTTP method | `GET`, `POST`, `PUT`, `DELETE` |
| `PING_INTERVAL` | Seconds between pings (min 60) | `180` |
| `CUSTOM_HEADERS` | JSON object with headers | `{"Auth": "token"}` |
| `CUSTOM_PAYLOAD` | Request body (JSON or string) | `{"ping": true}` |
| `LOG_LEVEL` | Logging level | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `MAX_HISTORY` | Max ping history entries | `100` |

## Testing Your Configuration

1. Start the service: `python main.py`
2. Check logs for successful pings
3. Use the web dashboard at `http://localhost:5000`
4. Monitor the "Ping History" section for results

## Troubleshooting

### Common Issues:

**Invalid JSON in environment variables:**
- Ensure proper JSON formatting in `CUSTOM_HEADERS` and `CUSTOM_PAYLOAD`
- Use single quotes around the JSON string in bash

**Authentication failures:**
- Verify your API tokens/keys are correct
- Check if tokens need refresh or have expiration

**Rate limiting:**
- Increase `PING_INTERVAL` if you're hitting rate limits
- Check API documentation for recommended ping frequencies

**Request format issues:**
- Verify the `Content-Type` header matches your payload format
- Check API documentation for required fields

### Debug Mode:
```bash
export LOG_LEVEL="DEBUG"
```
This will show detailed request/response information in the logs.