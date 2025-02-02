class Pump:
    """Class for creating a Pump object"""
    def __init__(self, id: str, pin: int, pump_rate: float):
            self._id: str = id
            self._pin: int = pin
            self._pump_rate: float = pump_rate
            
    # Getter for id
    @property
    def id(self) -> str:
            return self._id

    # Getter for pin
    @property
    def pin(self) -> int: 
            return self._pin

    # Getter for pumprate
    @property
    def pump_rate(self) -> float:
            return self._pump_rate        