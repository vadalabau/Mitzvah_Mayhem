🎮 Juego de Cartas - Sistema de Torneo (Arquitectura 3 Capas)
Un sistema de torneo de cartas con arquitectura profesional, patrones de diseño y concurrencia real en Python.
Arquitectura
  Capa de Base de Datos (database/): Modelos de datos (@dataclass)
  Capa de Acceso a Datos (data_access/): Repositorios y conexión a SQLite
  Capa de Lógica de Negocio (business_logic/): Motor del juego y reglas

Concurrencia
  1 Proceso: Árbitro (coordinador de la partida)
  5 Hilos: Uno por cada jugador
  Sincronización: threading.Event para turnos
  Comunicación: Queue para paso de mensajes seguro
  
Características
  5 jugadores, 3 rondas, ranking final
  6 tipos de cartas (Fuego, Agua, Tierra, Aire, Rayo, Oscuridad)
  Mazos balanceados y asignación automática
  Estadísticas persistentes (victorias/derrotas)
  Reinicio de mazos y limpieza de estadísticas
  Menú interactivo en consola
  
Instalación y Uso
  Requisitos
  Python 3.8+
  No requiere dependencias externas

Estructura del Proyecto
  Mitzvah Mayhem/
  ├── business_logic/
  │   └── game_engine.py
  ├── data_access/
  │   ├── database_connection.py
  │   └── repositories.py
  ├── database/
  │   └── models.py
  ├── juego_cartas.py
  ├── main_optimized.py
  ├── test_procesos.py
  ├── juego_cartas.db
  └── README.md

Ejemplo de Uso
  Ejecuta el menú y elige "1. Jugar una partida"
  El sistema simula el torneo y muestra el ranking
  Consulta estadísticas con la opción 2
  Reinicia mazos o limpia estadísticas según desees
  
Alumnos
  Vadala Bautista
  Geremias Romero
  Matias Barqui
