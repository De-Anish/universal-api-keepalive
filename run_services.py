#!/usr/bin/env python3
"""
Entry point script to run both the web dashboard and the standalone keep-alive service.
This script ensures maximum uptime by running both components.
"""

import os
import sys
import subprocess
import time
import logging
import signal
import atexit

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("services.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("run_services")

# Process tracking
web_app_process = None
keep_alive_process = None

def start_web_app():
    """Start the Flask web application with Gunicorn"""
    global web_app_process
    
    cmd = ["gunicorn", "--bind", "0.0.0.0:5000", "--reuse-port", "main:app"]
    logger.info(f"Starting web app: {' '.join(cmd)}")
    
    try:
        web_app_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        logger.info(f"Web app started with PID: {web_app_process.pid}")
        return True
    except Exception as e:
        logger.error(f"Failed to start web app: {e}")
        return False

def start_keep_alive():
    """Start the standalone keep-alive service"""
    global keep_alive_process
    
    cmd = ["python3", "keep_alive.py"]
    logger.info(f"Starting keep-alive service: {' '.join(cmd)}")
    
    try:
        keep_alive_process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        logger.info(f"Keep-alive service started with PID: {keep_alive_process.pid}")
        return True
    except Exception as e:
        logger.error(f"Failed to start keep-alive service: {e}")
        return False

def cleanup():
    """Clean up processes on exit"""
    logger.info("Cleaning up processes...")
    
    if web_app_process:
        logger.info(f"Terminating web app process (PID: {web_app_process.pid})")
        try:
            web_app_process.terminate()
            web_app_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("Web app process did not terminate gracefully, forcing kill")
            web_app_process.kill()
    
    if keep_alive_process:
        logger.info(f"Terminating keep-alive process (PID: {keep_alive_process.pid})")
        try:
            keep_alive_process.terminate()
            keep_alive_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning("Keep-alive process did not terminate gracefully, forcing kill")
            keep_alive_process.kill()
    
    logger.info("Cleanup complete")

def signal_handler(sig, frame):
    """Handle termination signals"""
    logger.info(f"Received signal {sig}, shutting down...")
    cleanup()
    sys.exit(0)

def monitor_processes():
    """Monitor child processes and restart them if they fail"""
    global web_app_process, keep_alive_process
    
    while True:
        # Check web app process
        if web_app_process and web_app_process.poll() is not None:
            logger.warning(f"Web app process terminated with code {web_app_process.returncode}, restarting...")
            start_web_app()
        
        # Check keep-alive process
        if keep_alive_process and keep_alive_process.poll() is not None:
            logger.warning(f"Keep-alive process terminated with code {keep_alive_process.returncode}, restarting...")
            start_keep_alive()
        
        # Check process output for logging
        for proc, name in [(web_app_process, "web_app"), (keep_alive_process, "keep_alive")]:
            if proc:
                try:
                    # Non-blocking read from process output
                    for line in proc.stdout:
                        if line:
                            logger.info(f"[{name}] {line.strip()}")
                except Exception:
                    pass
        
        # Sleep to avoid high CPU usage
        time.sleep(5)

if __name__ == "__main__":
    # Register cleanup and signal handlers
    atexit.register(cleanup)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("Starting services manager...")
    
    # Start both components
    web_app_started = start_web_app()
    keep_alive_started = start_keep_alive()
    
    if not web_app_started and not keep_alive_started:
        logger.error("Failed to start both components, exiting")
        sys.exit(1)
    
    # Monitor and restart processes if needed
    try:
        monitor_processes()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
    finally:
        cleanup()