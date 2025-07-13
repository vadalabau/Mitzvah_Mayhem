"""
Modelos de datos para el juego de cartas
========================================

Este archivo define todas las entidades principales del sistema de torneo de cartas.
Cada modelo representa una tabla en la base de datos y contiene la lógica básica
para manipular los datos.

ARQUITECTURA:
- Usa dataclasses para definir modelos de forma clara y concisa
- Incluye métodos útiles para cada entidad
- Mantiene la separación entre datos y lógica de negocio
- Facilita el acceso a datos desde otras capas del sistema

MODELOS DEFINIDOS:
1. Carta - Representa una carta del juego con sus propiedades
2. Jugador - Representa un jugador del torneo
3. Mazo - Representa el conjunto de cartas de un jugador
4. ResultadoPartida - Representa el resultado de una partida
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Carta:
    """
    Modelo que representa una carta del juego con todas sus propiedades.
    
    ATRIBUTOS:
        id: Identificador único de la carta en la base de datos
        nombre: Nombre de la carta (ej: "Fuego Infernal")
        tipo: Tipo elemental de la carta (Fuego, Agua, Tierra, Aire, Rayo, Oscuridad)
        poder: Poder de ataque/defensa de la carta (2-10 puntos)
    
    EJEMPLO:
        Carta(id=1, nombre="Fuego Infernal", tipo="Fuego", poder=8)
    """
    id: Optional[int]          # ID único de la carta (None si es nueva)
    nombre: str                # Nombre descriptivo de la carta
    tipo: str                  # Tipo elemental (Fuego, Agua, Tierra, etc.)
    poder: int                 # Poder de la carta (2-10 puntos)

    def __str__(self):
        """
        Retorna una representación en string de la carta.
        
        Returns:
            str: Formato "Nombre (Tipo, Poder)"
        
        Ejemplo:
            "Fuego Infernal (Fuego, 8)"
        """
        return f"{self.nombre} ({self.tipo}, {self.poder})"

@dataclass
class Jugador:
    """
    Modelo que representa un jugador del torneo con sus estadísticas.
    
    ATRIBUTOS:
        id: Identificador único del jugador en la base de datos
        nombre: Nombre del jugador (ej: "Jugador 1")
        victorias: Número total de victorias del jugador
        derrotas: Número total de derrotas del jugador
    
    EJEMPLO:
        Jugador(id=1, nombre="Jugador 1", victorias=5, derrotas=2)
    """
    id: Optional[int]          # ID único del jugador (None si es nuevo)
    nombre: str                # Nombre del jugador
    victorias: int = 0         # Contador de victorias (default: 0)
    derrotas: int = 0          # Contador de derrotas (default: 0)

    def __str__(self):
        """
        Retorna una representación en string del jugador con estadísticas.
        
        Returns:
            str: Formato "Nombre (V: victorias, D: derrotas)"
        
        Ejemplo:
            "Jugador 1 (V: 5, D: 2)"
        """
        return f"{self.nombre} (V: {self.victorias}, D: {self.derrotas})"

@dataclass
class Mazo:
    """
    Modelo que representa el mazo de cartas de un jugador.
    
    Un mazo contiene exactamente 4 cartas que el jugador puede usar
    durante la partida. Las cartas se van gastando conforme se juegan.
    
    ATRIBUTOS:
        jugador_id: ID del jugador propietario del mazo
        cartas: Lista de cartas en el mazo (máximo 4)
    
    EJEMPLO:
        Mazo(jugador_id=1, cartas=[carta1, carta2, carta3, carta4])
    """
    jugador_id: int            # ID del jugador propietario del mazo
    cartas: List[Carta]        # Lista de cartas en el mazo

    def __len__(self):
        """
        Retorna el número de cartas en el mazo.
        
        Returns:
            int: Número de cartas restantes
        
        Ejemplo:
            len(mazo) -> 3  # Si quedan 3 cartas
        """
        return len(self.cartas)

    def esta_vacio(self):
        """
        Verifica si el mazo no tiene cartas.
        
        Returns:
            bool: True si el mazo está vacío, False si tiene cartas
        
        Ejemplo:
            mazo.esta_vacio() -> True  # Si no quedan cartas
        """
        return len(self.cartas) == 0

    def tomar_carta(self) -> Optional[Carta]:
        """
        Toma y retorna la primera carta del mazo (la elimina del mazo).
        
        Este método simula el acto de jugar una carta. La carta se
        retorna y se elimina del mazo para que no se pueda usar de nuevo.
        
        Returns:
            Carta: La primera carta del mazo, o None si está vacío
        
        Ejemplo:
            carta = mazo.tomar_carta()  # Toma la primera carta
            if carta:
                print(f"Jugando: {carta}")
        """
        return self.cartas.pop(0) if self.cartas else None

    def agregar_carta(self, carta: Carta):
        """
        Agrega una carta al final del mazo.
        
        Este método se usa principalmente para construir el mazo inicial
        o para agregar cartas ganadas durante el juego.
        
        Args:
            carta: La carta a agregar al mazo
        
        Ejemplo:
            nueva_carta = Carta(id=5, nombre="Rayo", tipo="Rayo", poder=6)
            mazo.agregar_carta(nueva_carta)
        """
        self.cartas.append(carta)

@dataclass
class ResultadoPartida:
    """
    Modelo que representa el resultado final de una partida de torneo.
    
    Este modelo encapsula toda la información relevante sobre el resultado
    de una partida, incluyendo ganador, perdedor y cartas jugadas.
    
    ATRIBUTOS:
        ganador: Nombre del jugador ganador
        perdedor: Nombre del jugador perdedor (último lugar)
        cartas_jugadas: Lista de tuplas (jugador, carta) que se jugaron
    
    EJEMPLO:
        ResultadoPartida(
            ganador="Jugador 3",
            perdedor="Jugador 4", 
            cartas_jugadas=[("Jugador 1", carta1), ("Jugador 2", carta2)]
        )
    """
    ganador: str               # Nombre del jugador ganador
    perdedor: str              # Nombre del jugador perdedor
    cartas_jugadas: List[tuple]  # Lista de tuplas (jugador, carta) jugadas 