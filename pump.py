class Pump:
    def __init__(self, id: str, pin: int, pump_rate: float, description: str):
            self._id: str = id
            self._pin: int = pin
            self._pump_rate: float = pump_rate
            self._description: str = description
            
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

    #Getter for description
    @property
    def description(self) -> str:
            return self._description
        