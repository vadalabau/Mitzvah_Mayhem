Mitzvah_Mayhem/
│
├── business_logic/
│ └── game_engine.py # Motor del juego, procesos e hilos
│
├── data_access/
│ ├── database_connection.py # Singleton para conexión a BD
│ └── repositories.py # Repositorios de acceso a datos
│
├── database/
│ └── models.py # Modelos de datos (Carta, Jugador, Mazo, ResultadoPartida)
│
├── juego_cartas.db # Base de datos SQLite
├── main_optimized.py # Aplicación principal (menú, flujo de usuario)
└── test_procesos.py # (Opcional) Pruebas de procesos/hilos

## Control de Concurrencia

- **Procesos**:
  - `ProcesoArbitro`: Coordina la partida y crea 5 hilos de jugadores.
  - `ProcesoReiniciarMazos`: Reinicia los mazos de los jugadores.
  - `ProcesoLimpiarEstadisticas`: Limpia las estadísticas de los jugadores.
- **Hilos**:
  - Cada jugador es un hilo (`JugadorThread`) que juega su turno de forma sincronizada.
- **Sincronización**:
  - `threading.Lock`: Protege el acceso concurrente a los mazos.
  - `threading.Event`: Controla el turno de cada jugador.
  - `queue.Queue` y `multiprocessing.Queue`: Comunicación segura entre hilos y procesos.

---

## Cómo ejecutar

1. **Instala Python 3.8+** y asegúrate de tener `sqlite3` disponible.
2. **Inicializa la base de datos** (opcional, si no existe):
   ```bash
   python juego_cartas.py
   ```
3. **Ejecuta la aplicación principal**:
   ```bash
   python main_optimized.py
   ```
4. **Sigue el menú interactivo** para jugar partidas, ver estadísticas, reiniciar mazos o limpiar estadísticas.

---

## Ejemplo de uso

$ python main_optimized.py
🎮 JUEGO DE CARTAS - VERSIÓN OPTIMIZADA
Jugar una partida
Ver estadísticas
Reiniciar mazos
Limpiar estadísticas
Salir
Selecciona una opción (1-5): 1
🎯 Iniciando partida entre 5 jugadores...
...
🏆 GANADOR: Jugador 3
💀 PERDEDOR: Jugador 2

--

## Créditos

- Desarrollado por: Bautista Vadalá, Geremias Romero, Matias Barqui
- Inspirado en prácticas de arquitectura limpia y concurrencia en Python de Alan Uzal (Te amo).

## Agradecimientos

- Alan Uzal por enseñar estos conceptos.
- Matias Joel Sesto como beta tester.
