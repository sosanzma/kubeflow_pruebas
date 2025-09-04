from kfp import dsl
from kfp.dsl import Output, Dataset

@dsl.component(
    base_image='python:3.12',
    packages_to_install=['simfleet']
)
def simfleet_basic_simulation(
    max_simulation_time: int = 30,
    num_vehicles: int = 2,
    results_output: Output[Dataset] = None
) -> None:
    import subprocess
    import time
    import json
    import os
    import tempfile
    from datetime import datetime
    from pathlib import Path
    
    print("Starting SimFleet simulation in Kubeflow...")
    
    def create_simulation_config():
        config = {
            "fleets": [],
            "transports": [],
            "customers": [],
            "stations": [],
            "vehicles": [
                {
                    "speed": 2000,
                    "class": "simfleet.common.lib.vehicles.models.vehicle.VehicleAgent",
                    "position": [39.457364, -0.401621],
                    "destination": [39.45333818, -0.33223699],
                    "password": "secret",
                    "name": "drone1",
                    "icon": "drone"
                }
            ],
            "simulation_name": "kubeflow_fleet",
            "max_time": max_simulation_time,
            "vehicle_strategy": "simfleet.common.lib.vehicles.strategies.vehicle.FSMOneShotVehicleBehaviour",
            "host": "localhost",
            "http_port": 9000
        }
        
        if num_vehicles >= 2:
            config["vehicles"].append({
                "speed": 1800,
                "class": "simfleet.common.lib.vehicles.models.vehicle.VehicleAgent",
                "position": [39.460000, -0.405000],
                "destination": [39.450000, -0.330000],
                "password": "secret",
                "name": "drone2",
                "icon": "drone"
            })
        
        return config
    
    def run_simfleet_headless():
        config = create_simulation_config()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_file:
            json.dump(config, config_file, indent=2)
            config_path = config_file.name
        
        print(f"Config created: {config['simulation_name']}")
        print(f"Vehicles: {len(config['vehicles'])}")
        print(f"Max time: {config['max_time']} seconds")
        
        spade_process = None
        simfleet_process = None
        
        try:
            print("Step 1: Starting SPADE server...")
            spade_process = subprocess.Popen(
                ["spade", "run"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print(f"SPADE server started (PID: {spade_process.pid})")
            print("Waiting for SPADE server to initialize...")
            time.sleep(8)
            
            print("Step 2: Starting SimFleet simulation...")
            simfleet_process = subprocess.Popen(
                ["simfleet", "--config", config_path, "--autorun"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print(f"SimFleet started (PID: {simfleet_process.pid})")
            
            simfleet_process.wait(timeout=max_simulation_time + 30)
            
            stdout, stderr = simfleet_process.communicate()
            
            results = {
                "simulation_success": simfleet_process.returncode == 0,
                "configuration": {
                    "max_time": max_simulation_time,
                    "vehicles": num_vehicles,
                    "simulation_name": config['simulation_name']
                },
                "simfleet_output": stdout if stdout else "",
                "simfleet_errors": stderr if stderr else "",
                "return_code": simfleet_process.returncode,
                "execution_time": max_simulation_time,
                "timestamp": datetime.now().isoformat()
            }
            
            print("SimFleet simulation completed")
            if stdout:
                print("SimFleet stdout:")
                print(stdout[:1000])
            if stderr:
                print("SimFleet stderr:")
                print(stderr[:1000])
            
            return results
            
        except subprocess.TimeoutExpired:
            print("Simulation timeout reached")
            results = {
                "simulation_success": False,
                "error": "Simulation timeout",
                "configuration": {"max_time": max_simulation_time, "vehicles": num_vehicles},
                "timestamp": datetime.now().isoformat()
            }
            return results
            
        except Exception as e:
            print(f"Error during simulation: {e}")
            results = {
                "simulation_success": False,
                "error": str(e),
                "configuration": {"max_time": max_simulation_time, "vehicles": num_vehicles},
                "timestamp": datetime.now().isoformat()
            }
            return results
            
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
            
            try:
                os.unlink(config_path)
            except:
                pass
            
            print("Cleanup completed")
    
    try:
        print("Executing SimFleet simulation...")
        simulation_results = run_simfleet_headless()
        
        success = simulation_results.get("simulation_success", False)
        config = simulation_results.get("configuration", {})
        
        status_text = f"""SimFleet Basic Simulation Results
====================================
Overall Simulation Success: {success}

Configuration:
- Simulation Time: {config.get('max_time', 'Unknown')} seconds
- Number of Vehicles: {config.get('vehicles', 'Unknown')}
- Simulation Name: {config.get('simulation_name', 'Unknown')}

Execution Details:
- Return Code: {simulation_results.get('return_code', 'N/A')}
- Execution Time: {simulation_results.get('execution_time', 'N/A')} seconds
- Error: {simulation_results.get('error', 'None')}

SimFleet Output:
{simulation_results.get('simfleet_output', 'No output captured')[:2000]}

SimFleet Errors:
{simulation_results.get('simfleet_errors', 'No errors')[:1000]}

Timestamp: {simulation_results.get('timestamp', 'Unknown')}

RESULTADO FINAL: {'SUCCESS' if success else 'FAILED'}

==== DETAILED RESULTS (JSON) ====
{json.dumps(simulation_results, indent=2)[:1000]}...
"""
        
        with open(results_output.path, 'w') as f:
            f.write(status_text)
        
        print(f"Results saved to artifact: {results_output.path}")
        print(f"Final Status: {'SUCCESS' if success else 'FAILED'}")
        
        if not success:
            raise Exception(f"SimFleet simulation failed: {simulation_results.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"Error in SimFleet simulation: {e}")
        import traceback
        
        error_text = f"""SimFleet Basic Simulation Results
====================================
Overall Simulation Success: False

FATAL ERROR: {str(e)}

Timestamp: {datetime.now().isoformat()}

RESULTADO FINAL: FAILED

Traceback:
{traceback.format_exc()}
"""
        
        with open(results_output.path, 'w') as f:
            f.write(error_text)
        
        raise

@dsl.pipeline(
    name='simfleet-basic-simulation-pipeline',
    description='Simulación básica de flota usando SimFleet framework real'
)
def simfleet_basic_pipeline(
    max_simulation_time: int = 30,
    num_vehicles: int = 2
):
    simfleet_task = simfleet_basic_simulation(
        max_simulation_time=max_simulation_time,
        num_vehicles=num_vehicles
    )
    
    simfleet_task.set_display_name('SimFleet Real Simulation')
    simfleet_task.set_cpu_limit('2')
    simfleet_task.set_memory_limit('2Gi')
    
    simfleet_task.description = (
        "Ejecuta una simulación real usando SimFleet framework. "
        "Incluye servidor SPADE integrado y vehículos drone con "
        "configuración JSON completa y captura de resultados reales."
    )