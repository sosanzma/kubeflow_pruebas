import subprocess
import time
import json
import os
import signal
import sys
from pathlib import Path

def run_simfleet_simulation():
    print("Starting SimFleet simulation...")
    
    config_file = "vehicles.json"
    if not os.path.exists(config_file):
        print(f"Error: {config_file} not found")
        return False
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    print(f"Config loaded: {config['simulation_name']}")
    print(f"Vehicles: {len(config['vehicles'])}")
    print(f"Max time: {config['max_time']} seconds")
    print(f"Web interface: http://localhost:{config['http_port']}/app")
    
    spade_process = None
    simfleet_process = None
    
    try:
        print("\nStep 1: Starting SPADE server...")
        spade_process = subprocess.Popen(
            ["spade", "run"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("SPADE server started (PID: {})".format(spade_process.pid))
        print("Waiting for SPADE server to initialize...")
        time.sleep(5)
        
        print("\nStep 2: Starting SimFleet simulation...")
        simfleet_process = subprocess.Popen(
            ["simfleet", "--config", config_file, "--autorun"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"SimFleet started (PID: {simfleet_process.pid})")
        print(f"Open browser: http://localhost:{config['http_port']}/app")
        print("Press Ctrl+C to stop simulation")
        
        simfleet_process.wait()
        
        print("\nSimFleet simulation completed")
        
        if simfleet_process.stdout:
            stdout = simfleet_process.stdout.read().decode()
            if stdout:
                print("SimFleet output:")
                print(stdout)
        
        return True
        
    except KeyboardInterrupt:
        print("\nStopping simulation...")
        
    except Exception as e:
        print(f"Error running simulation: {e}")
        return False
        
    finally:
        if simfleet_process and simfleet_process.poll() is None:
            print("Terminating SimFleet...")
            simfleet_process.terminate()
            try:
                simfleet_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                simfleet_process.kill()
        
        if spade_process and spade_process.poll() is None:
            print("Terminating SPADE server...")
            spade_process.terminate()
            try:
                spade_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                spade_process.kill()
        
        print("Cleanup completed")
    
    return True

if __name__ == "__main__":
    try:
        success = run_simfleet_simulation()
        if success:
            print("Simulation completed successfully")
        else:
            print("Simulation failed")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)