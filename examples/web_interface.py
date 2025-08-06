#!/usr/bin/env python3
"""Example of running the Bystronic OPC web interface."""

import asyncio
import logging
from threading import Thread

from bystronic_opc.web import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run the web interface example."""
    
    # Machine configuration
    machines = {
        "Line_A_Machine_1": "opc.tcp://192.168.100.101:56000",
        "Line_A_Machine_2": "opc.tcp://192.168.100.102:56000", 
        "Line_B_Machine_1": "opc.tcp://192.168.101.101:56000",
    }
    
    # Application configuration
    config = {
        'SECRET_KEY': 'your-secret-key-change-in-production',
        'MACHINES': machines,
        'DEBUG': True,  # Set to False in production
        'HOST': '0.0.0.0',
        'PORT': 5000,
    }
    
    logger.info("Creating Bystronic OPC web application...")
    
    # Create Flask app
    app = create_app(config)
    
    logger.info(f"Configured {len(machines)} machines:")
    for name, url in machines.items():
        logger.info(f"  - {name}: {url}")
    
    # Start monitoring in background thread
    def start_monitoring():
        """Start machine monitoring in background."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(app.monitor.start_monitoring())
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
    
    monitor_thread = Thread(target=start_monitoring, daemon=True)
    monitor_thread.start()
    
    logger.info("Starting web server...")
    logger.info(f"Dashboard will be available at: http://localhost:{config['PORT']}")
    logger.info("Press Ctrl+C to stop the server")
    
    try:
        # Run the Flask-SocketIO app
        app.socketio.run(
            app,
            host=config['HOST'],
            port=config['PORT'],
            debug=config['DEBUG'],
            use_reloader=False  # Disable reloader when using threads
        )
    except KeyboardInterrupt:
        logger.info("Shutting down web server...")
    
    # Stop monitoring
    logger.info("Stopping machine monitoring...")
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(app.monitor.stop_monitoring())
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
    
    logger.info("Web interface stopped")


if __name__ == '__main__':
    main()