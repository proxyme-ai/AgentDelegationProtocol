#!/usr/bin/env python3
"""
Startup script for Agent Delegation Protocol servers.
Runs all servers (auth, resource, and API) in separate processes.
"""

import subprocess
import sys
import time
import signal
import os
from multiprocessing import Process
from config import config
from logging_config import get_logger

logger = get_logger('startup')

def run_auth_server():
    """Run the authorization server."""
    try:
        from auth_server import main
        main()
    except Exception as e:
        logger.error(f"Auth server failed: {str(e)}")

def run_resource_server():
    """Run the resource server."""
    try:
        from resource_server import main
        main()
    except Exception as e:
        logger.error(f"Resource server failed: {str(e)}")

def run_api_server():
    """Run the API server."""
    try:
        from api_server import main
        main()
    except Exception as e:
        logger.error(f"API server failed: {str(e)}")

def main():
    """Main startup function."""
    logger.info("Starting Agent Delegation Protocol servers...")
    
    # List of server processes
    processes = []
    
    try:
        # Start authorization server
        logger.info(f"Starting Authorization Server on {config.auth_server_host}:{config.auth_server_port}")
        auth_process = Process(target=run_auth_server, name="AuthServer")
        auth_process.start()
        processes.append(auth_process)
        
        # Wait a moment for auth server to start
        time.sleep(2)
        
        # Start resource server
        logger.info(f"Starting Resource Server on {config.resource_server_host}:{config.resource_server_port}")
        resource_process = Process(target=run_resource_server, name="ResourceServer")
        resource_process.start()
        processes.append(resource_process)
        
        # Wait a moment for resource server to start
        time.sleep(2)
        
        # Start API server
        logger.info(f"Starting API Server on 0.0.0.0:{config.frontend_port}")
        api_process = Process(target=run_api_server, name="APIServer")
        api_process.start()
        processes.append(api_process)
        
        logger.info("All servers started successfully!")
        logger.info("Server URLs:")
        logger.info(f"  - Authorization Server: {config.auth_server_url}")
        logger.info(f"  - Resource Server: {config.resource_server_url}")
        logger.info(f"  - API Server: http://localhost:{config.frontend_port}")
        logger.info("Press Ctrl+C to stop all servers")
        
        # Wait for all processes
        for process in processes:
            process.join()
            
    except KeyboardInterrupt:
        logger.info("Shutting down servers...")
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    process.kill()
        logger.info("All servers stopped")
    
    except Exception as e:
        logger.error(f"Error starting servers: {str(e)}")
        for process in processes:
            if process.is_alive():
                process.terminate()
        sys.exit(1)

if __name__ == '__main__':
    main()