from kfp import dsl
from kfp.dsl import Output, Dataset

@dsl.component(
    base_image='python:3.12',
    packages_to_install=['spade==4.0.3']
)
def test_spade_server_with_agent(test_results: Output[Dataset]) -> None:
    """
    Prueba el servidor SPADE iniciándolo, verificando conectividad y ejecutando un agente simple
    
    Args:
        test_results: Archivo de resultados del test como artifact
    """
    import asyncio
    import subprocess
    import socket
    import json
    import time
    import shutil
    import os
    from datetime import datetime
    from pathlib import Path
    
    print("🎯 Iniciando test del servidor SPADE + agente simple...")
    
    # Configuración del test
    test_data = {
        "server_started": False,
        "server_accessible": False,
        "test_duration": 0,
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "port": 5222,
        "error": None
    }
    
    server_process = None
    
    try:
        # Función para encontrar puerto disponible
        def find_available_port(start_port=5222):
            for port in range(start_port, start_port + 20):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('localhost', port))
                        return port
                except OSError:
                    continue
            raise Exception("No hay puertos disponibles")
        
        # Paso 1: Encontrar puerto y configurar
        test_data["port"] = find_available_port()
        port = test_data["port"]
        print(f"🔌 Puerto disponible: {port}")
        
        # Paso 2: Iniciar servidor SPADE
        print("📡 Iniciando servidor SPADE...")
        cmd = [
            "spade", "run"
        ]
        
        server_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"🚀 Servidor iniciado (PID: {server_process.pid})")
        
        # Dar tiempo para arrancar
        time.sleep(10)
        
        # Verificar que el proceso sigue corriendo
        if server_process.poll() is None:
            test_data["server_started"] = True
            print("✅ Servidor SPADE iniciado correctamente")
            
            # Paso 3: Probar conectividad
            print(f"🔍 Probando conectividad al puerto {port}...")
            max_attempts = 10
            
            for attempt in range(max_attempts):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(3)
                        result = s.connect_ex(('localhost', port))
                        if result == 0:
                            test_data["server_accessible"] = True
                            print(f"✅ Servidor accesible en puerto {port}")
                            break
                except Exception:
                    pass
                
                print(f"⏳ Intento {attempt + 1}/{max_attempts}...")
                time.sleep(2)
            
            if not test_data["server_accessible"]:
                print(f"❌ Servidor no accesible después de {max_attempts} intentos")
            
            # Paso 3: Ejecutar test de agente (código embebido para Vertex AI)
            print("🤖 Ejecutando test de agente simple...")
            try:
                # Importar SPADE dentro del componente
                from spade.agent import Agent
                from spade.behaviour import CyclicBehaviour, OneShotBehaviour
                from spade.message import Message
                from spade.template import Template
                
                # Definir agente simple inline
                class SimpleTestAgent(Agent):
                    def __init__(self, jid, password):
                        super().__init__(jid, password)
                        self.messages_sent = 0
                        self.messages_received = 0
                        self.max_messages = 5
                        self.message_history = []
                        self.start_time = None
                        self.test_complete = False
                    
                    class SendBehaviour(OneShotBehaviour):
                        async def run(self):
                            self.agent.start_time = datetime.now()
                            print(f"📤 SimpleTestAgent iniciando envío de mensajes...")
                            
                            for i in range(self.agent.max_messages):
                                msg = Message(to=str(self.agent.jid))
                                msg.set_metadata("performative", "inform") 
                                msg.set_metadata("conversation-id", "test-conversation")
                                msg.body = f"test_message_{i}"
                                
                                await self.send(msg)
                                self.agent.messages_sent += 1
                                print(f"📨 Mensaje enviado #{i}: {msg.body}")
                                
                                self.agent.message_history.append({
                                    "type": "sent",
                                    "message": msg.body,
                                    "timestamp": datetime.now().isoformat(),
                                    "to": str(msg.to)
                                })
                                
                                await asyncio.sleep(1)
                            
                            print(f"✅ Envío completado: {self.agent.messages_sent} mensajes")
                    
                    class ReceiveBehaviour(CyclicBehaviour):
                        async def run(self):
                            msg = await self.receive(timeout=30)
                            
                            if msg:
                                self.agent.messages_received += 1
                                print(f"📥 Mensaje recibido #{self.agent.messages_received}: {msg.body}")
                                
                                self.agent.message_history.append({
                                    "type": "received",
                                    "message": msg.body,
                                    "timestamp": datetime.now().isoformat(),
                                    "from": str(msg.sender)
                                })
                                
                                if self.agent.messages_received >= self.agent.max_messages:
                                    print(f"🎯 Test de mensajes completado: {self.agent.messages_received}/{self.agent.max_messages}")
                                    self.agent.test_complete = True
                                    await self.agent.stop()
                            else:
                                if self.agent.messages_sent >= self.agent.max_messages:
                                    print("⏰ Timeout en recepción, terminando agente")
                                    self.agent.test_complete = True
                                    await self.agent.stop()
                    
                    async def setup(self):
                        print(f"🤖 SimpleTestAgent configurado: {self.jid}")
                        
                        template = Template()
                        template.set_metadata("performative", "inform")
                        template.set_metadata("conversation-id", "test-conversation")
                        
                        receive_behaviour = self.ReceiveBehaviour()
                        self.add_behaviour(receive_behaviour, template)
                        
                        send_behaviour = self.SendBehaviour()
                        self.add_behaviour(send_behaviour)
                
                # Ejecutar test de agente inline
                async def run_agent_test():
                    print("🚀 Iniciando test del agente SPADE simple...")
                    
                    agent = SimpleTestAgent("testagent@localhost", "test_password")
                    await agent.start()
                    print(f"✅ Agente iniciado: {agent.jid}")
                    
                    while agent.is_alive() and not agent.test_complete:
                        await asyncio.sleep(1)
                    
                    end_time = datetime.now()
                    duration = (end_time - agent.start_time).total_seconds() if agent.start_time else 0
                    
                    return {
                        "agent_test_summary": {
                            "success": agent.messages_sent == agent.messages_received == agent.max_messages,
                            "messages_sent": agent.messages_sent,
                            "messages_received": agent.messages_received,
                            "expected_messages": agent.max_messages,
                            "test_duration": duration,
                            "start_time": agent.start_time.isoformat() if agent.start_time else None,
                            "end_time": end_time.isoformat()
                        },
                        "message_history": agent.message_history,
                        "agent_info": {
                            "jid": str(agent.jid),
                            "status": "completed" if agent.test_complete else "timeout"
                        }
                    }
                
                # Ejecutar el test
                import asyncio
                agent_results = asyncio.run(run_agent_test())
                
                # Añadir resultados del agente
                test_data["agent_test"] = agent_results
                print("✅ Test de agente completado exitosamente")
                
            except Exception as e:
                print(f"❌ Error en test de agente: {e}")
                import traceback
                traceback.print_exc()
                test_data["agent_error"] = str(e)
            
            # Mantener servidor corriendo un poco más
            print("⏱️ Manteniendo servidor activo (5 segundos más)...")
            time.sleep(5)
            
        else:
            print("❌ El servidor SPADE falló al iniciar")
            stdout, stderr = server_process.communicate()
            test_data["error"] = f"Server failed: {stderr}"
        
    except Exception as e:
        print(f"💥 Error durante el test: {e}")
        test_data["error"] = str(e)
    
    finally:
        # Cleanup del servidor
        if server_process and server_process.poll() is None:
            print("🧹 Terminando servidor...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
                print("✅ Servidor terminado")
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait()
        
        # Finalizar mediciones
        test_data["end_time"] = datetime.now().isoformat()
        
        # Calcular duración
        start = datetime.fromisoformat(test_data["start_time"])
        end = datetime.fromisoformat(test_data["end_time"])
        test_data["test_duration"] = (end - start).total_seconds()
        
        # Determinar éxito (incluyendo agente si existe)
        agent_success = True
        if "agent_test" in test_data:
            agent_success = test_data["agent_test"]["agent_test_summary"]["success"]
        
        success = (test_data["server_started"] and 
                  test_data["server_accessible"] and 
                  not test_data["error"] and
                  agent_success)
        
        test_data["test_success"] = success
        test_data["summary"] = f"SPADE server test {'PASSED' if success else 'FAILED'}"
        
        # Crear resultado para el artifact con información del agente
        agent_info = ""
        if "agent_test" in test_data:
            agent_data = test_data["agent_test"]["agent_test_summary"]
            agent_info = f"""
Agent Test Results:
- Agent Test Success: {agent_data['success']}
- Messages Sent: {agent_data['messages_sent']}
- Messages Received: {agent_data['messages_received']}
- Expected Messages: {agent_data['expected_messages']}
- Agent Duration: {agent_data['test_duration']:.2f} seconds
"""
        elif "agent_error" in test_data:
            agent_info = f"""
Agent Test Results:
- Agent Test Success: False
- Agent Error: {test_data['agent_error']}
"""
        
        status_text = f"""SPADE Server + Agent Test Results
==================================
Overall Test Success: {success}

Server Test:
- Server Started: {test_data['server_started']}
- Server Accessible: {test_data['server_accessible']}
- Port Used: {test_data['port']}
- Server Error: {test_data['error'] or 'None'}
{agent_info}
Total Duration: {test_data['test_duration']:.2f} seconds
Summary: {test_data['summary']}
Timestamp: {test_data['end_time']}

🎯 RESULTADO FINAL: {'✅ SUCCESS' if success else '❌ FAILED'}
"""
        
        # Guardar el resultado en el artifact de Kubeflow
        with open(test_results.path, 'w') as f:
            f.write(status_text)
        
        print(f"📋 Resultado del test: {'✅ EXITOSO' if success else '❌ FALLÓ'}")
        print(f"💾 Resultados guardados en artifact: {test_results.path}")
        
        # También crear un JSON con datos detallados en /output (opcional)
        output_dir = Path("/output")
        output_dir.mkdir(exist_ok=True)
        
        json_file = output_dir / "spade_test_details.json"
        with open(json_file, "w") as f:
            json.dump(test_data, f, indent=2)
        
        print(f"📊 Datos detallados en: {json_file}")
    
    return None

@dsl.pipeline(
    name='spade-server-agent-test-pipeline',
    description='Test del servidor SPADE + agente simple - ejemplo intermedio extendido'
)
def spade_server_agent_test_pipeline():
    """
    Pipeline que prueba el servidor SPADE con un agente simple

    
    El pipeline:
    1. Inicia servidor SPADE (spade run)
    2. Verifica conectividad TCP
    3. Ejecuta agente simple que envía/recibe mensajes
    4. Genera reporte completo con resultados del servidor y agente
    """
    
    # Componente de test
    test_task = test_spade_server_with_agent()
    
    # Configuración del componente
    test_task.set_display_name('Test SPADE Server + Agent')
    test_task.set_cpu_limit('1')
    test_task.set_memory_limit('512Mi')
    
    # Descripción detallada
    test_task.description = (
        "Ejecuta un test del servidor SPADE con un agente simple. "
        "Inicia el servidor XMPP, verifica conectividad, ejecuta agente que envía mensajes, "
        "y genera reporte completo. Ejemplo intermedio extendido con comunicación de agentes."
    )