"""
Warehouse Management System - Flask Web Interface
Provides API endpoints for warehouse generation, DQN training, and layout management
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

# Import DQN components (we'll handle errors gracefully)
try:
    from deepQ.beginner_training import SimpleAI, WarehouseEnv
    DQN_AVAILABLE = True
except ImportError:
    print("Warning: DQN modules not available. Training features will be disabled.")
    DQN_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configuration
WAREHOUSE_SAVE_DIR = "saved_warehouses"
MODEL_SAVE_DIR = "models"

# Ensure directories exist
os.makedirs(WAREHOUSE_SAVE_DIR, exist_ok=True)
os.makedirs(MODEL_SAVE_DIR, exist_ok=True)

@app.route('/api/time')
def get_current_time():
    return {'time': time.time()}

@app.route('/api/warehouse/generate', methods=['POST'])
def generate_warehouse():
    """
    Generate a new warehouse layout based on configuration
    """
    try:
        config = request.get_json()
        
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
                        'meta': data.get('meta', {})
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

@app.route('/api/training/start', methods=['POST'])
def start_training():
    """
    Start DQN training on a warehouse layout
    """
    if not DQN_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'DQN training modules not available'
        }), 500
    
    try:
        data = request.get_json()
        warehouse_data = data.get('warehouse')
        training_config = data.get('config', {})
        
        if not warehouse_data:
            return jsonify({'success': False, 'error': 'No warehouse data provided'}), 400
        
        # Default training configuration
        default_training = {
            'episodes': 500,
            'learning_rate': 0.001,
            'epsilon_decay': 0.995,
            'save_interval': 100
        }
        
        # Merge configurations
        final_config = {**default_training, **training_config}
        
        # Convert warehouse data to numpy array
        warehouse = np.array(warehouse_data)
        
        # Initialize training environment
        env = WarehouseEnv(warehouse)
        agent = SimpleAI(
            learning_rate=final_config['learning_rate'],
            epsilon_decay=final_config['epsilon_decay']
        )
        
        # Start training (simplified version for web interface)
        training_results = run_quick_training(env, agent, final_config)
        
        return jsonify({
            'success': True,
            'results': training_results,
            'config': final_config
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def run_quick_training(env, agent, config):
    """
    Run a quick training session and return results
    """
    episodes = min(config['episodes'], 100)  # Limit for web interface
    scores = []
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        steps = 0
        max_steps = 200
        
        while steps < max_steps:
            action = agent.choose_action(state)
            next_state, reward, done = env.step(action)
            agent.learn(state, action, reward, next_state)
            
            state = next_state
            total_reward += reward
            steps += 1
            
            if done:
                break
        
        scores.append(total_reward)
    
    # Calculate metrics
    avg_score = np.mean(scores)
    final_scores = scores[-10:] if len(scores) >= 10 else scores
    final_avg = np.mean(final_scores)
    improvement = final_avg - np.mean(scores[:10]) if len(scores) >= 10 else 0
    
    return {
        'episodes_trained': episodes,
        'average_score': float(avg_score),
        'final_average': float(final_avg),
        'improvement': float(improvement),
        'all_scores': scores,
        'success_rate': len([s for s in final_scores if s > 50]) / len(final_scores) if final_scores else 0
    }

@app.route('/api/training/models')
def list_models():
    """
    List all saved DQN models
    """
    try:
        models = []
        
        if os.path.exists(MODEL_SAVE_DIR):
            for filename in os.listdir(MODEL_SAVE_DIR):
                if filename.endswith('.h5') and '_main.h5' in filename:
                    # Extract model name
                    model_name = filename.replace('_main.h5', '')
                    
                    # Check for corresponding files
                    param_file = os.path.join(MODEL_SAVE_DIR, f"{model_name}_params.json")
                    target_file = os.path.join(MODEL_SAVE_DIR, f"{model_name}_target.h5")
                    
                    model_info = {
                        'name': model_name,
                        'main_model': os.path.exists(os.path.join(MODEL_SAVE_DIR, filename)),
                        'target_model': os.path.exists(target_file),
                        'parameters': os.path.exists(param_file),
                        'timestamp': datetime.fromtimestamp(
                            os.path.getmtime(os.path.join(MODEL_SAVE_DIR, filename))
                        ).isoformat()
                    }
                    
                    # Load parameters if available
                    if os.path.exists(param_file):
                        try:
                            with open(param_file, 'r') as f:
                                params = json.load(f)
                            model_info['config'] = params
                        except:
                            pass
                    
                    models.append(model_info)
        
        # Sort by timestamp (newest first)
        models.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'success': True,
            'models': models
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
            'dqn_available': DQN_AVAILABLE,
            'warehouse_save_dir': WAREHOUSE_SAVE_DIR,
            'model_save_dir': MODEL_SAVE_DIR,
            'saved_warehouses': len([f for f in os.listdir(WAREHOUSE_SAVE_DIR) if f.endswith('.json')]) if os.path.exists(WAREHOUSE_SAVE_DIR) else 0,
            'saved_models': len([f for f in os.listdir(MODEL_SAVE_DIR) if f.endswith('.h5')]) if os.path.exists(MODEL_SAVE_DIR) else 0,
            'timestamp': datetime.now().isoformat()
        }
    })

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
        storage_efficiency = shelf_cells / total_cells
        accessibility = usable_space / total_cells
        
        # Generate sample tasks to estimate complexity
        tasks = sample_tasks(warehouse, num_tasks=10)
        avg_distance = 0
        if tasks:
            distances = []
            for task in tasks:
                dist = abs(task['pickup_x'] - task['drop_x']) + abs(task['pickup_y'] - task['drop_y'])
                distances.append(dist)
            avg_distance = np.mean(distances) if distances else 0
        
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
                'free': float(free_cells / total_cells * 100),
                'shelves': float(shelf_cells / total_cells * 100),
                'drop_zones': float(drop_cells / total_cells * 100),
                'pickup_zones': float(pickup_cells / total_cells * 100),
                'obstacles': float(obstacle_cells / total_cells * 100)
            },
            'efficiency_metrics': {
                'storage_efficiency': float(storage_efficiency),
                'accessibility': float(accessibility),
                'average_task_distance': float(avg_distance)
            },
            'sample_tasks': len(tasks),
            'complexity_score': float((avg_distance / max(w, h)) * (1 - accessibility))
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

if __name__ == '__main__':
    print("Starting Warehouse Management System")
    print("=" * 50)
    print(f"DQN Training Available: {DQN_AVAILABLE}")
    print(f"Warehouse Save Directory: {WAREHOUSE_SAVE_DIR}")
    print(f"Model Save Directory: {MODEL_SAVE_DIR}")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)