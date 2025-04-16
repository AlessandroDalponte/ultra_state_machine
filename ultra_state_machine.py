from enum import Enum
from typing import Callable, Optional, Any


class ActivationRequirement(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ANY = "any"


class State:
    def __init__(
            self,
            state_id: int,
            activation_order_and_requirements: dict[int, dict[int, ActivationRequirement]],
            state_function: Optional[Callable] = None
            ) -> None:
        
        self.state_id = state_id
        self.activation_order_and_requirements = activation_order_and_requirements
        self.state_function = state_function
        self.active_state: bool = False
        self.next_activation: int = min(self.activation_order_and_requirements.keys())
    

    def _run_function(self, *args: Any, **kwargs: Any) -> Any:
        if self.state_function is not None:
            return self.state_function(*args, **kwargs)
        
        return None
    
    
    def activate_state(self) -> None:
        self.active_state = True
    

    def deactivate_state(self) -> None:
        self.active_state = False
    

    def update_state(self, *args: Any, **kwargs: Any) -> Any:
        result = self._run_function(args=args, kwargs=kwargs)
        return result


class UltraStateMachine:
    def __init__(self) -> None:
        pass


    def update_ultra_state_machine(self, active_states_numbers: list[int]) -> None:
        pass