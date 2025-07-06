# Universal API Keep-Alive Service

A Flask-based web application that provides a flexible keep-alive service for maintaining API uptime on hosting platforms like Render, Heroku, or any cloud service. Configure any API endpoint with custom request structures directly from the web dashboard.

## Features

- **Web Dashboard**: Real-time monitoring interface with Bootstrap 5 dark theme
- **Flexible Configuration**: Frontend interface to customize request structure without editing files
- **Multiple HTTP Methods**: Support for GET, POST, PUT, PATCH, DELETE requests
- **Custom Headers & Payloads**: JSON, form data, or no payload options
- **Quick Templates**: One-click configuration for common API patterns
- **Keep-Alive Service**: Automatic background pinging to maintain API uptime
- **Manual Controls**: Start/stop service and trigger manual pings
- **Comprehensive Logging**: File-based rotating logs with console output
- **Status Monitoring**: Real-time statistics and ping history
- **Production Ready**: Gunicorn server with process management

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd resume-api-keep-alive
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

4. **Access the dashboard**
   Open your browser to `http://localhost:5000`

## Configuration

The service can be configured via environment variables:

- `TARGET_URL`: API endpoint to ping (default: resume evaluation API)
- `PING_INTERVAL`: Time between pings in seconds (minimum: 60)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Custom Request Structure

You can customize the ping request to match your API requirements by modifying the `config.py` file:

```python
# Example configurations for different APIs:

# For JSON APIs:
DEFAULT_CONFIG = {
    "target_url": "https://your-api.com/endpoint",
    "ping_interval": 180,
    "request_method": "POST",
    "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer your-token"
    },
    "payload": {
        "ping": True,
        "timestamp": "auto"
    }
}

# For simple GET requests:
SIMPLE_GET_CONFIG = {
    "target_url": "https://your-api.com/health",
    "request_method": "GET",
    "headers": {"User-Agent": "KeepAlive-Service"}
}

# For form data APIs:
FORM_DATA_CONFIG = {
    "target_url": "https://your-api.com/ping",
    "request_method": "POST",
    "headers": {"Content-Type": "application/x-www-form-urlencoded"},
    "payload": "status=alive&source=keepalive"
}
```

**Environment Variable Override:**
Set `CUSTOM_PAYLOAD` to override the default request structure:
```bash
export CUSTOM_PAYLOAD='{"your": "custom", "data": "here"}'
export CUSTOM_HEADERS='{"Authorization": "Bearer your-token"}'
```

## Project Structure

```
├── main.py                 # Flask web application
├── keep_alive_service.py   # Core keep-alive service class
├── keep_alive.py          # Standalone keep-alive script
├── config.py              # Configuration management
├── run_services.py        # Dual-service process manager
├── templates/
│   └── index.html         # Web dashboard interface
└── static/
    └── style.css          # Custom styling
```

## API Endpoints

- `GET /` - Web dashboard
- `POST /ping` - Manual ping trigger
- `POST /start` - Start keep-alive service
- `POST /stop` - Stop keep-alive service
- `POST /config` - Update configuration
- `GET /status` - Service status (JSON)

## Deployment

### Render
1. Connect your GitHub repository to Render
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `gunicorn --bind 0.0.0.0:$PORT main:app`

### Replit
1. Import from GitHub in Replit
2. Run with the pre-configured workflow

## Security

This application has been security reviewed and contains no exploitable vulnerabilities. All subprocess calls use static commands with no external input.

## License

 License - see LICENSE file for details
