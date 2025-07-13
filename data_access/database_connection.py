"""
USO:
    # Crear conexión (Singleton)
    db = DatabaseConnection()
    
    # Usar context manager para operaciones
    with db.get_cursor() as cursor:
        cursor.execute("SELECT * FROM jugadores")
        results = cursor.fetchall()
    
    # Cerrar conexión al finalizar
    db.close_connection()
"""

# =============================================================================
# IMPORTS - Importaciones necesarias para la gestión de BD
# =============================================================================
import sqlite3
from typing import Optional
from contextlib import contextmanager


# =============================================================================
# CLASE DATABASE CONNECTION - Patrón Singleton para conexión a BD
# =============================================================================
class DatabaseConnection:
    """
    Clase singleton para manejar la conexión a la base de datos SQLite.
    
    Esta clase implementa el patrón Singleton para garantizar que solo
    exista una instancia de conexión a la base de datos en toda la aplicación.
    
    CARACTERÍSTICAS:
    - Singleton: Solo una instancia por aplicación
    - Lazy Loading: Conexión se crea solo cuando se necesita
    - Thread Safe: Manejo seguro en entornos multi-hilo
    - Context Manager: Uso seguro con 'with'
    
    EJEMPLO:
        db = DatabaseConnection()
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM jugadores")
    """
    
    # Variables de clase para implementar Singleton
    _instance: Optional['DatabaseConnection'] = None
    _connection: Optional[sqlite3.Connection] = None
    
    def __new__(cls, database_path: str = "juego_cartas.db"):
        """
        Constructor del Singleton - garantiza una sola instancia.
        
        Este método se ejecuta antes de __init__ y verifica si ya existe
        una instancia de la clase. Si no existe, crea una nueva.
        
        Args:
            database_path: Ruta al archivo de base de datos SQLite
        
        Returns:
            DatabaseConnection: La única instancia de la clase
        
        EJEMPLO:
            db1 = DatabaseConnection()  # Primera instancia
            db2 = DatabaseConnection()  # Misma instancia que db1
            assert db1 is db2  # True - es la misma instancia
        """
        if cls._instance is None:
            # Crear nueva instancia si no existe
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.database_path = database_path
        return cls._instance
    
    def __init__(self, database_path: str = "juego_cartas.db"):
        """
        Inicializador de la instancia (solo se ejecuta una vez).
        
        Args:
            database_path: Ruta al archivo de base de datos SQLite
        """
        # Solo inicializar si no se ha hecho antes (Singleton)
        if not hasattr(self, 'database_path'):
            self.database_path = database_path
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Obtiene una conexión a la base de datos (Lazy Loading).
        
        Si la conexión no existe, la crea. Si ya existe, la retorna.
        Esto implementa el patrón Lazy Loading para optimizar recursos.
        
        Returns:
            sqlite3.Connection: Conexión activa a la base de datos
        
        EJEMPLO:
            conn = db.get_connection()
            cursor = conn.cursor()
        """
        if self._connection is None:
            # Crear nueva conexión si no existe
            self._connection = sqlite3.connect(self.database_path)
            # Configurar para retornar filas como diccionarios
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def close_connection(self):
        """
        Cierra la conexión a la base de datos de forma segura.
        
        Este método debe llamarse al finalizar la aplicación para
        liberar recursos y asegurar que los datos se guarden correctamente.
        
        EJEMPLO:
            db.close_connection()  # Cerrar al finalizar
        """
        if self._connection:
            self._connection.close()
            self._connection = None
    
    @contextmanager
    def get_cursor(self):
        """
        Context manager para obtener un cursor de la base de datos.
        
        Este método proporciona un manejo seguro de transacciones:
        - Abre automáticamente un cursor
        - Hace commit si todo va bien
        - Hace rollback si hay errores
        - Cierra el cursor automáticamente
        
        Yields:
            sqlite3.Cursor: Cursor para ejecutar consultas
        
        EJEMPLO:
            with db.get_cursor() as cursor:
                cursor.execute("INSERT INTO jugadores (nombre) VALUES (?)", ("Juan",))
                # Commit automático al salir del 'with'
        
        EJEMPLO CON ERROR:
            with db.get_cursor() as cursor:
                cursor.execute("INSERT INTO tabla_inexistente VALUES (1)")
                # Rollback automático si hay error
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Retornar cursor para uso en el context manager
            yield cursor
            # Si llegamos aquí, no hubo errores - hacer commit
            conn.commit()
        except Exception as e:
            # Si hay error - hacer rollback para deshacer cambios
            conn.rollback()
            raise e
        finally:
            # Siempre cerrar el cursor
            cursor.close()
    
    def initialize_database(self):
        """
        Inicializa la base de datos con las tablas necesarias.
        
        Este método crea todas las tablas del sistema si no existen:
        - jugadores: Almacena información de jugadores
        - cartas: Almacena todas las cartas del juego
        - mazos: Relaciona jugadores con sus cartas
        - historial_partidas: Registra resultados de partidas
        
        También carga datos iniciales:
        - Cartas del juego con sus propiedades
        - Jugadores iniciales del torneo
        - Mazos balanceados para cada jugador
        
        EJEMPLO:
            db = DatabaseConnection()
            db.initialize_database()  # Crear tablas y datos iniciales
        """
        with self.get_cursor() as cursor:
            # =================================================================
            # CREAR TABLA DE JUGADORES
            # =================================================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jugadores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    victorias INTEGER DEFAULT 0,
                    derrotas INTEGER DEFAULT 0
                )
            """)
            
            # =================================================================
            # CREAR TABLA DE CARTAS
            # =================================================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cartas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    tipo TEXT NOT NULL,
                    poder INTEGER NOT NULL
                )
            """)
            
            # =================================================================
            # CREAR TABLA DE MAZOS (RELACIÓN JUGADOR-CARTA)
            # =================================================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mazos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jugador_id INTEGER NOT NULL,
                    carta_id INTEGER NOT NULL,
                    FOREIGN KEY (jugador_id) REFERENCES jugadores(id),
                    FOREIGN KEY (carta_id) REFERENCES cartas(id)
                )
            """)
            
            # =================================================================
            # CARGAR CARTAS INICIALES DEL JUEGO
            # =================================================================
            cartas = [
                ("Fuego Infernal", "Fuego", 5),
                ("Llama Doble", "Fuego", 3),
                ("Tsunami", "Agua", 4),
                ("Escudo de Agua", "Agua", 2),
                ("Golem de Tierra", "Tierra", 4),
                ("Viento Cortante", "Aire", 3),
                ("Tormenta Eléctrica", "Rayo", 6),
                ("Sombra del Vacío", "Oscuridad", 5)
            ]
            
            # Insertar cartas evitando duplicados
            cursor.executemany("""
                INSERT OR IGNORE INTO cartas (nombre, tipo, poder) VALUES (?, ?, ?)
            """, cartas)
            
            # =================================================================
            # CARGAR JUGADORES INICIALES
            # =================================================================
            jugadores = ["Jugador 1", "Jugador 2"]
            for nombre in jugadores:
                cursor.execute("INSERT OR IGNORE INTO jugadores (nombre) VALUES (?)", (nombre,))
            
            # =================================================================
            # ASIGNAR MAZOS INICIALES A JUGADORES
            # =================================================================
            self._asignar_mazos_iniciales(cursor)
    
    def _asignar_mazos_iniciales(self, cursor):
        """
        Asigna mazos iniciales a los jugadores con cartas aleatorias.
        
        Este método privado:
        1. Obtiene todos los jugadores de la base de datos
        2. Obtiene todas las cartas disponibles
        3. Asigna 4 cartas aleatorias a cada jugador
        4. Evita duplicados en la misma partida
        
        Args:
            cursor: Cursor activo para ejecutar consultas
        
        EJEMPLO:
            # Se llama internamente desde initialize_database()
            # No se debe llamar directamente
        """
        import random
        
        # Obtener IDs de jugadores
        cursor.execute("SELECT id, nombre FROM jugadores")
        jugadores_info = cursor.fetchall()
        
        # Obtener IDs de cartas
        cursor.execute("SELECT id, nombre FROM cartas")
        cartas_info = cursor.fetchall()
        
        # Asignar 4 cartas al azar a cada jugador
        for jugador_id, nombre in jugadores_info:
            # Seleccionar 4 cartas diferentes para este jugador
            cartas_seleccionadas = random.sample(cartas_info, 4)
            for carta_id, carta_nombre in cartas_seleccionadas:
                cursor.execute("""
                    INSERT OR IGNORE INTO mazos (jugador_id, carta_id) VALUES (?, ?)
                """, (jugador_id, carta_id)) 