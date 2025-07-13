"""
Repositorios para el acceso a datos
===================================

Este archivo implementa el patrón Repository para cada entidad del sistema.
Los repositorios encapsulan la lógica de acceso a datos y proporcionan
una interfaz limpia para operaciones CRUD.

PATRÓN REPOSITORY:
- Separa la lógica de acceso a datos de la lógica de negocio
- Proporciona métodos específicos para cada entidad
- Encapsula consultas SQL complejas
- Facilita testing y mantenimiento

REPOSITORIOS IMPLEMENTADOS:
1. CartaRepository - Maneja operaciones con cartas
2. JugadorRepository - Maneja operaciones con jugadores  
3. MazoRepository - Maneja operaciones con mazos

CARACTERÍSTICAS:
- Métodos CRUD completos (Create, Read, Update, Delete)
- Manejo de errores y validaciones
- Consultas optimizadas
- Transacciones seguras
"""

from typing import List, Optional
from database.models import Carta, Jugador, Mazo
from data_access.database_connection import DatabaseConnection


# =============================================================================
# REPOSITORIO DE CARTAS - Maneja operaciones con cartas del juego
# =============================================================================
class CartaRepository:
    """
    Repositorio para manejar operaciones con cartas del juego.
    
    Este repositorio proporciona métodos para:
    - Obtener todas las cartas
    - Buscar cartas por ID
    - Crear nuevas cartas
    - Obtener cartas aleatorias para mazos
    
    EJEMPLO:
        repo = CartaRepository()
        todas_cartas = repo.obtener_todas()
        carta = repo.obtener_por_id(1)
    """
    
    def __init__(self):
        """Inicializa el repositorio con una conexión a la base de datos."""
        self.db = DatabaseConnection()
    
    def obtener_todas(self) -> List[Carta]:
        """
        Obtiene todas las cartas de la base de datos.
        
        Returns:
            List[Carta]: Lista de todas las cartas disponibles
        
        EJEMPLO:
            cartas = repo.obtener_todas()
            for carta in cartas:
                print(f"{carta.nombre}: {carta.poder} poder")
        """
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT id, nombre, tipo, poder FROM cartas")
            return [Carta(row[0], row[1], row[2], row[3]) 
                   for row in cursor.fetchall()]
    
    def obtener_por_id(self, carta_id: int) -> Optional[Carta]:
        """
        Obtiene una carta específica por su ID.
        
        Args:
            carta_id: ID único de la carta a buscar
        
        Returns:
            Carta: La carta encontrada, o None si no existe
        
        EJEMPLO:
            carta = repo.obtener_por_id(5)
            if carta:
                print(f"Encontrada: {carta}")
        """
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT id, nombre, tipo, poder FROM cartas WHERE id = ?", (carta_id,))
            row = cursor.fetchone()
            return Carta(row[0], row[1], row[2], row[3]) if row else None
    
    def crear(self, carta: Carta) -> int:
        """
        Crea una nueva carta en la base de datos.
        
        Args:
            carta: Objeto Carta con los datos a insertar
        
        Returns:
            int: ID de la carta recién creada
        
        EJEMPLO:
            nueva_carta = Carta(None, "Nueva Carta", "Fuego", 7)
            id_carta = repo.crear(nueva_carta)
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO cartas (nombre, tipo, poder) VALUES (?, ?, ?)",
                (carta.nombre, carta.tipo, carta.poder)
            )
            return cursor.lastrowid or 0


# =============================================================================
# REPOSITORIO DE JUGADORES - Maneja operaciones con jugadores
# =============================================================================
class JugadorRepository:
    """
    Repositorio para manejar operaciones con jugadores del torneo.
    
    Este repositorio proporciona métodos para:
    - Obtener todos los jugadores
    - Buscar jugadores por nombre o ID
    - Crear nuevos jugadores
    - Actualizar estadísticas (victorias/derrotas)
    - Limpiar estadísticas
    
    EJEMPLO:
        repo = JugadorRepository()
        jugadores = repo.obtener_todos()
        jugador = repo.obtener_por_nombre("Jugador 1")
    """
    
    def __init__(self):
        """Inicializa el repositorio con una conexión a la base de datos."""
        self.db = DatabaseConnection()
    
    def obtener_todos(self) -> List[Jugador]:
        """
        Obtiene todos los jugadores de la base de datos.
        
        Returns:
            List[Jugador]: Lista de todos los jugadores registrados
        
        EJEMPLO:
            jugadores = repo.obtener_todos()
            for jugador in jugadores:
                print(f"{jugador.nombre}: {jugador.victorias}V/{jugador.derrotas}D")
        """
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT id, nombre, victorias, derrotas FROM jugadores")
            return [Jugador(row[0], row[1], row[2], row[3]) 
                   for row in cursor.fetchall()]
    
    def obtener_por_nombre(self, nombre: str) -> Optional[Jugador]:
        """
        Obtiene un jugador específico por su nombre.
        
        Args:
            nombre: Nombre del jugador a buscar
        
        Returns:
            Jugador: El jugador encontrado, o None si no existe
        
        EJEMPLO:
            jugador = repo.obtener_por_nombre("Jugador 1")
            if jugador:
                print(f"Encontrado: {jugador}")
        """
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT id, nombre, victorias, derrotas FROM jugadores WHERE nombre = ?", (nombre,))
            row = cursor.fetchone()
            return Jugador(row[0], row[1], row[2], row[3]) if row else None
    
    def obtener_por_id(self, jugador_id: int) -> Optional[Jugador]:
        """
        Obtiene un jugador específico por su ID.
        
        Args:
            jugador_id: ID único del jugador a buscar
        
        Returns:
            Jugador: El jugador encontrado, o None si no existe
        
        EJEMPLO:
            jugador = repo.obtener_por_id(3)
            if jugador:
                print(f"Encontrado: {jugador}")
        """
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT id, nombre, victorias, derrotas FROM jugadores WHERE id = ?", (jugador_id,))
            row = cursor.fetchone()
            return Jugador(row[0], row[1], row[2], row[3]) if row else None
    
    def crear_jugador(self, nombre: str) -> Jugador:
        """
        Crea un nuevo jugador con el nombre especificado.
        
        Args:
            nombre: Nombre del nuevo jugador
        
        Returns:
            Jugador: El jugador recién creado con ID asignado
        
        EJEMPLO:
            nuevo_jugador = repo.crear_jugador("Jugador Nuevo")
            print(f"Creado: {nuevo_jugador}")
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO jugadores (nombre, victorias, derrotas) VALUES (?, 0, 0)",
                (nombre,)
            )
            jugador_id = cursor.lastrowid or 0
            return Jugador(jugador_id, nombre, 0, 0)
    
    def crear(self, jugador: Jugador) -> int:
        """
        Crea un nuevo jugador con estadísticas específicas.
        
        Args:
            jugador: Objeto Jugador con los datos a insertar
        
        Returns:
            int: ID del jugador recién creado
        
        EJEMPLO:
            jugador = Jugador(None, "Juan", 0, 0)
            id_jugador = repo.crear(jugador)
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO jugadores (nombre, victorias, derrotas) VALUES (?, ?, ?)",
                (jugador.nombre, jugador.victorias, jugador.derrotas)
            )
            return cursor.lastrowid or 0
    
    def actualizar_estadisticas(self, jugador_id: int, victoria: bool):
        """
        Actualiza las estadísticas de un jugador (victoria o derrota).
        
        Args:
            jugador_id: ID del jugador a actualizar
            victoria: True si ganó, False si perdió
        
        EJEMPLO:
            # Registrar victoria
            repo.actualizar_estadisticas(1, True)
            
            # Registrar derrota
            repo.actualizar_estadisticas(1, False)
        """
        with self.db.get_cursor() as cursor:
            # Obtener estadísticas actuales para logging
            cursor.execute("SELECT nombre, victorias, derrotas FROM jugadores WHERE id = ?", (jugador_id,))
            jugador_actual = cursor.fetchone()
            
            # Verificar que el jugador existe
            if not jugador_actual:
                print(f"⚠️ No se encontró jugador con ID {jugador_id}")
                return
            
            if victoria:
                # Incrementar victorias
                cursor.execute(
                    "UPDATE jugadores SET victorias = victorias + 1 WHERE id = ?", 
                    (jugador_id,)
                )
                print(f"  📈 {jugador_actual[0]}: {jugador_actual[1]} → {jugador_actual[1] + 1} victorias")
            else:
                # Incrementar derrotas
                cursor.execute(
                    "UPDATE jugadores SET derrotas = derrotas + 1 WHERE id = ?", 
                    (jugador_id,)
                )
                print(f"  📉 {jugador_actual[0]}: {jugador_actual[2]} → {jugador_actual[2] + 1} derrotas")
    
    def limpiar_estadisticas(self):
        """
        Limpia todas las estadísticas de victorias y derrotas de todos los jugadores.
        
        Este método resetea los contadores a 0 pero mantiene los jugadores registrados.
        
        EJEMPLO:
            repo.limpiar_estadisticas()  # Resetear todas las estadísticas
        """
        with self.db.get_cursor() as cursor:
            cursor.execute("UPDATE jugadores SET victorias = 0, derrotas = 0")
            print("🧹 Estadísticas limpiadas")


# =============================================================================
# REPOSITORIO DE MAZOS - Maneja operaciones con mazos de jugadores
# =============================================================================
class MazoRepository:
    """
    Repositorio para manejar operaciones con mazos de cartas de jugadores.
    
    Este repositorio proporciona métodos para:
    - Obtener mazos completos de jugadores
    - Asignar cartas a jugadores
    - Limpiar mazos de jugadores
    - Obtener cartas aleatorias para mazos
    
    EJEMPLO:
        repo = MazoRepository()
        mazo = repo.obtener_mazo_jugador("Jugador 1")
        repo.asignar_carta_a_jugador(1, 5)
    """
    
    def __init__(self):
        """Inicializa el repositorio con conexiones a otros repositorios."""
        self.db = DatabaseConnection()
        self.carta_repo = CartaRepository()
        self.jugador_repo = JugadorRepository()
    
    def obtener_mazo_jugador(self, nombre_jugador: str) -> Optional[Mazo]:
        """
        Obtiene el mazo completo de un jugador.
        
        Args:
            nombre_jugador: Nombre del jugador cuyo mazo se quiere obtener
        
        Returns:
            Mazo: El mazo del jugador con todas sus cartas, o None si no existe
        
        EJEMPLO:
            mazo = repo.obtener_mazo_jugador("Jugador 1")
            if mazo:
                print(f"Mazo de {len(mazo.cartas)} cartas")
        """
        # Obtener el jugador por nombre
        jugador = self.jugador_repo.obtener_por_nombre(nombre_jugador)
        if not jugador:
            return None
        
        # Obtener todas las cartas del mazo del jugador
        with self.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT c.id, c.nombre, c.tipo, c.poder 
                FROM cartas c
                JOIN mazos m ON c.id = m.carta_id
                WHERE m.jugador_id = ?
                ORDER BY m.id
            """, (jugador.id,))
            
            cartas = [Carta(row[0], row[1], row[2], row[3]) 
                     for row in cursor.fetchall()]
            
            return Mazo(jugador.id or 0, cartas)
    
    def asignar_carta_a_jugador(self, jugador_id: int, carta_id: int):
        """
        Asigna una carta específica a un jugador.
        
        Args:
            jugador_id: ID del jugador que recibirá la carta
            carta_id: ID de la carta a asignar
        
        EJEMPLO:
            repo.asignar_carta_a_jugador(1, 5)  # Asignar carta 5 al jugador 1
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO mazos (jugador_id, carta_id) VALUES (?, ?)",
                (jugador_id, carta_id)
            )
    
    def limpiar_mazo_jugador(self, jugador_id: int):
        """
        Elimina todas las cartas del mazo de un jugador.
        
        Args:
            jugador_id: ID del jugador cuyo mazo se limpiará
        
        EJEMPLO:
            repo.limpiar_mazo_jugador(1)  # Limpiar mazo del jugador 1
        """
        with self.db.get_cursor() as cursor:
            cursor.execute("DELETE FROM mazos WHERE jugador_id = ?", (jugador_id,))
    
    def obtener_cartas_aleatorias(self, cantidad: int) -> List[Carta]:
        """
        Obtiene una cantidad aleatoria de cartas para asignar a mazos.
        
        Args:
            cantidad: Número de cartas aleatorias a obtener
        
        Returns:
            List[Carta]: Lista de cartas aleatorias
        
        EJEMPLO:
            cartas = repo.obtener_cartas_aleatorias(4)  # Obtener 4 cartas aleatorias
            for carta in cartas:
                print(f"Carta: {carta}")
        """
        import random
        # Obtener todas las cartas disponibles
        todas_cartas = self.carta_repo.obtener_todas()
        # Retornar una muestra aleatoria del tamaño especificado
        return random.sample(todas_cartas, min(cantidad, len(todas_cartas))) 