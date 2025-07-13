"""
Motor del juego - Lógica de negocio principal con Hilos y Procesos
Maneja las reglas del juego y la coordinación entre jugadores usando threading
"""
import threading
import multiprocessing
import random
import time
import queue
from typing import List, Dict, Optional, Tuple
from database.models import Carta, Jugador, Mazo, ResultadoPartida
from data_access.repositories import JugadorRepository, MazoRepository

class JugadorThread(threading.Thread):
    """Hilo que representa a un jugador durante la partida"""
    
    def __init__(self, nombre: str, mazo: Mazo, turno_event: threading.Event, 
                 resultado_queue: queue.Queue, lock_compartido: threading.Lock, jugador_id: int):
        super().__init__()
        self.nombre = nombre
        self.mazo = mazo
        self.turno_event = turno_event
        self.resultado_queue = resultado_queue
        self.lock_compartido = lock_compartido
        self.jugador_id = jugador_id
        self.activo = True
        
    def run(self):
        """Ejecuta el hilo del jugador"""
        print(f"🎮 {self.nombre} (Hilo {self.jugador_id}) se ha unido a la partida")
        
        while self.activo and not self.mazo.esta_vacio():
            try:
                # Esperar mi turno
                print(f"⏳ {self.nombre} esperando su turno...")
                self.turno_event.wait()
                
                if not self.activo or self.mazo.esta_vacio():
                    break
                
                # Simular tiempo de pensamiento
                tiempo_pensamiento = random.uniform(1.0, 2.0)
                print(f"🧠 {self.nombre} pensando por {tiempo_pensamiento:.1f}s...")
                time.sleep(tiempo_pensamiento)
                
                # Jugar carta
                carta = self.jugar_carta()
                if carta:
                    self.resultado_queue.put((self.nombre, carta, self.jugador_id))
                    print(f"  {self.nombre} juega: {carta}")
                
                # Señalar que terminé mi turno
                self.turno_event.clear()
                
            except Exception as e:
                print(f"❌ Error en hilo de {self.nombre}: {e}")
                break
        
        print(f"👋 {self.nombre} ha terminado su participación")
    
    def jugar_carta(self) -> Optional[Carta]:
        """Juega una carta del mazo"""
        with self.lock_compartido:
            if not self.mazo.esta_vacio():
                return self.mazo.tomar_carta()
        return None
    
    def terminar(self):
        """Termina el hilo del jugador"""
        self.activo = False
        self.turno_event.set()


class ProcesoArbitro(multiprocessing.Process):
    """Proceso árbitro que coordina la partida"""
    
    def __init__(self, jugadores_data: List[Dict], resultado_queue: multiprocessing.Queue):
        super().__init__()
        self.jugadores_data = jugadores_data
        self.resultado_queue = resultado_queue
        
    def run(self):
        """Ejecuta el proceso árbitro"""
        print(f"🏆 Proceso árbitro iniciado (PID: {self.pid})")
        
        # Crear cola para comunicación entre hilos
        resultado_queue_thread = queue.Queue()
        lock_compartido = threading.Lock()
        
        # Crear eventos de turno para cada jugador
        turno_events = [threading.Event() for _ in range(5)]
        
        # Crear hilos de jugadores (5 hilos)
        jugadores_threads = []
        nombres = ["Jugador 1", "Jugador 2", "Jugador 3", "Jugador 4", "Jugador 5"]
        
        for i in range(5):
            jugador_thread = JugadorThread(
                nombre=nombres[i],
                mazo=self.jugadores_data[i]['mazo'],
                turno_event=turno_events[i],
                resultado_queue=resultado_queue_thread,
                lock_compartido=lock_compartido,
                jugador_id=i
            )
            jugadores_threads.append(jugador_thread)
        
        # Iniciar hilos
        for jugador_thread in jugadores_threads:
            jugador_thread.start()
        
        # Ejecutar partida de 3 rondas
        resultado = self._ejecutar_partida_5_jugadores(jugadores_threads, resultado_queue_thread, turno_events)
        
        # Terminar hilos
        for jugador_thread in jugadores_threads:
            jugador_thread.terminar()
            jugador_thread.join()
        
        # Enviar resultado al proceso principal
        self.resultado_queue.put(resultado)
        print(f"🏆 Proceso árbitro terminado (PID: {self.pid})")
    
    def _ejecutar_partida_5_jugadores(self, jugadores_threads: List[JugadorThread], 
                                    resultado_queue: queue.Queue, 
                                    turno_events: List[threading.Event]) -> Dict:
        """Ejecuta la partida con 5 jugadores - 3 rondas"""
        cartas_jugadas = []
        ronda = 1
        rondas_maximas = 3
        
        print(f"🎯 Partida de {rondas_maximas} rondas con 5 jugadores")
        
        while ronda <= rondas_maximas and len([j for j in jugadores_threads if j.activo and not j.mazo.esta_vacio()]) > 1:
            print(f"\n🔄 Ronda {ronda} de {rondas_maximas}")
            
            jugadores_activos = [j for j in jugadores_threads if j.activo and not j.mazo.esta_vacio()]
            
            if not jugadores_activos:
                print("⚠️ No hay jugadores activos")
                break
            
            # Recolectar cartas jugadas en esta ronda
            cartas_ronda = []
            
            for i, jugador_thread in enumerate(jugadores_activos):
                try:
                    # Activar turno del jugador
                    print(f"🎯 Turno de {jugador_thread.nombre}")
                    turno_events[jugador_thread.jugador_id].set()
                    
                    # Esperar carta con timeout
                    nombre, carta, jugador_id = resultado_queue.get(timeout=10.0)
                    cartas_ronda.append((nombre, carta))
                    
                except queue.Empty:
                    print("⚠️ Timeout esperando carta de jugador")
                    break
            
            # Determinar ganador de la ronda
            if cartas_ronda:
                ganador_ronda = self._determinar_ganador_ronda(cartas_ronda)
                cartas_jugadas.extend(cartas_ronda)
                print(f"  🏆 Ganador de la ronda: {ganador_ronda}")
                
                # Mostrar cartas restantes
                for jugador_thread in jugadores_threads:
                    if jugador_thread.activo:
                        cartas_restantes = len(jugador_thread.mazo.cartas)
                        print(f"  📊 {jugador_thread.nombre}: {cartas_restantes} cartas restantes")
            
            ronda += 1
            time.sleep(1)  # Pausa para visualización
        
        print(f"\n🏁 Partida terminada después de {ronda-1} rondas")
        
        # Determinar ranking final de todos los jugadores
        ranking_jugadores = self._determinar_ranking_final(jugadores_threads)
        
        ganador = ranking_jugadores[0]  # Primer lugar
        perdedor = ranking_jugadores[-1]  # Último lugar
        
        print(f"🏆 Ganador: {ganador}")
        print(f"🥈 Segundo: {ranking_jugadores[1] if len(ranking_jugadores) > 1 else 'N/A'}")
        print(f"🥉 Tercero: {ranking_jugadores[2] if len(ranking_jugadores) > 2 else 'N/A'}")
        print(f"📊 Cuarto: {ranking_jugadores[3] if len(ranking_jugadores) > 3 else 'N/A'}")
        print(f"💀 Último: {perdedor}")
        
        return {
            'ganador': ganador,
            'perdedor': perdedor,
            'ranking_completo': ranking_jugadores,
            'cartas_jugadas': cartas_jugadas,
            'rondas_jugadas': ronda - 1
        }
    
    def _determinar_ganador_ronda(self, cartas_ronda: List[tuple]) -> str:
        """Determina el ganador de una ronda basado en el poder de las cartas"""
        if not cartas_ronda:
            return ""
        cartas_validas = [(nombre, carta) for nombre, carta in cartas_ronda if carta is not None]
        if not cartas_validas:
            return ""
        max_poder = max(carta.poder for _, carta in cartas_validas)
        ganadores = [nombre for nombre, carta in cartas_validas if carta.poder == max_poder]
        return random.choice(ganadores)
    
    def _determinar_ranking_final(self, jugadores_threads: List[JugadorThread]) -> List[str]:
        """Determina el ranking final de todos los jugadores basado en cartas restantes y poder"""
        jugadores_con_poder = []
        
        for jugador in jugadores_threads:
            cartas_restantes = len(jugador.mazo.cartas) if jugador.mazo.cartas else 0
            poder_total = sum(carta.poder for carta in jugador.mazo.cartas) if jugador.mazo.cartas else 0
            
            jugadores_con_poder.append({
                'nombre': jugador.nombre,
                'cartas_restantes': cartas_restantes,
                'poder_total': poder_total,
                'puntuacion': cartas_restantes * 10 + poder_total  # Priorizar cartas restantes
            })
        
        # Ordenar por puntuación (mayor a menor)
        jugadores_con_poder.sort(key=lambda x: x['puntuacion'], reverse=True)
        
        # Mostrar ranking detallado
        print("\n📊 RANKING FINAL:")
        for i, jugador in enumerate(jugadores_con_poder):
            posicion = i + 1
            emoji = "🏆" if posicion == 1 else "🥈" if posicion == 2 else "🥉" if posicion == 3 else "📊" if posicion == 4 else "💀"
            print(f"  {emoji} {posicion}º: {jugador['nombre']} - {jugador['cartas_restantes']} cartas, {jugador['poder_total']} poder")
        
        return [jugador['nombre'] for jugador in jugadores_con_poder]





class GameEngine:
    """Motor principal del juego que coordina las partidas usando procesos e hilos"""
    
    def __init__(self):
        self.jugador_repo = JugadorRepository()
        self.mazo_repo = MazoRepository()
        self.lock = threading.Lock()
    
    def iniciar_partida(self, nombres_jugadores: List[str]) -> ResultadoPartida:
        """Inicia y ejecuta una partida completa usando 3 procesos y 5 hilos"""
        # Reiniciar mazos antes de iniciar la partida
        print("🔄 Reiniciando mazos para nueva partida...")
        self.reiniciar_mazos(nombres_jugadores)
        
        # Validar que todos los jugadores existan y tengan mazos
        jugadores_mazos = self._validar_jugadores(nombres_jugadores)
        if not jugadores_mazos:
            raise ValueError("No se pueden iniciar la partida: jugadores inválidos")
        
        print(f"🎮 Iniciando partida entre: {', '.join(nombres_jugadores)}")
        print("🚀 Usando 3 procesos y 5 hilos...")
        
        # Crear colas para comunicación entre procesos
        resultado_queue = multiprocessing.Queue()
        
        # Preparar datos para los procesos
        jugadores_data = [
            {'nombre': nombre, 'mazo': mazo} 
            for nombre, mazo in jugadores_mazos.items()
        ]
        
        # Crear y ejecutar el proceso árbitro
        proceso_arbitro = ProcesoArbitro(jugadores_data, resultado_queue)
        
        # Iniciar proceso
        proceso_arbitro.start()
        
        # Esperar resultado del proceso árbitro
        resultado_dict = resultado_queue.get()
        
        # Terminar proceso
        proceso_arbitro.join()
        
        # Convertir resultado a formato esperado
        resultado = ResultadoPartida(
            ganador=resultado_dict['ganador'],
            perdedor=resultado_dict['perdedor'],
            cartas_jugadas=resultado_dict['cartas_jugadas']
        )
        
        # Actualizar estadísticas directamente usando repositorios
        self._actualizar_estadisticas_ranking(resultado_dict['ranking_completo'])
        
        return resultado
    
    def _validar_jugadores(self, nombres: List[str]) -> Dict[str, Mazo]:
        """Valida que todos los jugadores existan y tengan mazos válidos, creando los faltantes"""
        jugadores_mazos = {}
        
        for nombre in nombres:
            # Crear el jugador si no existe
            jugador = self.jugador_repo.obtener_por_nombre(nombre)
            if not jugador:
                jugador = self.jugador_repo.crear_jugador(nombre)
                print(f"✅ Jugador {nombre} creado con ID: {jugador.id}")
            
            # Obtener el mazo del jugador (ya debería estar reiniciado)
            mazo = self.mazo_repo.obtener_mazo_jugador(nombre)
            
            if mazo and not mazo.esta_vacio():
                jugadores_mazos[nombre] = mazo
                print(f"✅ Mazo validado para {nombre}: {len(mazo.cartas)} cartas")
            else:
                print(f"❌ No se pudo obtener mazo válido para {nombre}")
                return {}
        
        return jugadores_mazos
    
    def _actualizar_estadisticas(self, ganador: str, perdedor: str):
        """Actualiza las estadísticas de los jugadores en la base de datos"""
        print(f"📊 Actualizando estadísticas: Ganador={ganador}, Perdedor={perdedor}")
        
        jugador_ganador = self.jugador_repo.obtener_por_nombre(ganador)
        jugador_perdedor = self.jugador_repo.obtener_por_nombre(perdedor)
        
        if jugador_ganador and jugador_ganador.id is not None:
            self.jugador_repo.actualizar_estadisticas(jugador_ganador.id, True)
            print(f"✅ Victoria registrada para {ganador}")
        else:
            print(f"⚠️ No se encontró jugador ganador: {ganador}")
            
        if jugador_perdedor and jugador_perdedor.id is not None:
            self.jugador_repo.actualizar_estadisticas(jugador_perdedor.id, False)
            print(f"✅ Derrota registrada para {perdedor}")
        else:
            print(f"⚠️ No se encontró jugador perdedor: {perdedor}")
    
    def _actualizar_estadisticas_ranking(self, ranking_completo: List[str]):
        """Actualiza las estadísticas de todos los jugadores según su posición en el ranking"""
        print(f"\n📊 Actualizando estadísticas para {len(ranking_completo)} jugadores...")
        
        for i, nombre_jugador in enumerate(ranking_completo):
            jugador = self.jugador_repo.obtener_por_nombre(nombre_jugador)
            if jugador and jugador.id is not None:
                # Solo el primer lugar gana, los demás pierden
                es_victoria = (i == 0)
                self.jugador_repo.actualizar_estadisticas(jugador.id, es_victoria)
                
                if es_victoria:
                    print(f"🏆 Victoria registrada para {nombre_jugador} (1º lugar)")
                else:
                    print(f"💀 Derrota registrada para {nombre_jugador} ({i+1}º lugar)")
            else:
                print(f"⚠️ No se encontró jugador: {nombre_jugador}")
        
        print("✅ Estadísticas actualizadas correctamente")
    

    
    def obtener_estadisticas(self) -> List[Jugador]:
        """Obtiene las estadísticas de todos los jugadores"""
        return self.jugador_repo.obtener_todos()
    
    def reiniciar_mazos(self, nombres_jugadores: List[str]):
        """Reinicia los mazos de los jugadores con cartas aleatorias"""
        for nombre in nombres_jugadores:
            jugador = self.jugador_repo.obtener_por_nombre(nombre)
            if jugador and jugador.id is not None:
                # Limpiar mazo actual
                self.mazo_repo.limpiar_mazo_jugador(jugador.id)
                
                # Asignar nuevas cartas aleatorias
                nuevas_cartas = self.mazo_repo.obtener_cartas_aleatorias(4)
                for carta in nuevas_cartas:
                    if carta.id is not None:
                        self.mazo_repo.asignar_carta_a_jugador(jugador.id, carta.id)
                
                print(f"🔄 Mazo reiniciado para {nombre}: {len(nuevas_cartas)} cartas")
            else:
                print(f"⚠️ No se pudo reiniciar mazo para {nombre}: jugador no encontrado")
    
    def limpiar_estadisticas(self):
        """Limpia todas las estadísticas de victorias y derrotas"""
        self.jugador_repo.limpiar_estadisticas()


class JugadorConMazo:
    """Clase auxiliar que combina un jugador con su mazo para la partida"""
    
    def __init__(self, nombre: str, mazo: Mazo):
        self.nombre = nombre
        self.mazo = mazo
    
    def __str__(self):
        return f"{self.nombre} (Cartas: {len(self.mazo)})" 