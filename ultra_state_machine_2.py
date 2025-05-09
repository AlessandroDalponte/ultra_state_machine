from enum import Enum
from typing import Callable, Any


class ActivationCondition(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ANY = "any"


class ActivationRequirement:
    def __init__(
            self,
            state_id: int,
            activation_condition: ActivationCondition
            ) -> None:
        
        self.state_id = state_id
        self.activation_condition = activation_condition


class State:
    def __init__(
            self,
            state_id: int,
            activation_ids_and_requirements: dict[int, list[ActivationRequirement]],
            function: Callable | None,
            activation_threshold: int,
            deactivation_threshold: int
            ) -> None:
        
        self.state_id = state_id
        self.activation_ids_and_requirements = activation_ids_and_requirements
        self.function = function
        self.activation_threshold = activation_threshold
        self.deactivation_threshold = deactivation_threshold
        self.active_state: bool
        self.activation_counter: int
        self.deactivation_counter: int
        self._reset_state()
    
    
    def _reset_state(self) -> None:
        self.active_state = False
        self.activation_counter = 0
        self.deactivation_counter = 0
    

    def _activate_state(self) -> None:
        self.active_state = True
        self.activation_counter = 0
    

    def _deactivate_state(self) -> None:
        self.active_state = False
        self.deactivation_counter = 0
    

    def _run_function(self, *args: Any, **kwargs: Any) -> Any:
        result: Any = None
        result = self.function(args, kwargs=kwargs)

        return result
    
    
    def update_state(self, signal: bool, *args: Any, **kwargs: Any) -> Any:
        result: Any = None

        if signal:
            self.deactivation_counter = 0
            if not self.active_state:
                self.activation_counter += 1
                if self.activation_counter == self.activation_threshold:
                    self._activate_state()
        
        if self.active_state:
            self._run_function(args, kwargs=kwargs)
        
        if not signal:
            self.activation_counter = 0
            if self.active_state:
                self.deactivation_counter += 1
                if self.deactivation_counter == self.deactivation_threshold:
                    self._deactivate_state()
        
        return result
    

    def get_activation_requirements(self, activation_id: int) -> list[ActivationRequirement]:
        return self.activation_ids_and_requirements[activation_id]
        

class UltraStateMachine:
    def __init__(
            self,
            states_activations_ids_and_requirements: dict[int, dict[int, list[ActivationRequirement]]],
            states_functions: dict[int, Callable | None],
            activation_threshold: int,
            deactivation_threshold: int,
            inactive_machine_reset_threshold: int,
            states_activation_order_and_activation_ids: dict[int, dict[int, int]]
            ) -> None:
        
        self.states = self._initialize_states(
            states_activations_ids_and_requirements=states_activations_ids_and_requirements,
            states_functions=states_functions,
            activation_threshold=activation_threshold,
            deactivation_threshold=deactivation_threshold
            )
        self.inactive_machine_reset_threshold = inactive_machine_reset_threshold
        self.states_activation_order_and_activation_ids = states_activation_order_and_activation_ids
        self.organized_states_activation_order = self._organize_states_activation_order()
        self.current_activation: int

    
    def _initialize_states(
            self,
            states_activations_ids_and_requirements: dict[int, dict[int, list[ActivationRequirement]]],
            states_functions: dict[int, Callable | None],
            activation_threshold: int,
            deactivation_threshold: int,
            ) -> dict[int, State]:
        
        states: dict[int, State] = {}
        for state_id, activation_ids_and_requirements in states_activations_ids_and_requirements.items():
            states[state_id] = State(
                state_id=state_id,
                activation_ids_and_requirements=activation_ids_and_requirements,
                function=states_functions[state_id],
                activation_threshold=activation_threshold,
                deactivation_threshold=deactivation_threshold
                )
        
        return states
    
    
    def _organize_states_activation_order(self) -> list[int]:
        return list(set(sorted(self.states_activation_order_and_activation_ids.keys())))
    
    
    def _reset_state_machine(self) -> None:
        self.current_activation = min(self.organized_states_activation_order)
    
    
    def _check_states_activations_requirements(self) -> None:
        pass
    
    
    def update(self, signals_for_states: dict[int, bool]) -> None:
        for state_id, signal in signals_for_states:
            pass