from kfp import dsl
from kfp.dsl import Output, Dataset

@dsl.component(
    base_image='sosanzma/spade-pingpong:latest',
    packages_to_install=['spade==4.0.3', 'pyjabber>=0.1.9,<=0.2.4', 'slixmpp>=1.8.5,<=1.9.1']
)
def spade_ping_pong_embedded_task(
    max_pings: int = 10,
    ping_interval: int = 2,
    results_output: Output[Dataset] = None
) -> None:
    """
    Ejecuta un sistema multi-agente SPADE completo con código embebido
    
    Args:
        max_pings: Número máximo de mensajes ping a enviar
        ping_interval: Intervalo en segundos entre mensajes ping (actualmente no usado)
        results_output: Archivo de resultados JSON como artifact
    """
    import asyncio
    import subprocess
    import socket
    import signal
    import sys
    import json
    import time
    import os
    from pathlib import Path
    from datetime import datetime
    
    print("🎯 SPADE Ping-Pong System (Versión Embebida) iniciado")
    
    # =================================================================
    # CLASE PROCESS MANAGER (del orchestrator.py)
    # =================================================================
    class ProcessManager:
        """Maneja procesos de manera segura con cleanup automático"""
        
        def __init__(self):
            self.processes = []
            self.setup_signal_handlers()
        
        def setup_signal_handlers(self):
            """Configura manejo de señales para cleanup"""
            def signal_handler(signum, frame):
                print(f"📡 Señal recibida: {signum}")
                self.cleanup()
                sys.exit(0)
            
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
        
        def add_process(self, process):
            """Añade proceso a la lista para cleanup"""
            self.processes.append(process)
        
        def cleanup(self):
            """Termina todos los procesos de manera limpia"""
            print("🧹 Iniciando cleanup de procesos...")
            for process in self.processes:
                if process.poll() is None:  # Proceso aún corriendo
                    print(f"🔄 Terminando proceso PID: {process.pid}")
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                        print(f"✅ Proceso terminado correctamente")
                    except subprocess.TimeoutExpired:
                        print(f"⚠️ Proceso no respondió, forzando kill...")
                        process.kill()
                        process.wait()
    
    # =================================================================
    # FUNCIONES DE UTILIDAD (del orchestrator.py)
    # =================================================================
    def find_available_port(start_port=5222):
        """Encuentra un puerto disponible empezando desde start_port"""
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        raise Exception("No hay puertos disponibles")
    
    async def wait_for_xmpp_server(port=5222, max_attempts=15):
        """Espera hasta que el servidor XMPP esté disponible"""
        print(f"🔍 Verificando servidor XMPP en puerto {port}...")
        
        for attempt in range(max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(2)
                    result = s.connect_ex(('localhost', port))
                    if result == 0:
                        print(f"✅ Servidor XMPP disponible en puerto {port}")
                        return True
            except Exception as e:
                pass
            
            print(f"⏳ Intento {attempt + 1}/{max_attempts}, esperando...")
            await asyncio.sleep(2)
        
        return False
    
    async def start_xmpp_server(port, process_manager):
        """Inicia el servidor XMPP usando spade run"""
        print(f"📡 Iniciando servidor XMPP en puerto {port}...")
        
        try:
            # Usar spade run sin parámetros adicionales
            cmd = ["spade", "run"]
            
            print(f"🔧 Comando: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            print(f"🚀 Servidor XMPP iniciado (PID: {process.pid})")
            process_manager.add_process(process)
            
            # Dar más tiempo para que el servidor arranque
            await asyncio.sleep(8)
            
            return process
        
        except Exception as e:
            print(f"❌ Error iniciando servidor XMPP: {e}")
            raise
    
    # =================================================================
    # AGENTES SPADE (del spade_ping_pong.py)
    # =================================================================
    from spade.agent import Agent
    from spade.behaviour import CyclicBehaviour
    from spade.message import Message
    from spade.template import Template
    
    class PingAgent(Agent):
        """Agente que envía mensajes PING"""
        
        def __init__(self, jid, password, max_pings=10):
            super().__init__(jid, password)
            self.ping_count = 0
            self.max_pings = max_pings
            self.start_time = None
        
        class PingBehaviour(CyclicBehaviour):
            async def run(self):
                if self.agent.start_time is None:
                    self.agent.start_time = datetime.now()
                    print(f"🏓 PingAgent iniciado: {self.agent.start_time}")
                
                if self.agent.ping_count < self.agent.max_pings:
                    # Enviar PING
                    msg = Message(to="pong@localhost")
                    msg.set_metadata("performative", "inform")
                    msg.body = f"ping_{self.agent.ping_count}"
                    
                    await self.send(msg)
                    print(f"📤 Ping enviado #{self.agent.ping_count}: {msg.body}")
                    self.agent.ping_count += 1
                    
                    await asyncio.sleep(2)  # Esperar 2 segundos entre pings
                else:
                    print(f"✅ PingAgent completado. Total pings: {self.agent.ping_count}")
                    await self.agent.stop()
        
        async def setup(self):
            print("🏓 PingAgent configurado")
            ping_behaviour = self.PingBehaviour()
            self.add_behaviour(ping_behaviour)
    
    class PongAgent(Agent):
        """Agente que responde mensajes PONG"""
        
        def __init__(self, jid, password):
            super().__init__(jid, password)
            self.pong_count = 0
            self.responses = []
        
        class PongBehaviour(CyclicBehaviour):
            async def run(self):
                # Esperar mensajes
                msg = await self.receive(timeout=30)
                
                if msg:
                    print(f"📥 Pong recibido: {msg.body}")
                    
                    # Responder con PONG
                    reply = msg.make_reply()
                    reply.body = f"pong_{self.agent.pong_count}"
                    await self.send(reply)
                    
                    # Guardar estadísticas
                    self.agent.responses.append({
                        "received": msg.body,
                        "sent": reply.body,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    print(f"📤 Pong enviado #{self.agent.pong_count}: {reply.body}")
                    self.agent.pong_count += 1
                else:
                    # Timeout - probablemente PingAgent terminó
                    print("⏰ PongAgent timeout - terminando")
                    await self.agent.stop()
        
        async def setup(self):
            print("🏓 PongAgent configurado")
            template = Template()
            template.set_metadata("performative", "inform")
            pong_behaviour = self.PongBehaviour()
            self.add_behaviour(pong_behaviour, template)
    
    # =================================================================
    # FUNCIÓN PRINCIPAL DEL SISTEMA PING-PONG
    # =================================================================
    async def run_ping_pong_system(max_pings):
        """Función principal que ejecuta el sistema ping-pong"""
        
        print("🚀 Iniciando sistema Ping-Pong...")
        
        # Crear agentes
        ping_agent = PingAgent("ping@localhost", "ping_password", max_pings)
        pong_agent = PongAgent("pong@localhost", "pong_password")
        
        # Iniciar agentes
        await ping_agent.start()
        await pong_agent.start()
        
        print("✅ Agentes iniciados, comenzando intercambio...")
        
        # Esperar hasta que terminen
        while ping_agent.is_alive() or pong_agent.is_alive():
            await asyncio.sleep(1)
        
        # Recopilar resultados
        results = {
            "execution_summary": {
                "start_time": ping_agent.start_time.isoformat() if ping_agent.start_time else None,
                "end_time": datetime.now().isoformat(),
                "total_pings": ping_agent.ping_count,
                "total_pongs": pong_agent.pong_count,
                "success": ping_agent.ping_count == pong_agent.pong_count
            },
            "message_history": pong_agent.responses,
            "agent_statistics": {
                "ping_agent": {
                    "messages_sent": ping_agent.ping_count,
                    "status": "completed"
                },
                "pong_agent": {
                    "messages_received": pong_agent.pong_count,
                    "responses_sent": len(pong_agent.responses),
                    "status": "completed"
                }
            }
        }
        
        print(f"📊 Sistema completado:")
        print(f"   - Pings enviados: {results['execution_summary']['total_pings']}")
        print(f"   - Pongs recibidos: {results['execution_summary']['total_pongs']}")
        print(f"   - Éxito: {results['execution_summary']['success']}")
        
        return results
    
    # =================================================================
    # FUNCIÓN PRINCIPAL EMBEBIDA (del orchestrator.py main())
    # =================================================================
    async def main_orchestrator():
        """Función principal del orquestador embebido"""
        print("🎯 SPADE Pipeline Orchestrator embebido iniciado")
        print(f"⏰ Tiempo inicio: {datetime.now().isoformat()}")
        
        # Inicializar gestor de procesos
        process_manager = ProcessManager()
        
        try:
            # 1. Encontrar puerto disponible
            port = find_available_port(5222)
            print(f"🔌 Puerto disponible encontrado: {port}")
            
            # 2. Iniciar servidor XMPP
            xmpp_process = await start_xmpp_server(port, process_manager)
            
            # 3. Dar tiempo al servidor para arrancar completamente
            print("⏳ Esperando a que el servidor XMPP esté completamente listo...")
            await asyncio.sleep(10)
            print("✅ Servidor XMPP debería estar listo")
            
            # 4. Ejecutar sistema ping-pong
            print("🏓 Ejecutando sistema Ping-Pong...")
            start_agents_time = datetime.now()
            
            results = await run_ping_pong_system(max_pings)
            
            end_agents_time = datetime.now()
            execution_duration = (end_agents_time - start_agents_time).total_seconds()
            
            # 5. Añadir metadatos de orquestación
            results["orchestration"] = {
                "xmpp_port": port,
                "start_time": start_agents_time.isoformat(),
                "end_time": end_agents_time.isoformat(),
                "duration_seconds": execution_duration,
                "server_pid": xmpp_process.pid if xmpp_process else None
            }
            
            # 6. Mostrar estadísticas finales
            print("\\n📊 ESTADÍSTICAS FINALES:")
            print(f"   🏓 Mensajes Ping: {results['execution_summary']['total_pings']}")
            print(f"   🏓 Mensajes Pong: {results['execution_summary']['total_pongs']}")
            print(f"   ⏱️ Duración: {execution_duration:.2f} segundos")
            print(f"   ✅ Éxito: {results['execution_summary']['success']}")
            print(f"   🔌 Puerto XMPP: {port}")
            
            return results
            
        except Exception as e:
            print(f"❌ Error en orquestación: {e}")
            
            # Crear resultados de error
            error_results = {
                "execution_summary": {
                    "success": False,
                    "error": str(e),
                    "total_pings": 0,
                    "total_pongs": 0,
                    "start_time": datetime.now().isoformat(),
                    "end_time": datetime.now().isoformat()
                },
                "orchestration": {
                    "error": True,
                    "error_details": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            return error_results
        
        finally:
            # 7. Cleanup automático
            print("🧹 Ejecutando cleanup final...")
            process_manager.cleanup()
            print("✅ Orquestador finalizado")
    
    # =================================================================
    # EJECUCIÓN PRINCIPAL DEL COMPONENTE
    # =================================================================
    try:
        print("🎯 Iniciando sistema SPADE Ping-Pong embebido...")
        
        # Ejecutar el orquestador completo
        results = asyncio.run(main_orchestrator())
        
        # Crear archivo de texto para el artifact
        success = results.get("execution_summary", {}).get("success", False)
        total_pings = results.get("execution_summary", {}).get("total_pings", 0)
        total_pongs = results.get("execution_summary", {}).get("total_pongs", 0)
        duration = results.get("orchestration", {}).get("duration_seconds", 0)
        error = results.get("execution_summary", {}).get("error", None)
        
        status_text = f"""SPADE Ping-Pong System Results (Embebido)
==============================================
Overall Test Success: {success}

Ping-Pong Communication:
- Messages Sent (Ping): {total_pings}
- Messages Received (Pong): {total_pongs}
- Communication Success: {total_pings == total_pongs}
- Expected Messages: {max_pings}

System Performance:
- Total Duration: {duration:.2f} seconds
- XMPP Server Port: {results.get('orchestration', {}).get('xmpp_port', 'Unknown')}
- System Error: {error or 'None'}

Agent Statistics:
- Ping Agent Status: {results.get('agent_statistics', {}).get('ping_agent', {}).get('status', 'Unknown')}
- Pong Agent Status: {results.get('agent_statistics', {}).get('pong_agent', {}).get('status', 'Unknown')}
- Message History Count: {len(results.get('message_history', []))}

Timestamp: {results.get('execution_summary', {}).get('end_time', 'Unknown')}

🎯 RESULTADO FINAL: {'✅ SUCCESS' if success else '❌ FAILED'}

==== DETAILED RESULTS (JSON) ====
{json.dumps(results, indent=2)}
"""
        
        # Guardar el resultado en el artifact de Kubeflow
        with open(results_output.path, 'w') as f:
            f.write(status_text)
        
        print(f"📋 Resultado del sistema: {'✅ EXITOSO' if success else '❌ FALLÓ'}")
        print(f"💾 Resultados guardados en artifact: {results_output.path}")
        
        # También crear un JSON con datos detallados en /output (para compatibilidad)
        output_dir = Path("/output")
        output_dir.mkdir(exist_ok=True)
        
        json_file = output_dir / "spade_ping_pong_results.json"
        with open(json_file, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"📊 Datos detallados en: {json_file}")
        
    except Exception as e:
        print(f"💥 Error fatal en componente embebido: {e}")
        import traceback
        traceback.print_exc()
        
        # Crear archivo de error para el artifact
        error_text = f"""SPADE Ping-Pong System Results (Embebido)
==============================================
Overall Test Success: False

FATAL ERROR: {str(e)}

Timestamp: {datetime.now().isoformat()}

🎯 RESULTADO FINAL: ❌ FAILED

Traceback:
{traceback.format_exc()}
"""
        
        with open(results_output.path, 'w') as f:
            f.write(error_text)
        
        # Re-raise para que Kubeflow marque el componente como fallado
        raise
    
    return None

@dsl.pipeline(
    name='spade-ping-pong-embedded-pipeline',
    description='Sistema multi-agente SPADE Ping-Pong con código completamente embebido'
)
def spade_ping_pong_embedded_pipeline(
    max_pings: int = 10,
    ping_interval: int = 2
):
    """
    Pipeline embebido que ejecuta un sistema completo de agentes SPADE
    
    VERSIÓN EMBEBIDA: Todo el código del orchestrator y agentes está 
    integrado directamente en el componente Kubeflow para compatibilidad 
    total con Vertex AI.
    
    El pipeline incluye:
    1. Servidor XMPP integrado (spade run)
    2. PingAgent - Envía mensajes ping periódicamente  
    3. PongAgent - Responde con mensajes pong
    4. Recopilación de estadísticas y resultados completos
    5. Cleanup automático de procesos

    Args:
        max_pings: Número de mensajes ping a intercambiar
        ping_interval: Segundos entre cada ping (actualmente no usado)
    """
    
    # Ejecutar sistema SPADE embebido
    spade_task = spade_ping_pong_embedded_task(
        max_pings=max_pings,
        ping_interval=ping_interval
    )
    
    # Configuración del componente
    spade_task.set_display_name('SPADE Ping-Pong System (Embebido)')
    spade_task.set_cpu_limit('2')
    spade_task.set_memory_limit('1Gi')
    
    # Añadir descripción detallada
    spade_task.description = (
        "Ejecuta un sistema multi-agente completo usando SPADE framework con código embebido. "
        "Incluye servidor XMPP integrado y dos agentes que intercambian mensajes. "
        "Versión optimizada para Vertex AI con toda la lógica embebida en el componente."
    )