"""
Juego de Cartas - Versión Optimizada con Arquitectura de 3 Capas
===============================================================

Este archivo es la aplicación principal que ejecuta el sistema de torneo de cartas.

ARQUITECTURA IMPLEMENTADA:
- Capa de Base de Datos (database/): Modelos de datos
- Capa de Acceso a Datos (data_access/): Repositorios y conexión a BD
- Capa de Lógica de Negocio (business_logic/): Motor del juego

CONCEPTOS DE CONCURRENCIA:
- 3 procesos: Principal, Árbitro, Base de Datos
- 5 hilos: Uno por cada jugador
- Sincronización con threading.Events
- Comunicación segura con Queue

CARACTERÍSTICAS:
- Separación clara de responsabilidades
- Patrón Repository para acceso a datos
- Lógica de negocio centralizada
- Mejor manejo de errores y transacciones
- Conceptos básicos de hilos y procesos
"""
    
# =============================================================================
# IMPORTS - Importaciones necesarias para el funcionamiento
# =============================================================================
import multiprocessing
from data_access.database_connection import DatabaseConnection
from business_logic.game_engine import GameEngine
from database.models import Jugador


# =============================================================================
# FUNCIONES DE INTERFAZ DE USUARIO
# =============================================================================

def mostrar_menu():
    """
    Muestra el menú principal del juego con todas las opciones disponibles.
    
    Este menú permite al usuario:
    - Jugar una partida de torneo
    - Ver estadísticas de jugadores
    - Reiniciar mazos de cartas
    - Limpiar estadísticas
    - Salir del juego
    """
    print("\n" + "="*50)
    print("🎮 JUEGO DE CARTAS - VERSIÓN OPTIMIZADA")
    print("="*50)
    print("1. Jugar una partida")
    print("2. Ver estadísticas")
    print("3. Reiniciar mazos")
    print("4. Limpiar estadísticas")
    print("5. Salir")
    print("-"*50)


def mostrar_estadisticas(engine: GameEngine):
    """
    Muestra las estadísticas detalladas de todos los jugadores.
    
    Calcula y muestra:
    - Número de victorias y derrotas
    - Total de partidas jugadas
    - Porcentaje de victoria
    - Ranking de jugadores
    
    Args:
        engine: Instancia del motor del juego que contiene la lógica de negocio
    """
    print("\n📊 ESTADÍSTICAS DE JUGADORES")
    print("-"*30)
    
    # Obtener estadísticas desde la base de datos
    jugadores = engine.obtener_estadisticas()
    if not jugadores:
        print("No hay jugadores registrados.")
        return
    
    # Mostrar estadísticas de cada jugador
    for jugador in jugadores:
        # Calcular total de partidas y porcentaje de victoria
        total_partidas = jugador.victorias + jugador.derrotas
        porcentaje_victoria = (jugador.victorias / total_partidas * 100) if total_partidas > 0 else 0
        
        # Mostrar información formateada
        print(f"{jugador.nombre}:")
        print(f"  Victorias: {jugador.victorias}")
        print(f"  Derrotas: {jugador.derrotas}")
        print(f"  Total partidas: {total_partidas}")
        print(f"  Porcentaje victoria: {porcentaje_victoria:.1f}%")
        print()


# =============================================================================
# FUNCIONES DE LÓGICA DE JUEGO
# =============================================================================

def jugar_partida(engine: GameEngine):
    """
    Ejecuta una partida completa del torneo con 5 jugadores.
    
    Esta función:
    1. Inicia el sistema de concurrencia (3 procesos + 5 hilos)
    2. Coordina la partida de 3 rondas
    3. Determina el ranking final
    4. Actualiza estadísticas en la base de datos
    5. Muestra el resultado del torneo
    
    Args:
        engine: Instancia del motor del juego
    """
    # Lista de jugadores que participarán en el torneo
    nombres_jugadores = ["Jugador 1", "Jugador 2", "Jugador 3", "Jugador 4", "Jugador 5"]
    
    try:
        # Informar inicio de la partida
        print(f"\n🎯 Iniciando partida entre {len(nombres_jugadores)} jugadores...")
        print(f"👥 Jugadores: {', '.join(nombres_jugadores)}")
        
        # Iniciar la partida usando el motor del juego
        # Esto activará el sistema de concurrencia completo
        resultado = engine.iniciar_partida(nombres_jugadores)
        
        # Mostrar resultado final del torneo
        print("\n" + "🏁"*20)
        print("RESULTADO FINAL")
        print("🏁"*20)
        print(f"🏆 GANADOR: {resultado.ganador}")
        print(f"💀 PERDEDOR: {resultado.perdedor}")
        print(f"📝 Cartas jugadas: {len(resultado.cartas_jugadas)}")
        print(f"👥 Participantes: {', '.join(['Jugador 1', 'Jugador 2', 'Jugador 3', 'Jugador 4', 'Jugador 5'])}")
        
    except ValueError as e:
        # Error de validación (jugadores inválidos, mazos vacíos, etc.)
        print(f"❌ Error: {e}")
    except Exception as e:
        # Error inesperado del sistema
        print(f"❌ Error inesperado: {e}")


def reiniciar_mazos(engine: GameEngine):
    """
    Reinicia los mazos de todos los jugadores con nuevas cartas aleatorias.
    
    Esta función:
    1. Limpia los mazos actuales de todos los jugadores
    2. Asigna 4 cartas aleatorias a cada jugador
    3. Garantiza que los mazos estén balanceados
    
    Args:
        engine: Instancia del motor del juego
    """
    # Lista de jugadores cuyos mazos serán reiniciados
    nombres_jugadores = ["Jugador 1", "Jugador 2", "Jugador 3", "Jugador 4", "Jugador 5"]
    
    try:
        print("\n🔄 Reiniciando mazos...")
        # Llamar al método del motor para reiniciar mazos
        engine.reiniciar_mazos(nombres_jugadores)
        print("✅ Mazos reiniciados exitosamente")
    except Exception as e:
        print(f"❌ Error al reiniciar mazos: {e}")


def limpiar_estadisticas(engine: GameEngine):
    """
    Limpia todas las estadísticas de victorias y derrotas de todos los jugadores.
    
    Esta función resetea:
    - Contador de victorias a 0
    - Contador de derrotas a 0
    - Mantiene los jugadores registrados
    
    Args:
        engine: Instancia del motor del juego
    """
    try:
        print("\n🧹 Limpiando estadísticas...")
        # Llamar al método del motor para limpiar estadísticas
        engine.limpiar_estadisticas()
        print("✅ Estadísticas limpiadas exitosamente")
    except Exception as e:
        print(f"❌ Error al limpiar estadísticas: {e}")


# =============================================================================
# FUNCIÓN PRINCIPAL - Punto de entrada de la aplicación
# =============================================================================

def main():
    """
    Función principal que inicializa y ejecuta el sistema de torneo de cartas.
    
    FLUJO DE EJECUCIÓN:
    1. Inicializar la base de datos
    2. Crear el motor del juego
    3. Mostrar menú principal en bucle
    4. Procesar opciones del usuario
    5. Cerrar conexión a la base de datos al salir
    """
    print("🚀 Inicializando Juego de Cartas...")
    
    # =========================================================================
    # INICIALIZACIÓN DE LA BASE DE DATOS
    # =========================================================================
    try:
        # Crear conexión a la base de datos usando patrón Singleton
        db_connection = DatabaseConnection()
        # Inicializar tablas y datos necesarios
        db_connection.initialize_database()
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
        return
    
    # =========================================================================
    # CREACIÓN DEL MOTOR DEL JUEGO
    # =========================================================================
    # Crear instancia del motor que maneja toda la lógica de negocio
    engine = GameEngine()
    
    # =========================================================================
    # BUCLE PRINCIPAL DE LA APLICACIÓN
    # =========================================================================
    while True:
        try:
            # Mostrar menú de opciones
            mostrar_menu()
            
            # Obtener selección del usuario
            opcion = input("Selecciona una opción (1-5): ").strip()
            
            # Procesar la opción seleccionada
            if opcion == "1":
                # Iniciar una partida de torneo
                jugar_partida(engine)
            elif opcion == "2":
                # Mostrar estadísticas de jugadores
                mostrar_estadisticas(engine)
            elif opcion == "3":
                # Reiniciar mazos de cartas
                reiniciar_mazos(engine)
            elif opcion == "4":
                # Limpiar estadísticas
                limpiar_estadisticas(engine)
            elif opcion == "5":
                # Salir del juego
                print("\n👋 ¡Gracias por jugar! ¡Hasta luego!")
                break
            else:
                # Opción inválida
                print("❌ Opción inválida. Por favor, selecciona 1-5.")
                
        except KeyboardInterrupt:
            # Manejar interrupción del usuario (Ctrl+C)
            print("\n\n👋 ¡Juego interrumpido! ¡Hasta luego!")
            break
        except Exception as e:
            # Manejar errores inesperados
            print(f"❌ Error inesperado: {e}")
    
    # =========================================================================
    # LIMPIEZA Y CIERRE
    # =========================================================================
    # Cerrar conexión a la base de datos de forma segura
    try:
        db_connection.close_connection()
        print("✅ Conexión a la base de datos cerrada")
    except:
        pass

if __name__ == "__main__":
    main() 