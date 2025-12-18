"""
Warehouse Route Optimization using Deep Q-Learning

This module implements a reinforcement learning approach to solve warehouse
navigation problems. The system trains an agent to find optimal paths between
pickup and drop locations while avoiding obstacles.

Author: Warehouse Management System
Version: 1.0
Date: 2025
"""

import numpy as np  # For working with numbers and arrays
import tensorflow as tf  # Google's AI library
from tensorflow import keras  # Easy-to-use part of TensorFlow
import random  # For making random choices
import sys
import os

# Import our warehouse generator (the thing that makes warehouse maps)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from warehouseGenerator import make_map

class WarehouseGame:
    """
    Warehouse environment simulation for reinforcement learning.
    
    Manages the state space, action space, and reward structure for training
    an agent to navigate warehouse layouts efficiently. The environment
    provides a discrete grid world where agents must reach target locations
    while avoiding structural obstacles.
    """
    
    def __init__(self):
        print("Initializing warehouse environment...")
        self.warehouse_width = 10   # Grid width dimension
        self.warehouse_height = 8   # Grid height dimension
        self.start_new_game()
    
    def start_new_game(self):
        """Initialize new episode with randomly generated warehouse layout"""
        print("Generating new warehouse configuration...")
        
        # Generate warehouse layout using predefined generator
        # Cell values: 0=free, 1=shelf, 2=drop, 3=pickup, 4=obstacle
        self.warehouse, _ = make_map(w=self.warehouse_width, h=self.warehouse_height, 
                                   style='parallel', obstacle_prob=0.02)
        
        # Identify valid navigation spaces for agent placement
        empty_spaces = []
        for y in range(self.warehouse_height):
            for x in range(self.warehouse_width):
                if self.warehouse[y, x] == 0:  # Navigable cell
                    empty_spaces.append((x, y))
        
        # Assign random start and target positions
        if len(empty_spaces) >= 2:
            self.start_position = random.choice(empty_spaces)
            self.target_position = random.choice(empty_spaces)
            # Ensure distinct start and target locations
            while self.target_position == self.start_position:
                self.target_position = random.choice(empty_spaces)
        else:
            # Fallback positions if insufficient free space
            self.start_position = (0, 0)
            self.target_position = (self.warehouse_width-1, self.warehouse_height-1)
        
        # Initialize agent position and episode metrics
        self.current_position = self.start_position
        self.steps_taken = 0
        
        print(f"Episode initialized - Start: {self.start_position}, Target: {self.target_position}")
        return self.get_current_situation()
    
    def get_current_situation(self):
        """
        Generate state representation for neural network input.
        
        Returns:
            np.array: Flattened state vector containing warehouse layout,
                     agent position, and target position encodings.
        """
        situation = []
        
        # Encode warehouse layout (normalized to [0,1] range)
        for y in range(self.warehouse_height):
            for x in range(self.warehouse_width):
                situation.append(self.warehouse[y, x] / 4.0)
        
        # Encode agent position (one-hot encoding)
        for y in range(self.warehouse_height):
            for x in range(self.warehouse_width):
                if (x, y) == self.current_position:
                    situation.append(1.0)
                else:
                    situation.append(0.0)
        
        # Encode target position (one-hot encoding)
        for y in range(self.warehouse_height):
            for x in range(self.warehouse_width):
                if (x, y) == self.target_position:
                    situation.append(1.0)
                else:
                    situation.append(0.0)
        
        return np.array(situation)
    
    def make_move(self, action):
        """
        The AI chooses an action, and we move the character.
        Actions are: 0=up, 1=down, 2=left, 3=right
        """
        self.steps_taken += 1
        
        # Figure out where the character wants to move
        x, y = self.current_position
        if action == 0:    # Move up
            new_x, new_y = x, y - 1
        elif action == 1:  # Move down
            new_x, new_y = x, y + 1
        elif action == 2:  # Move left
            new_x, new_y = x - 1, y
        elif action == 3:  # Move right
            new_x, new_y = x + 1, y
        else:
            new_x, new_y = x, y  # Invalid action = stay put
        
        # Validate move and calculate reward
        reward = 0
        
        # Boundary violation check
        if new_x < 0 or new_x >= self.warehouse_width or new_y < 0 or new_y >= self.warehouse_height:
            print("Boundary collision detected")
            reward = -10  # Boundary penalty
        # Obstacle collision check
        elif self.warehouse[new_y, new_x] in [1, 4]:  # Shelf or obstacle
            print("Obstacle collision detected")
            reward = -20  # Obstacle penalty
        else:
            # Execute valid movement
            self.current_position = (new_x, new_y)
            reward = -1  # Step cost for path length optimization
            print(f"Agent position updated: {self.current_position}")
        
        # Episode termination conditions
        game_over = False
        if self.current_position == self.target_position:
            print("Target reached successfully")
            reward = 100  # Success reward
            game_over = True
        elif self.steps_taken >= 50:  # Maximum episode length
            print("Episode timeout reached")
            reward = -50  # Timeout penalty
            game_over = True
        
        return self.get_current_situation(), reward, game_over

def create_brain(input_size):
    """
    Initialize neural network architecture for Q-value approximation.
    
    Args:
        input_size (int): Dimension of state space vector
        
    Returns:
        keras.Sequential: Compiled neural network model
    """
    print(f"Initializing neural network with {input_size} input features...")
    
    model = keras.Sequential([
        # Hidden layer 1: Feature extraction
        keras.layers.Dense(64, activation='relu', input_shape=(input_size,)),
        
        # Hidden layer 2: Pattern recognition
        keras.layers.Dense(32, activation='relu'),
        
        # Output layer: Q-value estimation for each action
        keras.layers.Dense(4, activation='linear')
    ])
    
    # Configure optimization parameters
    model.compile(optimizer='adam', loss='mse')
    
    print("Neural network architecture initialized successfully")
    return model

class SimpleAI:
    """
    Deep Q-Network agent implementation for warehouse navigation.
    
    Implements experience replay and epsilon-greedy exploration strategy
    to learn optimal navigation policies through reinforcement learning.
    """
    
    def __init__(self, situation_size):
        print("Initializing DQN agent...")
        
        self.brain = create_brain(situation_size)  # Neural network for Q-value approximation
        self.memory = []  # Experience replay buffer
        self.exploration_rate = 1.0  # Epsilon for epsilon-greedy policy
        self.learning_rate = 0.95  # Discount factor for future rewards
        
        print("DQN agent initialization complete")
    
    def choose_action(self, situation):
        """
        Given the current situation, choose what to do.
        Sometimes explore randomly, sometimes use what we've learned.
        """
        # Should we explore (try random moves) or use our knowledge?
        if random.random() < self.exploration_rate:
            # Explore: try a random action
            action = random.randint(0, 3)  # 0, 1, 2, or 3
            #print(f"🎲 Trying random action: {action}")
        else:
            # Use brain: ask the neural network what to do
            situation_reshaped = situation.reshape(1, -1)  # Format for neural network
            action_values = self.brain.predict(situation_reshaped, verbose=0)
            action = np.argmax(action_values[0])  # Pick the action with highest value
            #print(f"🧠 Using brain, chose action: {action}")
        
        return action
    
    def remember_experience(self, situation, action, reward, next_situation, game_over):
        """
        Remember what happened so we can learn from it later.
        """
        self.memory.append((situation, action, reward, next_situation, game_over))
        
        # Don't remember too much (keep only recent experiences)
        if len(self.memory) > 2000:
            self.memory.pop(0)  # Remove oldest memory
    
    def learn_from_experience(self):
        """
        Look back at past experiences and learn from them.
        This is where the AI gets smarter!
        """
        if len(self.memory) < 32:  # Need enough experiences to learn
            return
        
        # Pick random experiences to learn from
        batch = random.sample(self.memory, 32)
        
        # Separate the experiences into parts
        situations = np.array([exp[0] for exp in batch])
        actions = [exp[1] for exp in batch]
        rewards = [exp[2] for exp in batch]
        next_situations = np.array([exp[3] for exp in batch])
        game_overs = [exp[4] for exp in batch]
        
        # Ask brain: "What did you think the value of each action was?"
        current_predictions = self.brain.predict(situations, verbose=0)
        
        # Ask brain: "What do you think about the next situations?"
        next_predictions = self.brain.predict(next_situations, verbose=0)
        
        # Update our understanding based on what actually happened
        for i in range(32):
            if game_overs[i]:
                # Game ended, so the value is just the reward we got
                target_value = rewards[i]
            else:
                # Game continues, so value = reward + best possible future value
                target_value = rewards[i] + self.learning_rate * np.max(next_predictions[i])
            
            # Update the prediction for the action we took
            current_predictions[i][actions[i]] = target_value
        
        # Train the brain with these corrected predictions
        self.brain.fit(situations, current_predictions, epochs=1, verbose=0)
        
        # Reduce exploration rate (become less random over time)
        if self.exploration_rate > 0.01:
            self.exploration_rate *= 0.995

def train_ai(num_games=200):
    """
    Train the AI by letting it play many games.
    It starts terrible but gets better with practice!
    """
    print(f"🎓 Starting training for {num_games} games...")
    
    # Create the game and AI
    game = WarehouseGame()
    situation_size = len(game.get_current_situation())
    ai = SimpleAI(situation_size)
    
    scores = []  # Keep track of how well the AI is doing
    
    for game_num in range(num_games):
        print(f"\n--- Game {game_num + 1} ---")
        
        # Start a new game
        situation = game.start_new_game()
        total_reward = 0
        
        # Play the game
        for step in range(50):  # Max 50 moves per game
            # AI chooses what to do
            action = ai.choose_action(situation)
            
            # Make the move and see what happens
            next_situation, reward, game_over = game.make_move(action)
            
            # AI remembers what happened
            ai.remember_experience(situation, action, reward, next_situation, game_over)
            
            # Update for next step
            situation = next_situation
            total_reward += reward
            
            if game_over:
                break
        
        # AI learns from this game
        ai.learn_from_experience()
        
        scores.append(total_reward)
        
        # Print progress every 25 games
        if (game_num + 1) % 25 == 0:
            recent_average = np.mean(scores[-25:])
            print(f"📊 Games {game_num-24}-{game_num+1}: Average score = {recent_average:.1f}")
            print(f"🎲 Exploration rate: {ai.exploration_rate:.3f}")
    
    # Save the trained AI brain
    ai.brain.save('trained_warehouse_ai.h5')
    print("\n💾 Saved trained AI as 'trained_warehouse_ai.h5'")
    
    return ai

def test_ai():
    """
    Test how well our trained AI performs.
    """
    print("\n🧪 Testing the trained AI...")
    
    # Load the trained brain
    try:
        brain = keras.models.load_model('trained_warehouse_ai.h5')
        print("✅ Loaded trained AI brain")
    except:
        print("❌ Could not load trained AI. Make sure to train first!")
        return
    
    # Create test game
    game = WarehouseGame()
    
    successes = 0
    total_tests = 5
    
    for test_num in range(total_tests):
        print(f"\n--- Test {test_num + 1} ---")
        
        situation = game.start_new_game()
        
        for step in range(50):
            # AI chooses action (no random exploration now)
            situation_reshaped = situation.reshape(1, -1)
            action_values = brain.predict(situation_reshaped, verbose=0)
            action = np.argmax(action_values[0])
            
            # Make the move
            situation, reward, game_over = game.make_move(action)
            
            if game_over:
                if reward > 50:  # Success!
                    successes += 1
                    print(f"✅ SUCCESS in {step + 1} steps!")
                else:
                    print(f"❌ Failed after {step + 1} steps")
                break
    
    print(f"\n📊 Final Results: {successes}/{total_tests} games won ({successes/total_tests*100:.1f}%)")

if __name__ == "__main__":
    print("Warehouse Route Optimization System")
    print("=" * 50)
    print("Deep Q-Learning implementation for autonomous warehouse navigation")
    print("Training phase: Learning optimal pathfinding strategies")
    print()
    
    # Execute training protocol
    ai = train_ai(num_games=150)
    
    # Evaluate trained model performance
    test_ai()
    
    print("\nTraining protocol completed successfully")
    print("Model weights saved to: trained_warehouse_ai.h5")