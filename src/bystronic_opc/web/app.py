"""Flask application factory for Bystronic OPC web interface."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
from uuid import UUID

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_socketio import SocketIO, emit
import asyncio
from threading import Thread

from ..client import BystronicClient
from ..monitor import MachineMonitor
from ..exceptions import ConnectionError, DataError


def create_app(config: Optional[Dict] = None) -> Flask:
    """Create Flask application with configuration.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev-key-change-in-production',
        MACHINES={
            "Machine_1": "opc.tcp://192.168.100.101:56000",
            "Machine_2": "opc.tcp://192.168.100.102:56000", 
            "Machine_3": "opc.tcp://192.168.101.101:56000",
        }
    )
    
    if config:
        app.config.update(config)
    
    # Initialize SocketIO for real-time updates
    socketio = SocketIO(app, cors_allowed_origins="*")
    app.socketio = socketio
    
    # Initialize machine monitor
    monitor = MachineMonitor(
        machines=app.config['MACHINES'],
        update_interval=30
    )
    app.monitor = monitor
    
    # Register routes
    register_routes(app)
    register_api_routes(app) 
    register_socketio_events(socketio, monitor)
    
    return app


def register_routes(app: Flask) -> None:
    """Register main web routes."""
    
    @app.route('/')
    def index():
        """Main dashboard page."""
        machines = app.config['MACHINES']
        machine_status = {}
        
        # Get current status of all machines
        if hasattr(app, 'monitor'):
            machine_status = app.monitor.get_all_machine_status()
        
        return render_template('dashboard.html', 
                             machines=machines,
                             machine_status=machine_status)
    
    @app.route('/machine/<machine_name>')
    def machine_detail(machine_name):
        """Detailed machine view."""
        if machine_name not in app.config['MACHINES']:
            flash(f'Machine {machine_name} not found', 'error')
            return redirect(url_for('index'))
        
        machine_url = app.config['MACHINES'][machine_name]
        status = None
        
        if hasattr(app, 'monitor'):
            status = app.monitor.get_machine_status(machine_name)
        
        return render_template('machine_detail.html',
                             machine_name=machine_name,
                             machine_url=machine_url,
                             status=status)
    
    @app.route('/history')
    def history():
        """Historical data view."""
        return render_template('history.html',
                             machines=app.config['MACHINES'])
    
    @app.route('/settings')
    def settings():
        """Settings and configuration page."""
        return render_template('settings.html',
                             machines=app.config['MACHINES'])


def register_api_routes(app: Flask) -> None:
    """Register API routes for AJAX calls."""
    
    @app.route('/api/machine/<machine_name>/status')
    def api_machine_status(machine_name):
        """Get machine status via API."""
        if machine_name not in app.config['MACHINES']:
            return jsonify({'error': 'Machine not found'}), 404
        
        status = None
        if hasattr(app, 'monitor'):
            status = app.monitor.get_machine_status(machine_name)
        
        if status:
            return jsonify({
                'machine_name': machine_name,
                'is_connected': status.is_connected,
                'current_job': {
                    'name': status.current_job.name if status.current_job else None,
                    'guid': str(status.current_job.guid) if status.current_job else None
                } if status.current_job else None,
                'laser_parameters': {
                    'current_power': status.laser_parameters.current_laser_power if status.laser_parameters else 0,
                    'gas_pressure': status.laser_parameters.gas_pressure if status.laser_parameters else 0,
                    'operation_mode': status.laser_parameters.process_operation_mode if status.laser_parameters else 0
                } if status.laser_parameters else None,
                'last_update': status.last_update.isoformat() if status.last_update else None,
                'error_message': status.error_message
            })
        
        return jsonify({'error': 'Status not available'}), 503
    
    @app.route('/api/machines/status')
    def api_all_machines_status():
        """Get status of all machines."""
        if not hasattr(app, 'monitor'):
            return jsonify({'error': 'Monitor not available'}), 503
        
        all_status = app.monitor.get_all_machine_status()
        result = {}
        
        for machine_name, status in all_status.items():
            result[machine_name] = {
                'is_connected': status.is_connected,
                'current_job': status.current_job.name if status.current_job else None,
                'last_update': status.last_update.isoformat() if status.last_update else None,
                'error_message': status.error_message
            }
        
        return jsonify(result)
    
    @app.route('/api/machine/<machine_name>/history')
    def api_machine_history(machine_name):
        """Get machine history via API."""
        if machine_name not in app.config['MACHINES']:
            return jsonify({'error': 'Machine not found'}), 404
        
        # Get query parameters
        days = request.args.get('days', 7, type=int)
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 50, type=int)
        
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        try:
            # Get machine client and fetch history
            machine_url = app.config['MACHINES'][machine_name]
            
            async def fetch_history():
                async with BystronicClient(machine_url) as client:
                    return await client.get_run_history(start_time, end_time, page, page_size)
            
            # Run async function in thread (simplified for demo)
            # In production, consider using proper async handling
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            history = loop.run_until_complete(fetch_history())
            loop.close()
            
            return jsonify({
                'machine_name': machine_name,
                'history': history,
                'query': {
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'page': page,
                    'page_size': page_size
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/machine/<machine_name>/screen')
    def api_machine_screen(machine_name):
        """Get machine screen image."""
        if machine_name not in app.config['MACHINES']:
            return jsonify({'error': 'Machine not found'}), 404
        
        try:
            machine_url = app.config['MACHINES'][machine_name]
            
            async def get_screen():
                async with BystronicClient(machine_url) as client:
                    return await client.get_screen_image()
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            image_data = loop.run_until_complete(get_screen())
            loop.close()
            
            # Return image directly
            from flask import Response
            return Response(image_data, mimetype='image/png')
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500


def register_socketio_events(socketio: SocketIO, monitor: MachineMonitor) -> None:
    """Register WebSocket events for real-time updates."""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        print('Client connected')
        emit('status', {'message': 'Connected to Bystronic OPC server'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        print('Client disconnected')
    
    @socketio.on('subscribe_machine')
    def handle_subscribe_machine(data):
        """Subscribe to machine updates."""
        machine_name = data.get('machine_name')
        if machine_name:
            # Join room for this machine
            from flask_socketio import join_room
            join_room(f'machine_{machine_name}')
            emit('subscribed', {'machine_name': machine_name})
    
    def broadcast_updates():
        """Broadcast machine status updates to connected clients."""
        while True:
            try:
                if monitor:
                    all_status = monitor.get_all_machine_status()
                    
                    for machine_name, status in all_status.items():
                        data = {
                            'machine_name': machine_name,
                            'is_connected': status.is_connected,
                            'current_job': status.current_job.name if status.current_job else None,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        # Broadcast to all clients subscribed to this machine
                        socketio.emit('machine_update', data, room=f'machine_{machine_name}')
                    
                    # Broadcast summary to all clients
                    connected_count = len([s for s in all_status.values() if s.is_connected])
                    socketio.emit('summary_update', {
                        'total_machines': len(all_status),
                        'connected_machines': connected_count,
                        'timestamp': datetime.now().isoformat()
                    })
                
            except Exception as e:
                print(f"Error in broadcast_updates: {e}")
            
            import time
            time.sleep(10)  # Update every 10 seconds
    
    # Start background thread for updates
    update_thread = Thread(target=broadcast_updates)
    update_thread.daemon = True
    update_thread.start()


def main():
    """Main function to run the web application."""
    app = create_app()
    
    # Start monitoring in background
    import threading
    
    def start_monitoring():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(app.monitor.start_monitoring())
    
    monitor_thread = threading.Thread(target=start_monitoring)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Run the app
    app.socketio.run(app, host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    main()