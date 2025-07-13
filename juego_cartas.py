"""
Juego de Cartas - Sistema de Torneo con Arquitectura de 3 Capas

"""
import sqlite3
import random
from typing import List, Tuple, Dict
from contextlib import contextmanager

class DatabaseInitializer:
    """Clase para inicializar y configurar la base de datos del juego"""
    
    def __init__(self, database_path: str = "juego_cartas.db"):
        self.database_path = database_path
        self.conn = None
        self.cursor = None
    
    def __enter__(self):
        """Context manager para manejar la conexión"""
        self.conn = sqlite3.connect(self.database_path)
        self.cursor = self.conn.cursor()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra la conexión de forma segura"""
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()
    
    def create_tables(self):
        """Crea todas las tablas necesarias para el juego"""
        print("🏗️ Creando estructura de base de datos...")
        
        if not self.cursor:
            raise RuntimeError("Cursor no inicializado")
        
        # Verificar si la base de datos ya existe y necesita migración
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cartas'")
        tabla_cartas_existe = self.cursor.fetchone() is not None
        
        if tabla_cartas_existe:
            print("🔄 Base de datos existente detectada. Verificando estructura...")
            self._migrate_database()
        else:
            print("🆕 Creando nueva base de datos...")
            self._create_new_database()
        
        print("✅ Estructura de base de datos actualizada")
    
    def _create_new_database(self):
        """Crea una nueva base de datos con la estructura completa"""
        if not self.cursor:
            raise RuntimeError("Cursor no inicializado")
        
        # Tabla de jugadores
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS jugadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                victorias INTEGER DEFAULT 0,
                derrotas INTEGER DEFAULT 0,
                fecha_creacion TEXT DEFAULT (datetime('now'))
            )
        """)
        
        # Tabla de cartas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cartas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                tipo TEXT NOT NULL,
                poder INTEGER NOT NULL,
                rareza TEXT DEFAULT 'Común',
                descripcion TEXT
            )
        """)
        
        # Tabla de mazos (relación jugador-carta)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS mazos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jugador_id INTEGER NOT NULL,
                carta_id INTEGER NOT NULL,
                fecha_asignacion TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (jugador_id) REFERENCES jugadores(id) ON DELETE CASCADE,
                FOREIGN KEY (carta_id) REFERENCES cartas(id) ON DELETE CASCADE
            )
        """)
        
        # Tabla de historial de partidas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_partidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ganador_id INTEGER NOT NULL,
                perdedor_id INTEGER NOT NULL,
                cartas_jugadas INTEGER DEFAULT 0,
                rondas_jugadas INTEGER DEFAULT 0,
                fecha_partida TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (ganador_id) REFERENCES jugadores(id),
                FOREIGN KEY (perdedor_id) REFERENCES jugadores(id)
            )
        """)
    
    def _migrate_database(self):
        """Migra la base de datos existente a la nueva estructura"""
        print("🔄 Migrando base de datos existente...")
        
        if not self.cursor:
            raise RuntimeError("Cursor no inicializado")
        
        # Verificar columnas existentes en tabla cartas
        self.cursor.execute("PRAGMA table_info(cartas)")
        columnas_cartas = [col[1] for col in self.cursor.fetchall()]
        
        # Agregar columnas faltantes a la tabla cartas
        if 'rareza' not in columnas_cartas:
            print("  ➕ Agregando columna 'rareza' a tabla cartas...")
            self.cursor.execute("ALTER TABLE cartas ADD COLUMN rareza TEXT DEFAULT 'Común'")
        
        if 'descripcion' not in columnas_cartas:
            print("  ➕ Agregando columna 'descripcion' a tabla cartas...")
            self.cursor.execute("ALTER TABLE cartas ADD COLUMN descripcion TEXT")
        
        # Verificar columnas existentes en tabla jugadores
        self.cursor.execute("PRAGMA table_info(jugadores)")
        columnas_jugadores = [col[1] for col in self.cursor.fetchall()]
        
        if 'fecha_creacion' not in columnas_jugadores:
            print("  ➕ Agregando columna 'fecha_creacion' a tabla jugadores...")
            self.cursor.execute("ALTER TABLE jugadores ADD COLUMN fecha_creacion TEXT")
            # Actualizar registros existentes con timestamp actual
            self.cursor.execute("UPDATE jugadores SET fecha_creacion = datetime('now') WHERE fecha_creacion IS NULL")
        
        # Verificar columnas existentes en tabla mazos
        self.cursor.execute("PRAGMA table_info(mazos)")
        columnas_mazos = [col[1] for col in self.cursor.fetchall()]
        
        if 'fecha_asignacion' not in columnas_mazos:
            print("  ➕ Agregando columna 'fecha_asignacion' a tabla mazos...")
            self.cursor.execute("ALTER TABLE mazos ADD COLUMN fecha_asignacion TEXT")
            # Actualizar registros existentes con timestamp actual
            self.cursor.execute("UPDATE mazos SET fecha_asignacion = datetime('now') WHERE fecha_asignacion IS NULL")
        
        # Crear tabla de historial si no existe
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_partidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ganador_id INTEGER NOT NULL,
                perdedor_id INTEGER NOT NULL,
                cartas_jugadas INTEGER DEFAULT 0,
                rondas_jugadas INTEGER DEFAULT 0,
                fecha_partida TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (ganador_id) REFERENCES jugadores(id),
                FOREIGN KEY (perdedor_id) REFERENCES jugadores(id)
            )
        """)
        
        print("✅ Migración completada")
    
    def load_cards(self):
        """Carga las cartas iniciales del juego con balance mejorado"""
        print("🃏 Cargando cartas del juego...")
        
        if not self.cursor:
            raise RuntimeError("Cursor no inicializado")
        
        # Cartas mejoradas con mejor balance y variedad
        cartas = [
            # Cartas de Fuego (poder alto, agresivas)
            ("Fuego Infernal", "Fuego", 8, "Raro", "Llama destructiva que arrasa todo"),
            ("Llama Doble", "Fuego", 5, "Común", "Dos ataques de fuego simultáneos"),
            ("Explosión Volcánica", "Fuego", 10, "Épico", "Erupción devastadora"),
            ("Chispa Ardiente", "Fuego", 3, "Común", "Pequeña pero efectiva"),
            
            # Cartas de Agua (versátiles, defensivas)
            ("Tsunami", "Agua", 7, "Raro", "Ola gigante que arrastra enemigos"),
            ("Escudo de Agua", "Agua", 4, "Común", "Protección líquida"),
            ("Tormenta Marina", "Agua", 6, "Raro", "Tempestad oceánica"),
            ("Gota Helada", "Agua", 2, "Común", "Congela al oponente"),
            
            # Cartas de Tierra (defensivas, resistentes)
            ("Golem de Tierra", "Tierra", 6, "Raro", "Guardián de piedra indestructible"),
            ("Muro de Piedra", "Tierra", 5, "Común", "Defensa sólida"),
            ("Terremoto", "Tierra", 9, "Épico", "Sacudida sísmica masiva"),
            ("Raíz Profunda", "Tierra", 3, "Común", "Ancla natural"),
            
            # Cartas de Aire (rápidas, evasivas)
            ("Viento Cortante", "Aire", 4, "Común", "Corte invisible del viento"),
            ("Tornado", "Aire", 7, "Raro", "Vórtice destructivo"),
            ("Ráfaga Veloz", "Aire", 3, "Común", "Ataque rápido como el viento"),
            ("Escudo de Viento", "Aire", 4, "Común", "Barrera de aire"),
            
            # Cartas de Rayo (críticas, poderosas)
            ("Tormenta Eléctrica", "Rayo", 9, "Épico", "Descarga eléctrica masiva"),
            ("Rayo Directo", "Rayo", 6, "Raro", "Impacto eléctrico preciso"),
            ("Chispa Eléctrica", "Rayo", 4, "Común", "Descarga menor"),
            
            # Cartas de Oscuridad (misteriosas, poderosas)
            ("Sombra del Vacío", "Oscuridad", 8, "Épico", "Poder de las tinieblas"),
            ("Drenaje de Vida", "Oscuridad", 7, "Raro", "Absorbe energía vital"),
            ("Portal Oscuro", "Oscuridad", 5, "Raro", "Abre un portal a la oscuridad"),
            ("Garra de Sombra", "Oscuridad", 4, "Común", "Ataque desde las sombras")
        ]
        
        # Insertar o actualizar cartas
        for nombre, tipo, poder, rareza, descripcion in cartas:
            # Verificar si la carta ya existe
            self.cursor.execute("SELECT id FROM cartas WHERE nombre = ?", (nombre,))
            carta_existente = self.cursor.fetchone()
            
            if carta_existente:
                # Actualizar carta existente con nuevos campos
                self.cursor.execute("""
                    UPDATE cartas SET tipo = ?, poder = ?, rareza = ?, descripcion = ?
                    WHERE nombre = ?
                """, (tipo, poder, rareza, descripcion, nombre))
            else:
                # Insertar nueva carta
                self.cursor.execute("""
                    INSERT INTO cartas (nombre, tipo, poder, rareza, descripcion) 
                    VALUES (?, ?, ?, ?, ?)
                """, (nombre, tipo, poder, rareza, descripcion))
        
        # Verificar cartas insertadas
        self.cursor.execute("SELECT COUNT(*) FROM cartas")
        num_cartas = self.cursor.fetchone()[0]
        print(f"✅ {num_cartas} cartas cargadas exitosamente")
    
    def load_players(self):
        """Carga los jugadores del torneo"""
        print("👥 Cargando jugadores del torneo...")
        
        if not self.cursor:
            raise RuntimeError("Cursor no inicializado")
        
        jugadores = [
            "Jugador 1",
            "Jugador 2", 
            "Jugador 3",
            "Jugador 4",
            "Jugador 5"
        ]
        
        for nombre in jugadores:
            self.cursor.execute("""
                INSERT OR IGNORE INTO jugadores (nombre) VALUES (?)
            """, (nombre,))
        
        # Verificar jugadores insertados
        self.cursor.execute("SELECT COUNT(*) FROM jugadores")
        num_jugadores = self.cursor.fetchone()[0]
        print(f"✅ {num_jugadores} jugadores cargados exitosamente")
    
    def assign_balanced_decks(self):
        """Asigna mazos balanceados a cada jugador"""
        print("🎯 Asignando mazos balanceados...")
        
        if not self.cursor:
            raise RuntimeError("Cursor no inicializado")
        
        # Obtener todos los jugadores
        self.cursor.execute("SELECT id, nombre FROM jugadores")
        jugadores = self.cursor.fetchall()
        
        # Obtener todas las cartas
        self.cursor.execute("SELECT id, tipo, poder FROM cartas")
        cartas = self.cursor.fetchall()
        
        # Limpiar mazos existentes
        self.cursor.execute("DELETE FROM mazos")
        
        # Estrategia de asignación balanceada
        for jugador_id, nombre in jugadores:
            print(f"  🎮 Configurando mazo para {nombre}...")
            
            # Seleccionar cartas balanceadas por tipo
            mazo_balanceado = self._create_balanced_deck(cartas)
            
            # Asignar cartas al jugador
            for carta_id in mazo_balanceado:
                self.cursor.execute("""
                    INSERT INTO mazos (jugador_id, carta_id) VALUES (?, ?)
                """, (jugador_id, carta_id))
            
            print(f"    ✅ {len(mazo_balanceado)} cartas asignadas")
    
    def _create_balanced_deck(self, cartas: List[Tuple]) -> List[int]:
        """Crea un mazo balanceado con diferentes tipos de cartas"""
        # Agrupar cartas por tipo
        cartas_por_tipo = {}
        for carta_id, tipo, poder in cartas:
            if tipo not in cartas_por_tipo:
                cartas_por_tipo[tipo] = []
            cartas_por_tipo[tipo].append((carta_id, poder))
        
        # Estrategia de balance: 1 carta de cada tipo + 1 extra
        mazo = []
        tipos_disponibles = list(cartas_por_tipo.keys())
        
        # Seleccionar 1 carta de cada tipo
        for tipo in tipos_disponibles:
            if cartas_por_tipo[tipo]:
                # Seleccionar carta con poder medio del tipo
                cartas_tipo = cartas_por_tipo[tipo]
                cartas_tipo.sort(key=lambda x: x[1])  # Ordenar por poder
                carta_media = cartas_tipo[len(cartas_tipo)//2]  # Carta del medio
                mazo.append(carta_media[0])
        
        # Si no tenemos 4 cartas, agregar cartas aleatorias
        while len(mazo) < 4:
            tipo_aleatorio = random.choice(tipos_disponibles)
            if cartas_por_tipo[tipo_aleatorio]:
                carta_aleatoria = random.choice(cartas_por_tipo[tipo_aleatorio])
                if carta_aleatoria[0] not in mazo:
                    mazo.append(carta_aleatoria[0])
        
        # Asegurar exactamente 4 cartas
        return mazo[:4]
    
    def verify_database_integrity(self):
        """Verifica la integridad de la base de datos"""
        print("🔍 Verificando integridad de la base de datos...")
        
        if not self.cursor:
            raise RuntimeError("Cursor no inicializado")
        
        # Verificar que todos los jugadores tengan mazos
        self.cursor.execute("""
            SELECT j.nombre, COUNT(m.carta_id) as cartas
            FROM jugadores j
            LEFT JOIN mazos m ON j.id = m.jugador_id
            GROUP BY j.id, j.nombre
        """)
        
        jugadores_mazos = self.cursor.fetchall()
        print("\n📊 Estado de mazos por jugador:")
        for nombre, cartas in jugadores_mazos:
            estado = "✅" if cartas == 4 else "❌"
            print(f"  {estado} {nombre}: {cartas}/4 cartas")
        
        # Verificar distribución de tipos de cartas
        self.cursor.execute("""
            SELECT c.tipo, COUNT(*) as cantidad
            FROM cartas c
            JOIN mazos m ON c.id = m.carta_id
            GROUP BY c.tipo
            ORDER BY cantidad DESC
        """)
        
        distribucion = self.cursor.fetchall()
        print("\n🎯 Distribución de tipos de cartas en mazos:")
        for tipo, cantidad in distribucion:
            print(f"  {tipo}: {cantidad} cartas")
        
        # Verificar estadísticas iniciales
        self.cursor.execute("""
            SELECT nombre, victorias, derrotas
            FROM jugadores
            ORDER BY nombre
        """)
        
        estadisticas = self.cursor.fetchall()
        print("\n📈 Estadísticas iniciales:")
        for nombre, victorias, derrotas in estadisticas:
            print(f"  {nombre}: {victorias}V/{derrotas}D")
    
    def initialize_database(self):
        """Inicializa completamente la base de datos"""
        print("🚀 INICIALIZANDO SISTEMA DE TORNEO DE CARTAS")
        print("=" * 60)
        
        try:
            self.create_tables()
            self.load_cards()
            self.load_players()
            self.assign_balanced_decks()
            self.verify_database_integrity()
            
            print("\n" + "=" * 60)
            print("🎉 ¡SISTEMA INICIALIZADO EXITOSAMENTE!")
            print("=" * 60)
            print("✅ Base de datos creada y configurada")
            print("✅ Cartas balanceadas cargadas")
            print("✅ 5 jugadores registrados")
            print("✅ Mazos balanceados asignados")
            print("✅ Sistema de torneo listo")
            print("\n🎮 ¡Puedes ejecutar main_optimized.py para comenzar el torneo!")
            
        except Exception as e:
            print(f"❌ Error durante la inicialización: {e}")
            raise

def main():
    """Función principal para inicializar el sistema"""
    try:
        with DatabaseInitializer() as db_init:
            db_init.initialize_database()
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())