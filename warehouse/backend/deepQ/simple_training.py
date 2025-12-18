"""
Simple Keras DQN for Warehouse Route Optimization
Minimal code approach using TensorFlow/Keras
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import random
from collections import deque
import sys
import os

# Add parent directory to path to import warehouse generator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from warehouseGenerator import make_map, sample_tasks

class SimpleWarehouseEnv:
    """Simple warehouse environment"""
    
    def __init__(self, size=(12, 8)):
        self.w, self.h = size
        self.reset()
    
    def reset(self):
        # Generate simple warehouse
        self.warehouse, _ = make_map(w=self.w, h=self.h, style='parallel')
        
        # Find free spaces
        free_spaces = list(zip(*np.where(self.warehouse == 0)))
        if len(free_spaces) < 2:
            # Fallback if no free spaces
            self.start = (0, 0)
            self.target = (self.w-1, self.h-1)
        else:
            self.start = random.choice(free_spaces)[::-1]  # (x,y)
            self.target = random.choice(free_spaces)[::-1]  # (x,y)
        
        self.agent_pos = self.start
        self.steps = 0
        return self.get_state()
    
    def get_state(self):
        """Return flattened state: warehouse + agent pos + target pos"""
        # Flatten warehouse and normalize
        state = self.warehouse.flatten() / 4.0
        
        # Add agent position (normalized)
        agent_encoded = np.zeros(self.w * self.h)
        agent_encoded[self.agent_pos[1] * self.w + self.agent_pos[0]] = 1.0
        
        # Add target position (normalized)
        target_encoded = np.zeros(self.w * self.h)
        target_encoded[self.target[1] * self.w + self.target[0]] = 1.0
        
        return np.concatenate([state, agent_encoded, target_encoded])
    
    def step(self, action):
        """Actions: 0=up, 1=down, 2=left, 3=right"""
        self.steps += 1
        
        # Calculate new position
        x, y = self.agent_pos
        moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right
        dx, dy = moves[action]
        new_x, new_y = x + dx, y + dy
        
        # Check if move is valid
        if (0 <= new_x < self.w and 0 <= new_y < self.h and 
            self.warehouse[new_y, new_x] in [0, 2, 3]):  # free, drop, or pickup
            self.agent_pos = (new_x, new_y)
            reward = -1  # Small penalty for each step
        else:
            reward = -10  # Penalty for invalid move
        
        # Check if reached target
        done = False
        if self.agent_pos == self.target:
            reward = 100
            done = True
        elif self.steps >= 100:  # Prevent infinite loops
            reward = -50
            done = True
        
        return self.get_state(), reward, done

def create_model(state_size, action_size=4):
    """Create simple neural network"""
    model = keras.Sequential([
        layers.Dense(128, activation='relu', input_shape=(state_size,)),
        layers.Dense(64, activation='relu'),
        layers.Dense(32, activation='relu'),
        layers.Dense(action_size, activation='linear')
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

class SimpleDQNAgent:
    """Minimal DQN agent"""
    
    def __init__(self, state_size, action_size=4):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.model = create_model(state_size, action_size)
    
    def act(self, state):
        """Choose action"""
        if np.random.random() <= self.epsilon:
            return random.randrange(self.action_size)
        q_values = self.model.predict(state.reshape(1, -1), verbose=0)
        return np.argmax(q_values[0])
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience"""
        self.memory.append((state, action, reward, next_state, done))
    
    def replay(self, batch_size=32):
        """Train the model"""
        if len(self.memory) < batch_size:
            return
        
        batch = random.sample(self.memory, batch_size)
        states = np.array([e[0] for e in batch])
        actions = np.array([e[1] for e in batch])
        rewards = np.array([e[2] for e in batch])
        next_states = np.array([e[3] for e in batch])
        dones = np.array([e[4] for e in batch])
        
        # Predict current Q values
        targets = self.model.predict(states, verbose=0)
        
        # Predict next Q values
        next_q_values = self.model.predict(next_states, verbose=0)
        
        # Update targets
        for i in range(batch_size):
            if dones[i]:
                targets[i][actions[i]] = rewards[i]
            else:
                targets[i][actions[i]] = rewards[i] + 0.95 * np.max(next_q_values[i])
        
        # Train model
        self.model.fit(states, targets, epochs=1, verbose=0)
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

def train_simple(episodes=500):
    """Simple training function"""
    env = SimpleWarehouseEnv()
    state_size = len(env.get_state())
    agent = SimpleDQNAgent(state_size)
    
    scores = []
    
    print(f"Training for {episodes} episodes...")
    print(f"State size: {state_size}")
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        
        for step in range(100):  # Max steps per episode
            action = agent.act(state)
            next_state, reward, done = env.step(action)
            agent.remember(state, action, reward, next_state, done)
            
            state = next_state
            total_reward += reward
            
            if done:
                break
        
        # Train every episode
        agent.replay()
        scores.append(total_reward)
        
        # Print progress
        if episode % 100 == 0:
            avg_score = np.mean(scores[-100:])
            print(f"Episode {episode}, Avg Score: {avg_score:.2f}, Epsilon: {agent.epsilon:.3f}")
    
    # Save model
    agent.model.save('simple_warehouse_model.h5')
    print("Model saved as 'simple_warehouse_model.h5'")
    
    return agent

def test_simple(model_path='simple_warehouse_model.h5', num_tests=5):
    """Test the trained model"""
    # Load model
    model = keras.models.load_model(model_path)
    
    # Test environment
    env = SimpleWarehouseEnv()
    
    successes = 0
    
    print(f"\nTesting model on {num_tests} episodes...")
    
    for test in range(num_tests):
        state = env.reset()
        steps = 0
        
        print(f"\nTest {test + 1}:")
        print(f"Start: {env.start}, Target: {env.target}")
        
        for step in range(50):
            # Predict action (no exploration)
            q_values = model.predict(state.reshape(1, -1), verbose=0)
            action = np.argmax(q_values[0])
            
            state, reward, done = env.step(action)
            steps += 1
            
            if done:
                if reward > 50:  # Success
                    successes += 1
                    print(f"SUCCESS in {steps} steps!")
                else:
                    print(f"Failed in {steps} steps")
                break
    
    print(f"\nSuccess rate: {successes}/{num_tests} ({successes/num_tests*100:.1f}%)")

if __name__ == "__main__":
    print("🏭 Simple Warehouse Route Optimization")
    print("=" * 40)
    
    # Train
    agent = train_simple(episodes=300)
    
    # Test
    test_simple()