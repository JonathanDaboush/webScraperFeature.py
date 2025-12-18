"""
Standalone DQN Training Script for Warehouse Route Optimization
This script sets up and trains Deep Q-Learning models independently from the web interface.
"""

import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import argparse

# Add current directory to path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import warehouse generation
from warehouseGenerator import make_map, sample_tasks, visualize_map

# Import DQN components
try:
    from deepQ.beginner_training import SimpleAI, WarehouseEnv
    print("✓ Beginner training module loaded successfully")
    BEGINNER_AVAILABLE = True
except ImportError as e:
    print(f"✗ Beginner training module failed to load: {e}")
    BEGINNER_AVAILABLE = False

try:
    from deepQ.focused_learning import DeepQNetwork, WarehouseEnvironment
    print("✓ Focused learning module loaded successfully") 
    FOCUSED_AVAILABLE = True
except ImportError as e:
    print(f"✗ Focused learning module failed to load: {e}")
    FOCUSED_AVAILABLE = False

class TrainingManager:
    """
    Manages the entire training pipeline for warehouse DQN models
    """
    
    def __init__(self, save_dir="training_results"):
        self.save_dir = save_dir
        self.model_dir = os.path.join(save_dir, "models")
        self.results_dir = os.path.join(save_dir, "results")
        self.warehouse_dir = os.path.join(save_dir, "warehouses")
        
        # Create directories
        for directory in [self.save_dir, self.model_dir, self.results_dir, self.warehouse_dir]:
            os.makedirs(directory, exist_ok=True)
        
        print(f"Training Manager initialized:")
        print(f"  Save directory: {self.save_dir}")
        print(f"  Models will be saved to: {self.model_dir}")
        print(f"  Results will be saved to: {self.results_dir}")
    
    def generate_training_warehouses(self, num_warehouses=5):
        """
        Generate diverse warehouse layouts for training
        """
        print(f"\nGenerating {num_warehouses} diverse warehouse layouts...")
        
        warehouse_configs = [
            # Small parallel warehouses
            {'w': 12, 'h': 8, 'style': 'parallel', 'obstacle_prob': 0.02, 'name': 'small_parallel'},
            {'w': 14, 'h': 10, 'style': 'parallel', 'obstacle_prob': 0.025, 'name': 'medium_parallel'},
            
            # Block style warehouses
            {'w': 16, 'h': 12, 'style': 'block', 'obstacle_prob': 0.03, 'name': 'standard_block'},
            {'w': 18, 'h': 14, 'style': 'block', 'obstacle_prob': 0.035, 'name': 'large_block'},
            
            # Complex layouts
            {'w': 20, 'h': 15, 'style': 'parallel', 'obstacle_prob': 0.04, 'name': 'complex_parallel'},
            {'w': 22, 'h': 16, 'style': 'block', 'obstacle_prob': 0.045, 'name': 'complex_block'},
        ]
        
        generated_warehouses = []
        
        for i, config in enumerate(warehouse_configs[:num_warehouses]):
            print(f"  Generating warehouse {i+1}/{num_warehouses}: {config['name']}")
            
            # Extract name and remove from config
            name = config.pop('name')
            
            # Generate warehouse
            warehouse, meta = make_map(**config)
            
            # Generate sample tasks
            tasks = sample_tasks(warehouse, num_tasks=10)
            
            # Save warehouse data
            warehouse_data = {
                'warehouse': warehouse.tolist(),
                'meta': meta,
                'config': config,
                'tasks': tasks,
                'name': name,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to file
            warehouse_path = os.path.join(self.warehouse_dir, f"{name}.json")
            with open(warehouse_path, 'w') as f:
                json.dump(warehouse_data, f, indent=2)
            
            # Create visualization
            self.visualize_warehouse(warehouse, name, meta)
            
            generated_warehouses.append(warehouse_data)
            
            print(f"    ✓ Saved to {warehouse_path}")
        
        print(f"✓ Generated {len(generated_warehouses)} warehouses successfully")
        return generated_warehouses
    
    def visualize_warehouse(self, warehouse, name, meta):
        """
        Create and save warehouse visualization
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        visualize_map(warehouse, ax=ax, title=f"Training Warehouse: {name}")
        
        # Add metadata to the plot
        info_text = f"Size: {warehouse.shape[1]}x{warehouse.shape[0]}\n"
        info_text += f"Free cells: {np.sum(warehouse == 0)}\n"
        info_text += f"Shelves: {np.sum(warehouse == 1)}\n"
        info_text += f"Drop zones: {np.sum(warehouse == 2)}\n"
        info_text += f"Pickup zones: {np.sum(warehouse == 3)}"
        
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", 
                facecolor="lightgray", alpha=0.8))
        
        # Save visualization
        img_path = os.path.join(self.results_dir, f"{name}_layout.png")
        plt.savefig(img_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"    ✓ Visualization saved to {img_path}")
    
    def train_beginner_model(self, warehouse_data, episodes=1000, model_name=None):
        """
        Train using the beginner-friendly DQN implementation
        """
        if not BEGINNER_AVAILABLE:
            print("✗ Beginner training module not available")
            return None
        
        print(f"\nTraining Beginner DQN Model...")
        print(f"  Episodes: {episodes}")
        
        # Setup model name
        if not model_name:
            model_name = f"beginner_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Convert warehouse data
        warehouse = np.array(warehouse_data['warehouse'])
        
        # Initialize environment and agent
        env = WarehouseEnv(warehouse)
        agent = SimpleAI(learning_rate=0.001, epsilon_decay=0.995)
        
        # Training metrics
        scores = []
        episode_lengths = []
        success_count = 0
        
        print("  Starting training...")
        
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
                    if total_reward > 50:  # Success threshold
                        success_count += 1
                    break
            
            scores.append(total_reward)
            episode_lengths.append(steps)
            
            # Progress reporting
            if episode % 100 == 0:
                recent_avg = np.mean(scores[-100:]) if len(scores) >= 100 else np.mean(scores)
                success_rate = success_count / (episode + 1)
                print(f"    Episode {episode}: Avg Score = {recent_avg:.2f}, Success Rate = {success_rate:.2%}")
        
        # Save model
        model_path = os.path.join(self.model_dir, f"{model_name}.json")
        agent.save_model(model_path)
        
        # Save training results
        results = {
            'model_name': model_name,
            'model_type': 'beginner',
            'warehouse_name': warehouse_data['name'],
            'episodes': episodes,
            'final_scores': scores,
            'episode_lengths': episode_lengths,
            'final_success_rate': success_count / episodes,
            'average_score': np.mean(scores),
            'final_average': np.mean(scores[-100:]) if len(scores) >= 100 else np.mean(scores),
            'timestamp': datetime.now().isoformat()
        }
        
        results_path = os.path.join(self.results_dir, f"{model_name}_results.json")
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Create training plots
        self.plot_training_results(results, model_name)
        
        print(f"  ✓ Model saved to {model_path}")
        print(f"  ✓ Results saved to {results_path}")
        print(f"  ✓ Final success rate: {results['final_success_rate']:.2%}")
        
        return results
    
    def train_focused_model(self, warehouse_data, episodes=1000, model_name=None):
        """
        Train using the focused learning DQN implementation
        """
        if not FOCUSED_AVAILABLE:
            print("✗ Focused training module not available")
            return None
        
        print(f"\nTraining Focused DQN Model...")
        print(f"  Episodes: {episodes}")
        
        # Setup model name
        if not model_name:
            model_name = f"focused_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Convert warehouse data
        warehouse = np.array(warehouse_data['warehouse'])
        
        # Initialize environment and agent
        env = WarehouseEnvironment(warehouse)
        agent = DeepQNetwork(learning_rate=0.001)
        
        # Training metrics
        scores = []
        episode_lengths = []
        losses = []
        success_count = 0
        
        print("  Starting training...")
        
        for episode in range(episodes):
            state = env.reset()
            total_reward = 0
            steps = 0
            episode_losses = []
            max_steps = 200
            
            while steps < max_steps:
                action = agent.choose_action(state)
                next_state, reward, done = env.step(action)
                
                # Store experience and train
                loss = agent.train_step(state, action, reward, next_state, done)
                if loss is not None:
                    episode_losses.append(loss)
                
                state = next_state
                total_reward += reward
                steps += 1
                
                if done:
                    if total_reward > 50:  # Success threshold
                        success_count += 1
                    break
            
            scores.append(total_reward)
            episode_lengths.append(steps)
            if episode_losses:
                losses.extend(episode_losses)
            
            # Progress reporting
            if episode % 100 == 0:
                recent_avg = np.mean(scores[-100:]) if len(scores) >= 100 else np.mean(scores)
                success_rate = success_count / (episode + 1)
                avg_loss = np.mean(losses[-100:]) if len(losses) >= 100 else np.mean(losses) if losses else 0
                print(f"    Episode {episode}: Avg Score = {recent_avg:.2f}, Success Rate = {success_rate:.2%}, Loss = {avg_loss:.4f}")
        
        # Save model
        model_path = os.path.join(self.model_dir, f"{model_name}")
        agent.save_model(model_path)
        
        # Save training results
        results = {
            'model_name': model_name,
            'model_type': 'focused',
            'warehouse_name': warehouse_data['name'],
            'episodes': episodes,
            'final_scores': scores,
            'episode_lengths': episode_lengths,
            'losses': losses[-1000:] if len(losses) > 1000 else losses,  # Save last 1000 losses
            'final_success_rate': success_count / episodes,
            'average_score': np.mean(scores),
            'final_average': np.mean(scores[-100:]) if len(scores) >= 100 else np.mean(scores),
            'timestamp': datetime.now().isoformat()
        }
        
        results_path = os.path.join(self.results_dir, f"{model_name}_results.json")
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Create training plots
        self.plot_training_results(results, model_name)
        
        print(f"  ✓ Model saved to {model_path}")
        print(f"  ✓ Results saved to {results_path}")
        print(f"  ✓ Final success rate: {results['final_success_rate']:.2%}")
        
        return results
    
    def plot_training_results(self, results, model_name):
        """
        Create comprehensive training plots
        """
        scores = results['final_scores']
        episode_lengths = results['episode_lengths']
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Training scores
        ax1.plot(scores, alpha=0.6, label='Episode Score')
        if len(scores) >= 100:
            moving_avg = np.convolve(scores, np.ones(100)/100, mode='valid')
            ax1.plot(range(99, len(scores)), moving_avg, 'r-', linewidth=2, label='100-Episode Average')
        ax1.set_title('Training Scores')
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Score')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Episode lengths
        ax2.plot(episode_lengths, alpha=0.6, label='Episode Length')
        if len(episode_lengths) >= 100:
            moving_avg = np.convolve(episode_lengths, np.ones(100)/100, mode='valid')
            ax2.plot(range(99, len(episode_lengths)), moving_avg, 'r-', linewidth=2, label='100-Episode Average')
        ax2.set_title('Episode Lengths')
        ax2.set_xlabel('Episode')
        ax2.set_ylabel('Steps')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Success rate
        window_size = 100
        success_rates = []
        for i in range(len(scores)):
            start_idx = max(0, i - window_size + 1)
            window_scores = scores[start_idx:i+1]
            success_rate = sum(1 for score in window_scores if score > 50) / len(window_scores)
            success_rates.append(success_rate)
        
        ax3.plot(success_rates, label='Success Rate')
        ax3.set_title(f'Success Rate ({window_size}-episode window)')
        ax3.set_xlabel('Episode')
        ax3.set_ylabel('Success Rate')
        ax3.set_ylim([0, 1])
        ax3.grid(True, alpha=0.3)
        
        # Loss (if available)
        if 'losses' in results and results['losses']:
            ax4.plot(results['losses'], alpha=0.6)
            ax4.set_title('Training Loss')
            ax4.set_xlabel('Training Step')
            ax4.set_ylabel('Loss')
            ax4.grid(True, alpha=0.3)
        else:
            # Score distribution
            ax4.hist(scores, bins=30, alpha=0.7, edgecolor='black')
            ax4.set_title('Score Distribution')
            ax4.set_xlabel('Score')
            ax4.set_ylabel('Frequency')
            ax4.grid(True, alpha=0.3)
        
        plt.suptitle(f'Training Results: {model_name}', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # Save plot
        plot_path = os.path.join(self.results_dir, f"{model_name}_training_curves.png")
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Training plots saved to {plot_path}")
    
    def run_full_training_pipeline(self, num_warehouses=3, episodes_per_model=1000):
        """
        Run the complete training pipeline
        """
        print("=" * 80)
        print("WAREHOUSE DQN TRAINING PIPELINE")
        print("=" * 80)
        
        # Step 1: Generate warehouses
        warehouses = self.generate_training_warehouses(num_warehouses)
        
        # Step 2: Train models on each warehouse
        all_results = []
        
        for i, warehouse_data in enumerate(warehouses):
            print(f"\n" + "=" * 60)
            print(f"TRAINING ON WAREHOUSE {i+1}/{len(warehouses)}: {warehouse_data['name']}")
            print("=" * 60)
            
            # Train beginner model
            if BEGINNER_AVAILABLE:
                beginner_results = self.train_beginner_model(
                    warehouse_data, 
                    episodes=episodes_per_model,
                    model_name=f"beginner_{warehouse_data['name']}"
                )
                if beginner_results:
                    all_results.append(beginner_results)
            
            # Train focused model
            if FOCUSED_AVAILABLE:
                focused_results = self.train_focused_model(
                    warehouse_data,
                    episodes=episodes_per_model, 
                    model_name=f"focused_{warehouse_data['name']}"
                )
                if focused_results:
                    all_results.append(focused_results)
        
        # Step 3: Generate summary report
        self.generate_summary_report(all_results)
        
        print("\n" + "=" * 80)
        print("TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
        return all_results
    
    def generate_summary_report(self, all_results):
        """
        Generate a comprehensive summary report
        """
        if not all_results:
            print("No results to summarize")
            return
        
        print(f"\n" + "=" * 60)
        print("TRAINING SUMMARY REPORT")
        print("=" * 60)
        
        # Group by model type
        beginner_results = [r for r in all_results if r['model_type'] == 'beginner']
        focused_results = [r for r in all_results if r['model_type'] == 'focused']
        
        summary = {
            'total_models_trained': len(all_results),
            'beginner_models': len(beginner_results),
            'focused_models': len(focused_results),
            'timestamp': datetime.now().isoformat(),
            'results': all_results
        }
        
        # Calculate averages
        if beginner_results:
            summary['beginner_avg_success_rate'] = np.mean([r['final_success_rate'] for r in beginner_results])
            summary['beginner_avg_score'] = np.mean([r['average_score'] for r in beginner_results])
            
        if focused_results:
            summary['focused_avg_success_rate'] = np.mean([r['final_success_rate'] for r in focused_results])
            summary['focused_avg_score'] = np.mean([r['average_score'] for r in focused_results])
        
        # Print summary
        print(f"  Total Models Trained: {summary['total_models_trained']}")
        print(f"  Beginner Models: {summary['beginner_models']}")
        print(f"  Focused Models: {summary['focused_models']}")
        
        if beginner_results:
            print(f"  Beginner Avg Success Rate: {summary['beginner_avg_success_rate']:.2%}")
            print(f"  Beginner Avg Score: {summary['beginner_avg_score']:.2f}")
            
        if focused_results:
            print(f"  Focused Avg Success Rate: {summary['focused_avg_success_rate']:.2%}")
            print(f"  Focused Avg Score: {summary['focused_avg_score']:.2f}")
        
        # Save summary
        summary_path = os.path.join(self.results_dir, "training_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n  ✓ Summary report saved to {summary_path}")

def main():
    """
    Main training script entry point
    """
    parser = argparse.ArgumentParser(description='Train DQN models for warehouse navigation')
    parser.add_argument('--warehouses', type=int, default=3, help='Number of warehouses to generate')
    parser.add_argument('--episodes', type=int, default=1000, help='Episodes per model')
    parser.add_argument('--save-dir', type=str, default='training_results', help='Directory to save results')
    parser.add_argument('--model-type', choices=['beginner', 'focused', 'both'], default='both', 
                       help='Type of model to train')
    
    args = parser.parse_args()
    
    print("Warehouse DQN Training Script")
    print("=" * 50)
    print(f"Configuration:")
    print(f"  Warehouses to generate: {args.warehouses}")
    print(f"  Episodes per model: {args.episodes}")
    print(f"  Save directory: {args.save_dir}")
    print(f"  Model type: {args.model_type}")
    print("=" * 50)
    
    # Check module availability
    print(f"Module availability:")
    print(f"  Beginner training: {BEGINNER_AVAILABLE}")
    print(f"  Focused training: {FOCUSED_AVAILABLE}")
    
    if not BEGINNER_AVAILABLE and not FOCUSED_AVAILABLE:
        print("\n✗ No training modules available. Please check your installation.")
        return
    
    # Initialize training manager
    trainer = TrainingManager(save_dir=args.save_dir)
    
    # Run training pipeline
    if args.model_type == 'both':
        results = trainer.run_full_training_pipeline(
            num_warehouses=args.warehouses,
            episodes_per_model=args.episodes
        )
    else:
        # Generate warehouses
        warehouses = trainer.generate_training_warehouses(args.warehouses)
        results = []
        
        # Train specific model type
        for warehouse_data in warehouses:
            if args.model_type == 'beginner' and BEGINNER_AVAILABLE:
                result = trainer.train_beginner_model(
                    warehouse_data,
                    episodes=args.episodes,
                    model_name=f"beginner_{warehouse_data['name']}"
                )
                if result:
                    results.append(result)
                    
            elif args.model_type == 'focused' and FOCUSED_AVAILABLE:
                result = trainer.train_focused_model(
                    warehouse_data,
                    episodes=args.episodes,
                    model_name=f"focused_{warehouse_data['name']}"
                )
                if result:
                    results.append(result)
        
        # Generate summary
        trainer.generate_summary_report(results)
    
    print(f"\nTraining completed! Results saved to: {args.save_dir}")

if __name__ == "__main__":
    main()