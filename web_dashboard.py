#!/usr/bin/env python3
"""
Web Dashboard for TMS Data Warehouse Synchronization
This application provides a web interface to monitor sync status
"""

from flask import Flask, render_template_string, jsonify, request
import logging
from datetime import datetime
from database_utils import DatabaseManager
from sync_manager import get_sync_status
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# HTML Template for the dashboard
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TMS Data Warehouse Sync Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .content {
            padding: 20px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .stat-card h3 {
            margin: 0 0 10px 0;
            color: #333;
        }
        .stat-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .controls {
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 10px;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            background: #5a6fd8;
        }
        .btn-danger {
            background: #dc3545;
        }
        .btn-danger:hover {
            background: #c82333;
        }
        .btn-success {
            background: #28a745;
        }
        .btn-success:hover {
            background: #218838;
        }
        .sync-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .sync-table th,
        .sync-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .sync-table th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        .sync-table tr:hover {
            background-color: #f5f5f5;
        }
        .status-success {
            color: #28a745;
            font-weight: bold;
        }
        .status-failed {
            color: #dc3545;
            font-weight: bold;
        }
        .status-running {
            color: #ffc107;
            font-weight: bold;
        }
        .refresh-info {
            text-align: center;
            color: #666;
            margin-top: 20px;
            font-size: 0.9em;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 TMS Data Warehouse</h1>
            <p>Synchronization Dashboard</p>
        </div>
        
        <div class="content">
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Sync Records</h3>
                    <div class="value" id="total-syncs">-</div>
                </div>
                <div class="stat-card">
                    <h3>Successful Syncs</h3>
                    <div class="value" id="successful-syncs">-</div>
                </div>
                <div class="stat-card">
                    <h3>Failed Syncs</h3>
                    <div class="value" id="failed-syncs">-</div>
                </div>
                <div class="stat-card">
                    <h3>Last Sync</h3>
                    <div class="value" id="last-sync">-</div>
                </div>
            </div>

            <div class="controls">
                <h3>Quick Actions</h3>
                <a href="/sync/both" class="btn btn-success">🔄 Sync Both Tables</a>
                <a href="/sync/fact_order" class="btn">📋 Sync Fact Order</a>
                <a href="/sync/fact_delivery" class="btn">🚚 Sync Fact Delivery</a>
                <a href="/status" class="btn">📊 Refresh Status</a>
                <a href="/status/fact_order" class="btn">📋 Order Status</a>
                <a href="/status/fact_delivery" class="btn">🚚 Delivery Status</a>
            </div>

            <div id="sync-history">
                <h3>📈 Recent Sync History</h3>
                <div class="loading">Loading sync history...</div>
            </div>

            <div class="refresh-info">
                Auto-refresh every 30 seconds | Last updated: <span id="last-updated">-</span>
            </div>
        </div>
    </div>

    <script>
        function updateDashboard() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-syncs').textContent = data.stats.total_syncs;
                    document.getElementById('successful-syncs').textContent = data.stats.successful_syncs;
                    document.getElementById('failed-syncs').textContent = data.stats.failed_syncs;
                    document.getElementById('last-sync').textContent = data.stats.last_sync;
                    document.getElementById('last-updated').textContent = new Date().toLocaleString();
                    
                    // Update sync history table
                    const historyHtml = generateHistoryTable(data.sync_history);
                    document.getElementById('sync-history').innerHTML = historyHtml;
                })
                .catch(error => {
                    console.error('Error fetching status:', error);
                    document.getElementById('sync-history').innerHTML = 
                        '<div class="error">Error loading sync history. Please try again.</div>';
                });
        }

        function generateHistoryTable(syncHistory) {
            if (!syncHistory || syncHistory.length === 0) {
                return '<h3>📈 Recent Sync History</h3><p>No sync history found.</p>';
            }

            let html = `
                <h3>📈 Recent Sync History</h3>
                <table class="sync-table">
                    <thead>
                        <tr>
                            <th>Sync Type</th>
                            <th>Start Time</th>
                            <th>End Time</th>
                            <th>Status</th>
                            <th>Records</th>
                            <th>Error</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            syncHistory.forEach(sync => {
                const statusClass = sync.status === 'SUCCESS' ? 'status-success' : 
                                  sync.status === 'FAILED' ? 'status-failed' : 'status-running';
                
                html += `
                    <tr>
                        <td>${sync.sync_type}</td>
                        <td>${sync.start_time || 'N/A'}</td>
                        <td>${sync.end_time || 'N/A'}</td>
                        <td class="${statusClass}">${sync.status}</td>
                        <td>${sync.records_processed || 0}</td>
                        <td>${sync.error_message ? sync.error_message.substring(0, 50) + '...' : '-'}</td>
                    </tr>
                `;
            });

            html += '</tbody></table>';
            return html;
        }

        // Auto-refresh every 30 seconds
        setInterval(updateDashboard, 30000);
        
        // Initial load
        updateDashboard();
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def api_status():
    """API endpoint to get sync status"""
    try:
        db_manager = DatabaseManager()
        sync_history = get_sync_status(db_manager, limit=20)
        
        # Calculate statistics
        total_syncs = len(sync_history)
        successful_syncs = len([s for s in sync_history if s[3] == 'SUCCESS'])
        failed_syncs = len([s for s in sync_history if s[3] == 'FAILED'])
        
        # Get last sync time
        last_sync = 'Never'
        if sync_history:
            last_sync_time = sync_history[0][1]  # start_time of most recent sync
            if last_sync_time:
                last_sync = last_sync_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Format sync history for JSON
        formatted_history = []
        for sync in sync_history:
            formatted_history.append({
                'sync_type': sync[0],
                'start_time': sync[1].strftime('%Y-%m-%d %H:%M:%S') if sync[1] else None,
                'end_time': sync[2].strftime('%Y-%m-%d %H:%M:%S') if sync[2] else None,
                'status': sync[3],
                'records_processed': sync[4],
                'error_message': sync[5]
            })
        
        return jsonify({
            'stats': {
                'total_syncs': total_syncs,
                'successful_syncs': successful_syncs,
                'failed_syncs': failed_syncs,
                'last_sync': last_sync
            },
            'sync_history': formatted_history
        })
        
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/sync/<sync_type>')
def run_sync(sync_type):
    """Run synchronization"""
    try:
        from sync_manager import run_sync
        logger.info(f"Starting {sync_type} sync from web dashboard...")
        run_sync(sync_type)
        return jsonify({'status': 'success', 'message': f'{sync_type} sync completed successfully'})
    except Exception as e:
        logger.error(f"Error running {sync_type} sync: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/status')
def status_page():
    """Status page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/status/<sync_type>')
def status_type_page(sync_type):
    """Status page for specific sync type"""
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.getenv('WEB_PORT', 5000))
    host = os.getenv('WEB_HOST', '0.0.0.0')
    
    print(f"🚀 Starting TMS Data Warehouse Web Dashboard...")
    print(f"📊 Dashboard will be available at: http://{host}:{port}")
    print(f"🔄 Auto-refresh every 30 seconds")
    print(f"⏹️  Press Ctrl+C to stop")
    
    app.run(host=host, port=port, debug=False) 