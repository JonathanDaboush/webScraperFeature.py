"""
Quick start script for warehouse route optimization training
"""

import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from training import train_agent, test_agent

def main():
    print("🏭 Warehouse Route Optimization Training")
    print("=" * 50)
    
    # Quick training configuration
    print("Starting training with 500 episodes...")
    print("This will take approximately 10-20 minutes depending on your hardware.")
    
    # Train with smaller episode count for quick results
    agent, scores, lengths, losses = train_agent(
        episodes=500,
        save_every=100,
        warehouse_configs=[
            {'w': 12, 'h': 8, 'style': 'parallel', 'obstacle_prob': 0.02},
            {'w': 14, 'h': 10, 'style': 'block', 'obstacle_prob': 0.03},
        ]
    )
    
    print("\n✅ Training completed!")
    print("\n🧪 Testing the trained agent...")
    
    # Test the trained model
    test_agent(model_path='models/dqn_warehouse_final.pth', num_tests=5)
    
    print("\n🎉 All done! Check the 'models' folder for saved weights.")
    print("📊 Training curves saved as 'training_curves.png'")

if __name__ == "__main__":
    main()