"""
Simple test script to verify the warehouse system works
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_warehouse_generator():
    """Test the warehouse generator"""
    try:
        from warehouseGenerator import make_map, sample_tasks
        print("✓ Warehouse generator imported successfully")
        
        # Test warehouse generation
        warehouse, meta = make_map(w=10, h=8, style='parallel')
        print(f"✓ Generated warehouse: {warehouse.shape[1]}x{warehouse.shape[0]}")
        
        # Test task generation
        tasks = sample_tasks(warehouse, num_tasks=3)
        print(f"✓ Generated {len(tasks)} tasks")
        
        return True
    except Exception as e:
        print(f"✗ Warehouse generator test failed: {e}")
        return False

def test_beginner_training():
    """Test the beginner training module"""
    try:
        from deepQ.beginner_training import SimpleAI, WarehouseEnv
        print("✓ Beginner training module imported successfully")
        
        # Test environment creation
        import numpy as np
        test_warehouse = np.zeros((8, 10))
        env = WarehouseEnv(test_warehouse)
        print("✓ Warehouse environment created")
        
        # Test agent creation
        agent = SimpleAI()
        print("✓ Simple AI agent created")
        
        return True
    except Exception as e:
        print(f"✗ Beginner training test failed: {e}")
        return False

def test_keras_training():
    """Test the Keras training module (optional)"""
    try:
        # Try to import TensorFlow first
        import tensorflow as tf
        print("✓ TensorFlow available")
        
        from deepQ.training import WarehouseEnv as KerasWarehouseEnv, DQNAgent
        print("✓ Keras training module imported successfully")
        
        return True
    except ImportError as e:
        print(f"ℹ Keras training module not available (TensorFlow not installed): {e}")
        return False
    except Exception as e:
        print(f"✗ Keras training test failed: {e}")
        return False

def test_flask_dependencies():
    """Test Flask and web dependencies"""
    try:
        import flask
        from flask import Flask, request, jsonify
        print("✓ Flask imported successfully")
        
        try:
            from flask_cors import CORS
            print("✓ Flask-CORS imported successfully")
        except ImportError:
            print("ℹ Flask-CORS not available (optional)")
        
        return True
    except Exception as e:
        print(f"✗ Flask test failed: {e}")
        return False

def main():
    print("Warehouse System Component Test")
    print("=" * 50)
    
    results = []
    
    # Test warehouse generator
    print("\n1. Testing Warehouse Generator...")
    results.append(test_warehouse_generator())
    
    # Test beginner training
    print("\n2. Testing Beginner Training Module...")
    results.append(test_beginner_training())
    
    # Test Keras training (optional)
    print("\n3. Testing Keras Training Module...")
    results.append(test_keras_training())
    
    # Test Flask dependencies
    print("\n4. Testing Flask Dependencies...")
    results.append(test_flask_dependencies())
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results)
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    
    if passed_tests >= 2:  # At least warehouse generator and beginner training
        print("\n✓ MINIMUM REQUIREMENTS MET")
        print("The system should work with basic functionality.")
        
        if passed_tests == total_tests:
            print("✓ ALL TESTS PASSED - Full functionality available!")
        else:
            print("ℹ Some advanced features may not be available.")
    else:
        print("\n✗ CRITICAL ERRORS DETECTED")
        print("Please check your Python environment and dependencies.")
    
    return passed_tests >= 2

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)