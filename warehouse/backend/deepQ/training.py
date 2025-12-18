"""
Professional Keras DQN for Warehouse Route Optimization
Complete implementation using TensorFlow/Keras
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import random
import matplotlib.pyplot as plt
from collections import deque
import sys
import os

# Add parent directory to path to import warehouse generator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from warehouseGenerator import make_map, sample_tasks

class WarehouseEnv:
    """
    Professional warehouse environment for reinforcement learning.
    
    Provides a complete simulation environment with configurable warehouse
    layouts, dynamic task generation, and proper reward structures.
    """
    
    def __init__(self, warehouse_config=None):
        self.warehouse_config = warehouse_config or {
            'w': 16, 'h': 12, 'style': 'parallel',
            'obstacle_prob': 0.03, 'min_aisle': 2, 'max_aisle': 3
        }
        self.reset()
    
    def reset(self):
        """Generate new warehouse layout and task"""
        # Generate warehouse layout
        self.warehouse, self.meta = make_map(**self.warehouse_config)
        self.h, self.w = self.warehouse.shape
        
        # Generate realistic pickup-drop tasks
        tasks = sample_tasks(self.warehouse, num_tasks=1)
        if tasks:
            task = tasks[0]
            self.start_pos = (task['pickup_x'], task['pickup_y'])
            self.target_pos = (task['drop_x'], task['drop_y'])
        else:
            # Fallback: random free positions
            free_cells = list(zip(*np.where(self.warehouse == 0)))
            if len(free_cells) >= 2:
                self.start_pos = random.choice(free_cells)[::-1]  # (x,y)
                self.target_pos = random.choice(free_cells)[::-1]  # (x,y)
            else:
                self.start_pos = (0, 0)
                self.target_pos = (self.w-1, self.h-1)
        
        self.agent_pos = self.start_pos
        self.steps = 0
        self.max_steps = self.w * self.h * 2  # Prevent infinite episodes
        
        return self.get_state()
    
    def get_state(self):
        """
        Generate state representation for neural network.
        
        Returns:
            np.array: Flattened state vector with warehouse layout,
                     agent position, and target position encodings.
        """
        # Flatten warehouse layout (normalized)
        warehouse_flat = self.warehouse.flatten() / 4.0
        
        # One-hot encode agent position
        agent_encoding = np.zeros(self.w * self.h)
        agent_encoding[self.agent_pos[1] * self.w + self.agent_pos[0]] = 1.0
        
        # One-hot encode target position
        target_encoding = np.zeros(self.w * self.h)
        target_encoding[self.target_pos[1] * self.w + self.target_pos[0]] = 1.0
        
        return np.concatenate([warehouse_flat, agent_encoding, target_encoding])
    
    def step(self, action):
        """
        Execute action and return environment response.
        
        Args:
            action (int): Action to take (0=up, 1=down, 2=left, 3=right)
            
        Returns:
            tuple: (next_state, reward, done, info)
        """
        self.steps += 1
        
        # Calculate new position based on action
        x, y = self.agent_pos
        if action == 0:    # up
            new_pos = (x, y - 1)
        elif action == 1:  # down
            new_pos = (x, y + 1)
        elif action == 2:  # left
            new_pos = (x - 1, y)
        elif action == 3:  # right
            new_pos = (x + 1, y)
        else:
            new_pos = (x, y)  # invalid action = stay put
        
        # Validate move and calculate reward
        new_x, new_y = new_pos
        if new_x < 0 or new_x >= self.w or new_y < 0 or new_y >= self.h:
            # Boundary collision
            reward = -10
        elif self.warehouse[new_y, new_x] in [1, 4]:  # Shelf or obstacle
            # Obstacle collision
            reward = -20
        else:
            # Valid move
            self.agent_pos = new_pos
            reward = -1  # Step penalty for efficiency
        
        # Check termination conditions
        done = False
        info = {'steps': self.steps}
        
        if self.agent_pos == self.target_pos:
            reward = 100  # Success reward
            done = True
            info['success'] = True
        elif self.steps >= self.max_steps:
            reward = -50  # Timeout penalty
            done = True
            info['timeout'] = True
        
        info['distance_to_target'] = abs(self.agent_pos[0] - self.target_pos[0]) + \
                                   abs(self.agent_pos[1] - self.target_pos[1])
        
        return self.get_state(), reward, done, info

def create_dqn_model(state_size, action_size=4, learning_rate=0.001):
    """
    Create Deep Q-Network architecture.
    
    Args:
        state_size (int): Dimension of state space
        action_size (int): Number of possible actions
        learning_rate (float): Optimizer learning rate
        
    Returns:
        keras.Model: Compiled DQN model
    """
    model = keras.Sequential([
        # Input layer
        layers.Dense(128, activation='relu', input_shape=(state_size,)),
        layers.Dropout(0.2),
        
        # Hidden layers
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.2),
        
        layers.Dense(32, activation='relu'),
        
        # Output layer (Q-values for each action)
        layers.Dense(action_size, activation='linear')
    ])
    
    # Compile with appropriate optimizer and loss
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss='mse',
        metrics=['mae']
    )
    
    return model

class DQNAgent:
    """
    Deep Q-Network agent implementation.
    
    Features:
    - Experience replay for stable learning
    - Epsilon-greedy exploration strategy
    - Target network for improved stability
    - Configurable hyperparameters
    """
    
    def __init__(self, state_size, action_size=4, learning_rate=0.001, 
                 gamma=0.99, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        # Experience replay buffer
        self.memory = deque(maxlen=10000)
        self.batch_size = 32
        
        # Neural networks
        self.q_network = create_dqn_model(state_size, action_size, learning_rate)
        self.target_network = create_dqn_model(state_size, action_size, learning_rate)
        
        # Initialize target network with same weights
        self.update_target_network()
        
        # Training parameters
        self.update_every = 4
        self.target_update_every = 1000
        self.step_count = 0
        
        print(f"DQN Agent initialized:")
        print(f"  State size: {state_size}")
        print(f"  Action size: {action_size}")
        print(f"  Learning rate: {learning_rate}")
        print(f"  Memory capacity: {len(self.memory)}")
    
    def act(self, state, training=True):
        """
        Choose action using epsilon-greedy policy.
        
        Args:
            state (np.array): Current state
            training (bool): Whether in training mode
            
        Returns:
            int: Selected action
        """
        if training and random.random() < self.epsilon:
            # Explore: choose random action
            return random.randint(0, self.action_size - 1)
        
        # Exploit: choose best action according to Q-network
        state_batch = np.expand_dims(state, axis=0)
        q_values = self.q_network.predict(state_batch, verbose=0)
        return np.argmax(q_values[0])
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay buffer"""
        self.memory.append((state, action, reward, next_state, done))
    
    def replay(self):
        """
        Train the Q-network using experience replay.
        
        Returns:
            float: Training loss
        """
        if len(self.memory) < self.batch_size:
            return None
        
        # Sample random batch from memory
        batch = random.sample(self.memory, self.batch_size)
        states = np.array([e[0] for e in batch])
        actions = np.array([e[1] for e in batch])
        rewards = np.array([e[2] for e in batch])
        next_states = np.array([e[3] for e in batch])
        dones = np.array([e[4] for e in batch])
        
        # Current Q-values
        current_q_values = self.q_network.predict(states, verbose=0)
        
        # Next Q-values from target network
        next_q_values = self.target_network.predict(next_states, verbose=0)
        
        # Calculate target Q-values using Bellman equation
        targets = current_q_values.copy()
        for i in range(self.batch_size):
            if dones[i]:
                targets[i][actions[i]] = rewards[i]
            else:
                targets[i][actions[i]] = rewards[i] + self.gamma * np.max(next_q_values[i])
        
        # Train the network
        history = self.q_network.fit(states, targets, epochs=1, verbose=0, batch_size=self.batch_size)
        loss = history.history['loss'][0]
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        return loss
    
    def update_target_network(self):
        """Copy weights from main network to target network"""
        self.target_network.set_weights(self.q_network.get_weights())
    
    def save(self, filepath):
        """
        Save model weights and training state.
        
        Args:
            filepath (str): Path to save model
        """
        # Save main model
        self.q_network.save(f"{filepath}_main.h5")
        
        # Save target model
        self.target_network.save(f"{filepath}_target.h5")
        
        # Save training parameters
        params = {
            'epsilon': self.epsilon,
            'gamma': self.gamma,
            'learning_rate': self.learning_rate,
            'step_count': self.step_count
        }
        
        import json
        with open(f"{filepath}_params.json", 'w') as f:
            json.dump(params, f)
        
        print(f"Model saved to {filepath}_*.h5 and {filepath}_params.json")
    
    def load(self, filepath):
        """
        Load model weights and training state.
        
        Args:
            filepath (str): Path to load model from
        """
        try:
            # Load main model
            self.q_network = keras.models.load_model(f"{filepath}_main.h5")
            
            # Load target model
            self.target_network = keras.models.load_model(f"{filepath}_target.h5")
            
            # Load training parameters
            import json
            with open(f"{filepath}_params.json", 'r') as f:
                params = json.load(f)
            
            self.epsilon = params.get('epsilon', self.epsilon_min)
            self.gamma = params.get('gamma', 0.99)
            self.learning_rate = params.get('learning_rate', 0.001)
            self.step_count = params.get('step_count', 0)
            
            print(f"Model loaded from {filepath}")
            
        except Exception as e:
            print(f"Error loading model: {e}")

def train_agent(episodes=2000, save_every=500, warehouse_configs=None):
    """
    Train DQN agent on warehouse navigation tasks.
    
    Args:
        episodes (int): Number of training episodes
        save_every (int): Save model every N episodes
        warehouse_configs (list): List of warehouse configurations
        
    Returns:
        tuple: (trained_agent, scores, episode_lengths, losses)
    """
    # Default warehouse configurations for diversity
    if warehouse_configs is None:
        warehouse_configs = [
            {'w': 12, 'h': 8, 'style': 'parallel', 'obstacle_prob': 0.02},
            {'w': 16, 'h': 12, 'style': 'block', 'obstacle_prob': 0.03},
            {'w': 20, 'h': 14, 'style': 'parallel', 'obstacle_prob': 0.025},
            {'w': 14, 'h': 10, 'style': 'block', 'obstacle_prob': 0.035},
        ]
    
    # Initialize environment and agent
    env = WarehouseEnv(warehouse_configs[0])
    state_size = len(env.get_state())
    agent = DQNAgent(state_size)
    
    # Training metrics
    scores = []
    episode_lengths = []
    losses = []
    success_rate_window = deque(maxlen=100)
    
    print(f"\nStarting training for {episodes} episodes...")
    print(f"State space size: {state_size}")
    
    for episode in range(episodes):
        # Vary warehouse configuration for diversity
        config = warehouse_configs[episode % len(warehouse_configs)]
        env = WarehouseEnv(config)
        
        state = env.reset()
        total_reward = 0
        step_count = 0
        episode_losses = []
        
        while True:
            # Agent chooses action
            action = agent.act(state, training=True)
            
            # Execute action
            next_state, reward, done, info = env.step(action)
            
            # Store experience
            agent.remember(state, action, reward, next_state, done)
            
            # Train network
            agent.step_count += 1
            if agent.step_count % agent.update_every == 0:
                loss = agent.replay()
                if loss is not None:
                    episode_losses.append(loss)
            
            # Update target network
            if agent.step_count % agent.target_update_every == 0:
                agent.update_target_network()
            
            state = next_state
            total_reward += reward
            step_count += 1
            
            if done:
                break
        
        # Record metrics
        scores.append(total_reward)
        episode_lengths.append(step_count)
        if episode_losses:
            losses.extend(episode_losses)
        
        # Success tracking
        success = total_reward > 50
        success_rate_window.append(1 if success else 0)
        
        # Progress reporting
        if episode % 100 == 0:
            avg_score = np.mean(scores[-100:])
            avg_length = np.mean(episode_lengths[-100:])
            success_rate = np.mean(success_rate_window)
            avg_loss = np.mean(losses[-100:]) if losses else 0
            
            print(f"\nEpisode {episode}")
            print(f"  Average Score: {avg_score:.2f}")
            print(f"  Average Length: {avg_length:.1f}")
            print(f"  Success Rate: {success_rate:.2%}")
            print(f"  Average Loss: {avg_loss:.4f}")
            print(f"  Epsilon: {agent.epsilon:.3f}")
            print(f"  Memory Size: {len(agent.memory)}")
        
        # Save model periodically
        if episode % save_every == 0 and episode > 0:
            os.makedirs('models', exist_ok=True)
            agent.save(f'models/dqn_warehouse_{episode}')
            print(f"Model saved at episode {episode}")
    
    # Final save
    os.makedirs('models', exist_ok=True)
    agent.save('models/dqn_warehouse_final')
    
    # Plot training curves
    plot_training_curves(scores, episode_lengths, losses)
    
    return agent, scores, episode_lengths, losses

def plot_training_curves(scores, episode_lengths, losses):
    """Plot comprehensive training metrics"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Training scores
    ax1.plot(scores, alpha=0.6)
    if len(scores) >= 100:
        moving_avg = np.convolve(scores, np.ones(100)/100, mode='valid')
        ax1.plot(range(99, len(scores)), moving_avg, 'r-', linewidth=2)
    ax1.set_title('Training Scores')
    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Score')
    ax1.grid(True, alpha=0.3)
    
    # Episode lengths
    ax2.plot(episode_lengths, alpha=0.6)
    if len(episode_lengths) >= 100:
        moving_avg = np.convolve(episode_lengths, np.ones(100)/100, mode='valid')
        ax2.plot(range(99, len(episode_lengths)), moving_avg, 'r-', linewidth=2)
    ax2.set_title('Episode Lengths')
    ax2.set_xlabel('Episode')
    ax2.set_ylabel('Steps')
    ax2.grid(True, alpha=0.3)
    
    # Training loss
    if losses:
        ax3.plot(losses, alpha=0.6)
        ax3.set_title('Training Loss')
        ax3.set_xlabel('Training Step')
        ax3.set_ylabel('Loss')
        ax3.grid(True, alpha=0.3)
    
    # Success rate
    window_size = 100
    success_rates = []
    for i in range(len(scores)):
        start_idx = max(0, i - window_size + 1)
        window_scores = scores[start_idx:i+1]
        success_rate = sum(1 for score in window_scores if score > 50) / len(window_scores)
        success_rates.append(success_rate)
    
    ax4.plot(success_rates)
    ax4.set_title(f'Success Rate ({window_size}-episode window)')
    ax4.set_xlabel('Episode')
    ax4.set_ylabel('Success Rate')
    ax4.set_ylim([0, 1])
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('training_curves.png', dpi=300, bbox_inches='tight')
    plt.show()

def test_agent(model_path='models/dqn_warehouse_final', num_tests=10, visualize=True):
    """
    Test trained agent performance.
    
    Args:
        model_path (str): Path to saved model
        num_tests (int): Number of test episodes
        visualize (bool): Whether to show path visualizations
    """
    # Load trained agent
    print("Loading trained agent...")
    env = WarehouseEnv()
    state_size = len(env.get_state())
    agent = DQNAgent(state_size)
    agent.load(model_path)
    agent.epsilon = 0  # No exploration during testing
    
    # Test configurations
    test_configs = [
        {'w': 16, 'h': 12, 'style': 'parallel', 'obstacle_prob': 0.03},
        {'w': 18, 'h': 14, 'style': 'block', 'obstacle_prob': 0.025},
    ]
    
    total_success = 0
    total_steps = 0
    
    print(f"\nTesting agent on {num_tests} episodes...")
    
    for test_num in range(num_tests):
        config = test_configs[test_num % len(test_configs)]
        env = WarehouseEnv(config)
        state = env.reset()
        
        path = [env.agent_pos]
        total_reward = 0
        steps = 0
        
        print(f"\nTest {test_num + 1}:")
        print(f"  Start: {env.start_pos}, Target: {env.target_pos}")
        
        while steps < 200:  # Maximum steps per test
            action = agent.act(state, training=False)
            state, reward, done, info = env.step(action)
            path.append(env.agent_pos)
            total_reward += reward
            steps += 1
            
            if done:
                break
        
        success = env.agent_pos == env.target_pos
        total_success += success
        total_steps += steps
        
        print(f"  Result: {'SUCCESS' if success else 'FAILED'} in {steps} steps")
        print(f"  Total reward: {total_reward}")
        
        # Visualize first few tests
        if visualize and test_num < 3:
            visualize_path(env.warehouse, path, env.start_pos, env.target_pos,
                         title=f"Test {test_num + 1} - {'Success' if success else 'Failed'}")
    
    print(f"\nOverall Test Results:")
    print(f"  Success Rate: {total_success/num_tests:.1%}")
    print(f"  Average Steps: {total_steps/num_tests:.1f}")

def visualize_path(warehouse, path, start, target, title="Agent Path"):
    """Visualize agent's path through warehouse"""
    plt.figure(figsize=(12, 8))
    
    # Create color map for warehouse elements
    warehouse_colors = warehouse.copy().astype(float)
    
    # Plot warehouse layout
    plt.imshow(warehouse_colors, cmap='tab10', alpha=0.8)
    
    # Plot agent path
    if len(path) > 1:
        path_x = [pos[0] for pos in path]
        path_y = [pos[1] for pos in path]
        plt.plot(path_x, path_y, 'blue', linewidth=3, alpha=0.8, label='Agent Path')
        plt.plot(path_x, path_y, 'o', color='blue', markersize=3, alpha=0.6)
    
    # Mark start and target positions
    plt.plot(start[0], start[1], 's', color='red', markersize=15, label='Start', markeredgecolor='black')
    plt.plot(target[0], target[1], '^', color='green', markersize=15, label='Target', markeredgecolor='black')
    
    plt.title(title, fontsize=14, fontweight='bold')
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    plt.colorbar(label='Cell Type')
    
    # Add cell type legend
    legend_text = ['0: Free', '1: Shelf', '2: Drop', '3: Pickup', '4: Obstacle']
    plt.figtext(0.02, 0.02, '\n'.join(legend_text), fontsize=10, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("Professional DQN Warehouse Navigation System")
    print("=" * 60)
    
    # Training configuration
    training_config = {
        'episodes': 1000,
        'save_every': 200,
        'warehouse_configs': [
            {'w': 12, 'h': 8, 'style': 'parallel', 'obstacle_prob': 0.02},
            {'w': 16, 'h': 12, 'style': 'block', 'obstacle_prob': 0.03},
        ]
    }
    
    print("Starting training phase...")
    agent, scores, lengths, losses = train_agent(**training_config)
    
    print("\nStarting evaluation phase...")
    test_agent(num_tests=5, visualize=True)
    
    print("\nTraining and evaluation completed successfully!")
    print("Check 'models/' directory for saved weights and 'training_curves.png' for metrics.")