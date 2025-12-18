"""
Warehouse Management System - Flask Web Interface (Simplified Version)
Provides API endpoints for warehouse generation and layout management
Advanced training features available via separate training script
"""

import time
import os
import json
import numpy as np
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

# Import warehouse generation
from warehouseGenerator import make_map, sample_tasks, visualize_map

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configuration
WAREHOUSE_SAVE_DIR = "saved_warehouses"
MODEL_SAVE_DIR = "models"
TRAINING_RESULTS_DIR = "training_results"

# Ensure directories exist
for directory in [WAREHOUSE_SAVE_DIR, MODEL_SAVE_DIR, TRAINING_RESULTS_DIR]:
    os.makedirs(directory, exist_ok=True)

@app.route('/api/time')
def get_current_time():
    return {'time': time.time()}

@app.route('/api/warehouse/generate', methods=['POST'])
def generate_warehouse():
    """
    Generate a new warehouse layout based on configuration
    """
    try:
        config = request.get_json() or {}
        
        # Default configuration
        default_config = {
            'w': 16,
            'h': 12,
            'style': 'parallel',
            'obstacle_prob': 0.03,
            'min_aisle': 2,
            'max_aisle': 3
        }
        
        # Merge with user config
        warehouse_config = {**default_config, **config}
        
        # Validate inputs
        warehouse_config['w'] = max(6, min(30, warehouse_config['w']))
        warehouse_config['h'] = max(6, min(30, warehouse_config['h']))
        warehouse_config['obstacle_prob'] = max(0.0, min(0.1, warehouse_config['obstacle_prob']))
        
        # Generate warehouse
        warehouse, meta = make_map(**warehouse_config)
        
        # Generate sample tasks
        tasks = sample_tasks(warehouse, num_tasks=5)
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(12, 8))
        visualize_map(warehouse, ax=ax, title="Generated Warehouse Layout")
        
        # Convert plot to base64 image
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return jsonify({
            'success': True,
            'warehouse': warehouse.tolist(),
            'meta': meta,
            'tasks': tasks,
            'config': warehouse_config,
            'image': img_base64,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/warehouse/save', methods=['POST'])
def save_warehouse():
    """
    Save a warehouse layout to disk
    """
    try:
        data = request.get_json()
        warehouse_name = data.get('name', f"warehouse_{int(time.time())}")
        warehouse_data = data.get('warehouse')
        meta_data = data.get('meta', {})
        config_data = data.get('config', {})
        
        if not warehouse_data:
            return jsonify({'success': False, 'error': 'No warehouse data provided'}), 400
        
        # Sanitize warehouse name
        warehouse_name = "".join(c for c in warehouse_name if c.isalnum() or c in (' ', '-', '_')).strip()
        if not warehouse_name:
            warehouse_name = f"warehouse_{int(time.time())}"
        
        # Save warehouse data
        save_data = {
            'warehouse': warehouse_data,
            'meta': meta_data,
            'config': config_data,
            'timestamp': datetime.now().isoformat(),
            'name': warehouse_name
        }
        
        filepath = os.path.join(WAREHOUSE_SAVE_DIR, f"{warehouse_name}.json")
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'Warehouse saved as {warehouse_name}',
            'filepath': filepath
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/warehouse/load/<warehouse_name>')
def load_warehouse(warehouse_name):
    """
    Load a saved warehouse layout
    """
    try:
        filepath = os.path.join(WAREHOUSE_SAVE_DIR, f"{warehouse_name}.json")
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'Warehouse not found'}), 404
        
        with open(filepath, 'r') as f:
            warehouse_data = json.load(f)
        
        # Regenerate visualization
        warehouse = np.array(warehouse_data['warehouse'])
        fig, ax = plt.subplots(figsize=(12, 8))
        visualize_map(warehouse, ax=ax, title=f"Warehouse: {warehouse_name}")
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        warehouse_data['image'] = img_base64
        
        return jsonify({
            'success': True,
            'data': warehouse_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/warehouse/list')
def list_warehouses():
    """
    List all saved warehouses
    """
    try:
        warehouses = []
        
        if os.path.exists(WAREHOUSE_SAVE_DIR):
            for filename in os.listdir(WAREHOUSE_SAVE_DIR):
                if filename.endswith('.json'):
                    name = filename[:-5]  # Remove .json extension
                    filepath = os.path.join(WAREHOUSE_SAVE_DIR, filename)
                    
                    try:
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                        
                        warehouses.append({
                            'name': name,
                            'timestamp': data.get('timestamp', 'Unknown'),
                            'config': data.get('config', {}),
                            'meta': data.get('meta', {}),
                            'size': f"{data.get('config', {}).get('w', '?')}x{data.get('config', {}).get('h', '?')}"
                        })
                    except:
                        continue  # Skip corrupted files
        
        # Sort by timestamp (newest first)
        warehouses.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'success': True,
            'warehouses': warehouses
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/warehouse/delete/<warehouse_name>', methods=['DELETE'])
def delete_warehouse(warehouse_name):
    """
    Delete a saved warehouse
    """
    try:
        filepath = os.path.join(WAREHOUSE_SAVE_DIR, f"{warehouse_name}.json")
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'Warehouse not found'}), 404
        
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': f'Warehouse {warehouse_name} deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/warehouse/analyze', methods=['POST'])
def analyze_warehouse():
    """
    Analyze warehouse layout for metrics and statistics
    """
    try:
        data = request.get_json()
        warehouse_data = data.get('warehouse')
        
        if not warehouse_data:
            return jsonify({'success': False, 'error': 'No warehouse data provided'}), 400
        
        warehouse = np.array(warehouse_data)
        h, w = warehouse.shape
        
        # Calculate metrics
        total_cells = h * w
        free_cells = np.sum(warehouse == 0)
        shelf_cells = np.sum(warehouse == 1)
        drop_cells = np.sum(warehouse == 2)
        pickup_cells = np.sum(warehouse == 3)
        obstacle_cells = np.sum(warehouse == 4)
        
        # Calculate efficiency metrics
        usable_space = free_cells + drop_cells + pickup_cells
        storage_efficiency = shelf_cells / total_cells if total_cells > 0 else 0
        accessibility = usable_space / total_cells if total_cells > 0 else 0
        
        # Generate sample tasks to estimate complexity
        tasks = sample_tasks(warehouse, num_tasks=10)
        avg_distance = 0
        if tasks:
            distances = []
            for task in tasks:
                dist = abs(task['pickup_x'] - task['drop_x']) + abs(task['pickup_y'] - task['drop_y'])
                distances.append(dist)
            avg_distance = np.mean(distances) if distances else 0
        
        # Calculate warehouse efficiency score
        efficiency_score = (storage_efficiency * 0.4 + accessibility * 0.4 + 
                           (1 - min(avg_distance / max(w, h), 1)) * 0.2) * 100
        
        analysis = {
            'dimensions': {'width': w, 'height': h, 'total_cells': total_cells},
            'cell_counts': {
                'free': int(free_cells),
                'shelves': int(shelf_cells),
                'drop_zones': int(drop_cells),
                'pickup_zones': int(pickup_cells),
                'obstacles': int(obstacle_cells)
            },
            'percentages': {
                'free': float(free_cells / total_cells * 100) if total_cells > 0 else 0,
                'shelves': float(shelf_cells / total_cells * 100) if total_cells > 0 else 0,
                'drop_zones': float(drop_cells / total_cells * 100) if total_cells > 0 else 0,
                'pickup_zones': float(pickup_cells / total_cells * 100) if total_cells > 0 else 0,
                'obstacles': float(obstacle_cells / total_cells * 100) if total_cells > 0 else 0
            },
            'efficiency_metrics': {
                'storage_efficiency': float(storage_efficiency),
                'accessibility': float(accessibility),
                'average_task_distance': float(avg_distance),
                'efficiency_score': float(efficiency_score)
            },
            'sample_tasks': len(tasks),
            'complexity_score': float((avg_distance / max(w, h)) * (1 - accessibility)) if max(w, h) > 0 else 0
        }
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/training/info')
def training_info():
    """
    Provide information about training capabilities and instructions
    """
    return jsonify({
        'success': True,
        'training_info': {
            'deep_learning_available': False,
            'reason': 'TensorFlow not installed or not available in current environment',
            'alternative': 'Use the standalone training script for advanced AI training',
            'instructions': {
                'step1': 'Install TensorFlow: pip install tensorflow',
                'step2': 'Run: python train_models.py --warehouses 3 --episodes 1000',
                'step3': 'Check results in training_results/ directory',
                'step4': 'Use beginner_training.py for simple reinforcement learning'
            },
            'available_scripts': [
                'train_models.py - Comprehensive training pipeline',
                'beginner_training.py - Simple Q-learning implementation',
                'focused_learning.py - Focused DQN learning',
                'test_system.py - System diagnostics'
            ]
        }
    })

@app.route('/api/training/results')
def training_results():
    """
    List available training results
    """
    try:
        results = []
        
        if os.path.exists(TRAINING_RESULTS_DIR):
            results_dir = os.path.join(TRAINING_RESULTS_DIR, 'results')
            if os.path.exists(results_dir):
                for filename in os.listdir(results_dir):
                    if filename.endswith('_results.json'):
                        try:
                            filepath = os.path.join(results_dir, filename)
                            with open(filepath, 'r') as f:
                                result_data = json.load(f)
                            
                            results.append({
                                'filename': filename,
                                'model_name': result_data.get('model_name', 'Unknown'),
                                'model_type': result_data.get('model_type', 'Unknown'),
                                'timestamp': result_data.get('timestamp', 'Unknown'),
                                'success_rate': result_data.get('final_success_rate', 0),
                                'episodes': result_data.get('episodes', 0)
                            })
                        except:
                            continue
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'success': True,
            'results': results,
            'total_results': len(results)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system/status')
def system_status():
    """
    Get system status and capabilities
    """
    return jsonify({
        'success': True,
        'status': {
            'warehouse_generation': True,
            'visualization': True,
            'save_load': True,
            'analysis': True,
            'deep_learning': False,
            'warehouse_save_dir': WAREHOUSE_SAVE_DIR,
            'training_results_dir': TRAINING_RESULTS_DIR,
            'saved_warehouses': len([f for f in os.listdir(WAREHOUSE_SAVE_DIR) if f.endswith('.json')]) if os.path.exists(WAREHOUSE_SAVE_DIR) else 0,
            'training_results': len([f for f in os.listdir(os.path.join(TRAINING_RESULTS_DIR, 'results')) if f.endswith('.json')]) if os.path.exists(os.path.join(TRAINING_RESULTS_DIR, 'results')) else 0,
            'timestamp': datetime.now().isoformat(),
            'python_environment': 'Conda',
            'available_features': [
                'Warehouse Generation',
                'Layout Visualization', 
                'Save/Load Layouts',
                'Warehouse Analysis',
                'Task Generation'
            ],
            'training_notes': 'Use train_models.py script for AI training. Install TensorFlow for deep learning features.'
        }
    })

@app.route('/api/warehouse/export/<warehouse_name>')
def export_warehouse(warehouse_name):
    """
    Export warehouse data for training scripts
    """
    try:
        filepath = os.path.join(WAREHOUSE_SAVE_DIR, f"{warehouse_name}.json")
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'Warehouse not found'}), 404
        
        with open(filepath, 'r') as f:
            warehouse_data = json.load(f)
        
        # Create training-ready format
        training_data = {
            'name': warehouse_name,
            'warehouse': warehouse_data['warehouse'],
            'config': warehouse_data['config'],
            'tasks': sample_tasks(np.array(warehouse_data['warehouse']), num_tasks=20),
            'export_timestamp': datetime.now().isoformat(),
            'ready_for_training': True
        }
        
        return jsonify({
            'success': True,
            'training_data': training_data,
            'instructions': 'Save this data and use with train_models.py --warehouse-file <filename>'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/')
def index():
    """
    Simple index page with API documentation
    """
    api_docs = """
    <html>
    <head><title>Warehouse Management System API</title></head>
    <body>
        <h1>Warehouse Management System API</h1>
        <h2>Available Endpoints:</h2>
        <ul>
            <li><strong>POST /api/warehouse/generate</strong> - Generate new warehouse layout</li>
            <li><strong>POST /api/warehouse/save</strong> - Save warehouse layout</li>
            <li><strong>GET /api/warehouse/load/&lt;name&gt;</strong> - Load saved warehouse</li>
            <li><strong>GET /api/warehouse/list</strong> - List all saved warehouses</li>
            <li><strong>DELETE /api/warehouse/delete/&lt;name&gt;</strong> - Delete warehouse</li>
            <li><strong>POST /api/warehouse/analyze</strong> - Analyze warehouse efficiency</li>
            <li><strong>GET /api/warehouse/export/&lt;name&gt;</strong> - Export for training</li>
            <li><strong>GET /api/training/info</strong> - Training system information</li>
            <li><strong>GET /api/training/results</strong> - List training results</li>
            <li><strong>GET /api/system/status</strong> - System status</li>
        </ul>
        <h2>Training:</h2>
        <p>For AI training, use the standalone scripts:</p>
        <ul>
            <li><code>python train_models.py</code> - Full training pipeline</li>
            <li><code>python test_system.py</code> - System diagnostics</li>
        </ul>
    </body>
    </html>
    """
    return api_docs

if __name__ == '__main__':
    print("Warehouse Management System - Web Interface")
    print("=" * 60)
    print(f"Warehouse Save Directory: {WAREHOUSE_SAVE_DIR}")
    print(f"Training Results Directory: {TRAINING_RESULTS_DIR}")
    print("Deep Learning: Use separate training scripts")
    print("=" * 60)
    print("Starting web server on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)