#!/usr/bin/env python3
"""
Test de los 3 Procesos - Sistema de Juego de Cartas
==================================================

Este archivo demuestra cómo funcionan los 3 procesos:
1. ProcesoArbitro - Coordina la partida
2. ProcesoBaseDatos - Maneja operaciones de BD
3. ProcesoJugadores - Maneja la lógica de jugadores

Cada proceso es independiente y se comunica a través de colas.
"""

import multiprocessing
import time
from business_logic.game_engine import ProcesoArbitro, ProcesoBaseDatos, ProcesoJugadores

def test_procesos():
    """Prueba los 3 procesos funcionando juntos"""
    print("🧪 TEST DE LOS 3 PROCESOS")
    print("=" * 50)
    
    # Crear colas para comunicación
    resultado_queue = multiprocessing.Queue()
    operaciones_bd_queue = multiprocessing.Queue()
    resultados_bd_queue = multiprocessing.Queue()
    acciones_jugadores_queue = multiprocessing.Queue()
    resultados_jugadores_queue = multiprocessing.Queue()
    
    # Datos de prueba para jugadores
    jugadores_data = [
        {'nombre': 'Jugador 1', 'mazo': []},
        {'nombre': 'Jugador 2', 'mazo': []},
        {'nombre': 'Jugador 3', 'mazo': []},
        {'nombre': 'Jugador 4', 'mazo': []},
        {'nombre': 'Jugador 5', 'mazo': []}
    ]
    
    print("🚀 Creando los 3 procesos...")
    
    # Crear los 3 procesos
    proceso_bd = ProcesoBaseDatos(operaciones_bd_queue, resultados_bd_queue)
    proceso_jugadores = ProcesoJugadores(jugadores_data, acciones_jugadores_queue, resultados_jugadores_queue)
    proceso_arbitro = ProcesoArbitro(jugadores_data, resultado_queue)
    
    print("▶️ Iniciando procesos...")
    
    # Iniciar procesos
    proceso_bd.start()
    proceso_jugadores.start()
    proceso_arbitro.start()
    
    print("⏳ Esperando resultados...")
    
    # Esperar resultado del árbitro
    resultado = resultado_queue.get()
    
    print("\n📊 RESULTADO DE LA PARTIDA:")
    print(f"🏆 Ganador: {resultado['ganador']}")
    print(f"💀 Último: {resultado['perdedor']}")
    print(f"🃏 Cartas jugadas: {len(resultado['cartas_jugadas'])}")
    print(f"🔄 Rondas: {resultado['rondas_jugadas']}")
    
    print("\n📋 Ranking completo:")
    for i, jugador in enumerate(resultado['ranking_completo']):
        print(f"  {i+1}º: {jugador}")
    
    # Terminar procesos
    print("\n🛑 Terminando procesos...")
    operaciones_bd_queue.put({'tipo': 'terminar'})
    acciones_jugadores_queue.put({'tipo': 'terminar'})
    
    # Esperar a que terminen
    proceso_arbitro.join()
    proceso_jugadores.join()
    proceso_bd.join()
    
    print("✅ Todos los procesos terminados correctamente")
    print("🎉 Test completado exitosamente!")

if __name__ == "__main__":
    # Configurar multiprocessing para Windows
    multiprocessing.set_start_method('spawn', force=True)
    test_procesos() 