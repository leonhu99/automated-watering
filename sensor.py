class Sensor:
    def __init__(self, id: str, description: str, dry_value: int, wet_value: int, last_value: int = 0):
            self._id: str = id
            self._description: str = description
            self._dry_value: int = dry_value
            self._wet_value: int = wet_value
            self._interval_size: int = round((self.dry_value - self._wet_value)/3)
            self.__last_value: int = last_value
            
    # Getter for id
    @property
    def id(self) -> str:
            return self._id

    # Getter for description
    @property
    def description(self) -> str:
            return self._description

    # Getter for dry value
    @property
    def dry_value(self) -> int:
           return self._dry_value

    # Getter for wet value
    @property
    def wet_value(self) -> int:
           return self._wet_value
    
    # Getter for interval size
    @property
    def interval_size(self) -> int:
           return self._interval_size
    
    # Getter for last value
    @property
    def last_value(self) -> int:
           return self.__last_value
    
    # Setter for last value
    @last_value.setter
    def last_value(self, new_value: int) -> None:
           self.__last_value = new_value
    