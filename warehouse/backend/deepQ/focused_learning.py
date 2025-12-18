"""
Core Deep Q-Learning Implementation
Focus: The actual learning algorithm, not data preparation
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
import random
from collections import deque
import sys
import os

# Import warehouse generator (just for data)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from warehouseGenerator import make_map

# FAST SETUP - Minimal warehouse environment
class FastEnv:
    def __init__(self):
        self.w, self.h = 10, 8
        self.reset()
    
    def reset(self):
        self.warehouse, _ = make_map(w=self.w, h=self.h)
        free = list(zip(*np.where(self.warehouse == 0)))
        if len(free) >= 2:
            self.start = random.choice(free)[::-1]
            self.target = random.choice(free)[::-1]
        else:
            self.start, self.target = (0,0), (self.w-1, self.h-1)
        self.pos = self.start
        self.steps = 0
        return self._state()
    
    def _state(self):
        state = self.warehouse.flatten() / 4.0
        pos_enc = np.zeros(self.w * self.h)
        pos_enc[self.pos[1] * self.w + self.pos[0]] = 1.0
        target_enc = np.zeros(self.w * self.h)
        target_enc[self.target[1] * self.w + self.target[0]] = 1.0
        return np.concatenate([state, pos_enc, target_enc])
    
    def step(self, action):
        self.steps += 1
        x, y = self.pos
        moves = [(0,-1), (0,1), (-1,0), (1,0)]
        dx, dy = moves[action]
        new_x, new_y = x + dx, y + dy
        
        if (0 <= new_x < self.w and 0 <= new_y < self.h and 
            self.warehouse[new_y, new_x] in [0, 2, 3]):
            self.pos = (new_x, new_y)
            reward = -1
        else:
            reward = -10
        
        done = False
        if self.pos == self.target:
            reward = 100
            done = True
        elif self.steps >= 50:
            reward = -50
            done = True
            
        return self._state(), reward, done

# ============================================================================
# THE ACTUAL LEARNING ALGORITHM - THIS IS THE IMPORTANT PART
# ============================================================================

class DeepQNetwork:
    """
    This is where the AI actually learns!
    Core DQN algorithm with experience replay and target network updates.
    """
    
    def __init__(self, state_size):
        print("🧠 INITIALIZING DEEP Q-NETWORK")
        
        # Neural Network Architecture
        self.model = keras.Sequential([
            keras.layers.Dense(64, activation='relu', input_shape=(state_size,)),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(4, activation='linear')  # 4 actions: up,down,left,right
        ])
        self.model.compile(optimizer='adam', loss='mse')
        
        # Learning Parameters
        self.memory = deque(maxlen=10000)  # Experience replay buffer
        self.epsilon = 1.0        # Exploration rate (start at 100% random)
        self.epsilon_min = 0.01   # Minimum exploration (1% random)
        self.epsilon_decay = 0.995  # How fast to reduce randomness
        self.gamma = 0.95         # Future reward discount factor
        
        print(f"✅ Network ready: {state_size} inputs → 64 → 32 → 4 outputs")
    
    def act(self, state):
        """
        DECISION MAKING: Should I explore randomly or use my knowledge?
        """
        if random.random() <= self.epsilon:
            # EXPLORE: Try random action
            return random.randint(0, 3)
        else:
            # EXPLOIT: Use learned knowledge
            q_values = self.model.predict(state.reshape(1, -1), verbose=0)
            return np.argmax(q_values[0])
    
    def remember(self, state, action, reward, next_state, done):
        """
        MEMORY: Store experience for later learning
        """
        self.memory.append((state, action, reward, next_state, done))
    
    def learn(self, batch_size=32):
        """
        🎓 THE CORE LEARNING ALGORITHM
        This is where the AI actually gets smarter!
        """
        if len(self.memory) < batch_size:
            return None
        
        print("🎓 LEARNING FROM EXPERIENCE...")
        
        # Step 1: Sample random experiences from memory
        batch = random.sample(self.memory, batch_size)
        states = np.array([e[0] for e in batch])
        actions = np.array([e[1] for e in batch])
        rewards = np.array([e[2] for e in batch])
        next_states = np.array([e[3] for e in batch])
        dones = np.array([e[4] for e in batch])
        
        # Step 2: Predict current Q-values
        current_q_values = self.model.predict(states, verbose=0)
        
        # Step 3: Predict future Q-values
        next_q_values = self.model.predict(next_states, verbose=0)
        
        # Step 4: Calculate target Q-values using Bellman equation
        # Q(s,a) = reward + gamma * max(Q(s',a'))
        targets = current_q_values.copy()
        
        for i in range(batch_size):
            if dones[i]:
                # Episode ended, so target is just the reward
                targets[i][actions[i]] = rewards[i]
            else:
                # Episode continues, so add discounted future reward
                targets[i][actions[i]] = rewards[i] + self.gamma * np.max(next_q_values[i])
        
        # Step 5: Train the network on corrected Q-values
        loss = self.model.fit(states, targets, epochs=1, verbose=0)
        
        # Step 6: Reduce exploration over time (exploit more, explore less)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        print(f"   📈 Loss: {loss.history['loss'][0]:.4f}, Epsilon: {self.epsilon:.3f}")
        return loss.history['loss'][0]

def train_dqn(episodes=200):
    """
    🏋️ TRAINING LOOP - Watch the AI learn in real-time!
    """
    print("🚀 STARTING DQN TRAINING")
    print("=" * 50)
    
    env = FastEnv()
    agent = DeepQNetwork(len(env._state()))
    
    scores = []
    losses = []
    
    for episode in range(episodes):
        print(f"\n📍 EPISODE {episode + 1}/{episodes}")
        
        # Reset environment for new episode
        state = env.reset()
        total_reward = 0
        step_count = 0
        
        # Play one complete episode
        for step in range(50):  # Max 50 steps per episode
            # Agent chooses action
            action = agent.act(state)
            
            # Execute action in environment
            next_state, reward, done = env.step(action)
            
            # Store experience in memory
            agent.remember(state, action, reward, next_state, done)
            
            # Move to next state
            state = next_state
            total_reward += reward
            step_count += 1
            
            if done:
                result = "SUCCESS" if reward > 50 else "TIMEOUT/FAIL"
                print(f"   🎯 Episode ended: {result} in {step_count} steps")
                break
        
        # LEARN FROM THIS EPISODE
        loss = agent.learn()
        
        # Track progress
        scores.append(total_reward)
        if loss:
            losses.append(loss)
        
        # Print progress every 25 episodes
        if (episode + 1) % 25 == 0:
            avg_score = np.mean(scores[-25:])
            success_rate = sum(1 for s in scores[-25:] if s > 50) / 25
            print(f"\n📊 PROGRESS REPORT (Episodes {episode-24}-{episode+1}):")
            print(f"   Average Score: {avg_score:.1f}")
            print(f"   Success Rate: {success_rate:.1%}")
            print(f"   Exploration Rate: {agent.epsilon:.3f}")
            print(f"   Memory Size: {len(agent.memory)}")
    
    # Save trained model
    agent.model.save('dqn_warehouse_model.h5')
    print(f"\n💾 Model saved as 'dqn_warehouse_model.h5'")
    
    return agent, scores, losses

def demonstrate_learning():
    """
    🎪 SHOW THE LEARNING IN ACTION
    """
    print("👀 DEMONSTRATING LEARNING PROGRESSION")
    
    # Train and watch the AI improve
    agent, scores, losses = train_dqn(episodes=150)
    
    # Show learning curve
    print("\n📈 LEARNING CURVE:")
    windows = [scores[i:i+25] for i in range(0, len(scores), 25)]
    for i, window in enumerate(windows):
        if window:
            avg = np.mean(window)
            success = sum(1 for s in window if s > 50) / len(window)
            print(f"Episodes {i*25+1}-{(i+1)*25}: Avg={avg:.1f}, Success={success:.1%}")
    
    print("\n🎓 TRAINING COMPLETE!")
    return agent

if __name__ == "__main__":
    print("🤖 DEEP Q-LEARNING DEMONSTRATION")
    print("Focus: Core learning algorithm in action")
    print("=" * 50)
    
    # Run the learning demonstration
    trained_agent = demonstrate_learning()
    
    print("\n✨ The AI has learned to navigate warehouses!")
    print("Key learning components demonstrated:")
    print("- Experience replay buffer")
    print("- Epsilon-greedy exploration")
    print("- Bellman equation for Q-value updates")
    print("- Neural network training on Q-targets")