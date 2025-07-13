# 🃏 Juego de Cartas - Sistema de Torneo
Un sistema completo de torneo de cartas implementado con **Arquitectura de 3 Capas**, **concurrencia avanzada** y **patrones de diseño** modernos.

## Características Principales

### Arquitectura Robusta
- **Arquitectura de 3 Capas**: Separación clara de responsabilidades
- **Patrón Repository**: Acceso a datos encapsulado y reutilizable
- **Context Managers**: Manejo seguro de recursos

### Concurrencia Avanzada
- **3 Procesos**: Principal, Árbitro, Base de Datos
- **5 Hilos**: Uno por cada jugador del torneo
- **Sincronización**: Events y Locks para coordinación
- **Comunicación**: Queues para intercambio de datos seguro

### Sistema de Juego Completo
- **5 Jugadores**: Torneo multijugador
- **3 Rondas**: Partidas dinámicas y emocionantes
- **Mazos Balanceados**: Distribución equitativa de cartas
- **Estadísticas**: Seguimiento completo de victorias/derrotas

### Cartas Elementales
- **6 Tipos**: Fuego, Agua, Tierra, Aire, Rayo, Oscuridad
- **Poder Variable**: Cartas de 2-10 puntos de poder
- **Rarezas**: Común, Raro, Épico
- **Balance**: Sistema equilibrado para competencia justa

## Estructura del Proyecto

```
juego-cartas/
├── 📂 database/
│   ├── __init__.py
│   └── models.py              # Modelos de datos (Carta, Jugador, Mazo)
├── 📂 data_access/
│   ├── __init__.py
│   ├── database_connection.py # Conexión Singleton a BD
│   └── repositories.py        # Repositorios CRUD
├── 📂 business_logic/
│   ├── __init__.py
│   └── game_engine.py         # Motor del juego y concurrencia
├──  main_optimized.py       # Aplicación principal
├──  juego_cartas.py         # Inicializador de BD
├──  juego_cartas.db         # Base de datos SQLite
└── README.md               # Este archivo
```

## Instalación y Configuración

### Prerrequisitos
- Python 3.8 o superior
- SQLite3 (incluido con Python)

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/juego-cartas.git
   cd juego-cartas
   ```

2. **Inicializar la base de datos**
   ```bash
   python juego_cartas.py
   ```

3. **Ejecutar el juego**
   ```bash
   python main_optimized.py
   ```

## Cómo Jugar

### Iniciar una Partida
1. Ejecuta `python main_optimized.py`
2. Selecciona opción **1. Jugar una partida**
3. El sistema automáticamente:
   - Inicia 3 procesos y 5 hilos
   - Coordina 3 rondas de juego
   - Determina el ganador final
   - Actualiza estadísticas

### Ver Estadísticas
- Selecciona opción **2. Ver estadísticas**
- Visualiza victorias, derrotas y porcentajes
- Ranking de jugadores

### Reiniciar Mazos
- Selecciona opción **3. Reiniciar mazos**
- Asigna nuevas cartas aleatorias a todos los jugadores

## Arquitectura Técnica

### Capa de Base de Datos (`database/`)
```python
# Modelos principales
Carta(id, nombre, tipo, poder)
Jugador(id, nombre, victorias, derrotas)
Mazo(jugador_id, cartas)
ResultadoPartida(ganador, perdedor, cartas_jugadas)
```

### Capa de Acceso a Datos (`data_access/`)
```python
# Patrón Singleton
DatabaseConnection()  # Conexión única a BD

# Patrón Repository
CartaRepository()     # Operaciones CRUD de cartas
JugadorRepository()   # Operaciones CRUD de jugadores
MazoRepository()      # Operaciones CRUD de mazos
```

### Capa de Lógica de Negocio (`business_logic/`)
```python
# Motor principal
GameEngine()          # Coordina toda la lógica del juego

# Concurrencia
JugadorThread()       # Hilo por jugador
ProcesoArbitro()      # Proceso coordinador
```

## Flujo de Concurrencia

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Proceso        │    │  Proceso        │    │  Proceso        │
│  Principal      │    │  Árbitro        │    │  Base de Datos  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
              ┌─────▼─────┐ ┌────▼────┐ ┌────▼────┐
              │ Hilo      │ │ Hilo    │ │ Hilo    │
              │ Jugador 1 │ │ Jugador │ │ Jugador │
              └───────────┘ │    2    │ │    3    │
                           └─────────┘ └─────────┘
```

## Reglas del Juego

### Mecánica Básica
- **5 jugadores** compiten en un torneo
- Cada jugador tiene un **mazo de 4 cartas**
- Se juegan **3 rondas** por partida
- En cada ronda, todos juegan una carta simultáneamente
- La carta con **mayor poder** gana la ronda

### Sistema de Poder
- **Cartas de Fuego**: 3-10 poder (agresivas)
- **Cartas de Agua**: 2-7 poder (versátiles)
- **Cartas de Tierra**: 3-9 poder (defensivas)
- **Cartas de Aire**: 3-7 poder (rápidas)
- **Cartas de Rayo**: 4-9 poder (críticas)
- **Cartas de Oscuridad**: 4-8 poder (misteriosas)

### Determinación del Ganador
1. **Cartas restantes**: Prioridad principal
2. **Poder total**: Desempate por poder acumulado
3. **Aleatoriedad**: En caso de empate total

## Características Técnicas

### Patrones de Diseño Implementados
- ✅ **Singleton**: Conexión única a base de datos
- ✅ **Repository**: Acceso encapsulado a datos
- ✅ **Context Manager**: Manejo seguro de recursos

### Conceptos de Concurrencia
- ✅ **Threading**: 5 hilos para jugadores
- ✅ **Multiprocessing**: 3 procesos principales
- ✅ **Synchronization**: Events y Locks
- ✅ **Inter-Process Communication**: Queues

### Base de Datos
- ✅ **SQLite**: Base de datos ligera y portable
- ✅ **Transacciones**: ACID compliance
- ✅ **Foreign Keys**: Integridad referencial
- ✅ **Migrations**: Actualización automática de esquema

## Testing y Validación

### Verificación de Integridad
```bash
# Verificar estructura de BD
python -c "from juego_cartas import DatabaseInitializer; DatabaseInitializer().verify_database_integrity()"
```

### Pruebas de Concurrencia
- El sistema maneja automáticamente:
  - Timeouts de jugadores
  - Errores de sincronización
  - Recuperación de procesos fallidos

## Optimizaciones Implementadas

###Rendimiento
- **Lazy Loading**: Conexión a BD solo cuando se necesita
- **Connection Pooling**: Reutilización de conexiones
- **Batch Operations**: Operaciones en lote para BD

###Escalabilidad
- **Arquitectura Modular**: Fácil extensión
- **Separación de Responsabilidades**: Mantenimiento simplificado
- **Configuración Externa**: Parámetros ajustables

## Solución de Problemas

### Error: "Base de datos no encontrada"
```bash
python juego_cartas.py  # Inicializar BD
```

### Error: "Jugadores no encontrados"
```bash
# Verificar que la BD esté inicializada
python -c "from data_access.database_connection import DatabaseConnection; db = DatabaseConnection(); db.initialize_database()"
```

### Error: "Timeout en concurrencia"
- El sistema maneja automáticamente timeouts
- Los jugadores inactivos son eliminados de la partida

##Roadmap

### Próximas Características
- [ ] **Interfaz Gráfica**: GUI con tkinter o PyQt
- [ ] **Red Multiplayer**: Soporte para jugadores remotos
- [ ] **Más Tipos de Cartas**: Expansión del sistema elemental
- [ ] **Torneos Personalizados**: Configuración de reglas
- [ ] **API REST**: Servicio web para integración

##Agradecimientos

- Python Community 
- SQLite Team
- Alan Uzal
