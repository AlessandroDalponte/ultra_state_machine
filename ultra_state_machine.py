from enum import Enum
from typing import Callable, Any


class ActivationRequirement(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ANY = "any"


class PreStateData:
    def __init__(self, state_id: int, active: bool, *args: Any, **kwargs: Any) -> None:
        self.state_id = state_id
        self.active = active
        self.args = args
        self.kwargs = kwargs


class State:
    def __init__(
            self,
            state_id: int,
            state_activation_threshold: int,
            state_deactivation_threshold: int,
            activations_order_and_requirements: dict[int, dict[int, ActivationRequirement]] | None = None,
            state_function: Callable | None = None,
            ) -> None:
        
        self.state_id = state_id
        self.state_activation_threshold = state_activation_threshold
        self.state_deactivation_threshold = state_deactivation_threshold
        self.state_activation_counter: int
        self.state_deactivation_counter: int
        self.activations_order_and_requirements = activations_order_and_requirements
        self.state_function = state_function
        self.active_state: bool
        self.activations_order: list[int]
        self.current_active_index: int | None
        self.next_activation_index: int | None
        self._reset_properties()


    def _reset_properties(self) -> None:                
        if self.activations_order_and_requirements is not None:
            self.activations_order = sorted(list((self.activations_order_and_requirements.keys())))
            self.current_active_index = None
            self.next_activation_index = 0
        else:
            self.current_active_index = None
            self.next_activation_index = None

        self.state_activation_counter = 0
        self.state_deactivation_counter = 0

    
    def _run_function(self, *args: Any, **kwargs: Any) -> Any:
        if self.state_function is not None:
            return self.state_function(*args, **kwargs)
        
        return None
    
    
    def _activate_state(self) -> None:
        self.active_state = True
        if self.next_activation_index is not None:
            self.current_active_index = self.next_activation_index
            
    
    def _deactivate_state(self) -> None:
        self.active_state = False
    

    def update_state(self, active: bool, *args: Any, **kwargs: Any) -> Any:
        result: Any = None

        if active and not self.active_state:
            self.state_activation_counter += 1
            if self.state_activation_counter == self.state_activation_threshold:
                self.state_activation_counter = 0
                self._activate_state()
        
        if not active and self.active_state:
            self.state_deactivation_counter += 1
            if self.state_deactivation_counter == self.state_deactivation_threshold:
                self.state_deactivation_counter = 0
                self._deactivate_state()
        
        if self.active_state:
            result = self._run_function(args=args, kwargs=kwargs)
        
        return result


    def get_next_activation_requirement(self) -> dict[int, ActivationRequirement]:
        next_activation = self.activations_order[self.next_activation_index]
        
        return self.activations_order_and_requirements[next_activation]


class UltraStateMachine:
    def __init__(
            self,
            states_and_requirements: dict[int, dict[int, dict[int, ActivationRequirement]] | None],
            states_functions: dict[int, Callable | None],
            true_initial_states: list[int] | None,
            state_activation_threshold: int,
            state_deactivation_threshold: int,
            reset_state_machine_threshold: int
            ) -> None:
        
        self.reset_state_machine_threshold = reset_state_machine_threshold
        self.states_dict = dict[int, State] = {}
        self.state_activation_order: list[int] = []
        self.current_state_activation_order_index: int
        self.reset_state_machine_counter: int
        self._generate_states(
            states_and_requirements=states_and_requirements,
            states_functions=states_functions,
            true_initial_states=true_initial_states,
            state_activation_threshold=state_activation_threshold,
            state_deactivation_threshold=state_deactivation_threshold
            )
        self._reset_state_machine()


    def _generate_states(
            self,
            states_and_requirements: dict[int, dict[int, dict[int, ActivationRequirement]] | None],
            states_functions: dict[int, Callable | None],
            true_initial_states: list[int] | None,
            state_activation_threshold: int,
            state_deactivation_threshold: int
            ) -> None:
        
        activation_order_dict: dict[int, list[int]] = {}
        
        for n, configs in states_and_requirements.items():
            initial_state = True if n in true_initial_states else False
            self.states_dict[n] = State(
                state_id=n,
                state_activation_threshold=state_activation_threshold,
                state_deactivation_threshold=state_deactivation_threshold,
                activations_order_and_requirements=configs,
                state_function=states_functions[n],
                initial_state=initial_state
                )
            for i in configs.keys():
                activation_order_dict[i] = n
        
        for n in sorted(activation_order_dict.keys()):
            self.state_activation_order.append(activation_order_dict[n])
        

    def _reset_state_machine(self) -> None:
        self.current_activation_order_index = 0
        self.reset_state_machine_counter = 0
    
    
    def _check_activation_requirements(
            self,
            activation_requirements: dict[int, ActivationRequirement],
            ) -> bool:
        
        requirements_met = True
        for id, requirement in activation_requirements.items():
            condition_1 = requirement == ActivationRequirement.ACTIVE and not self.states_dict[id].active_state
            condition_2 = requirement == ActivationRequirement.INACTIVE and self.states_dict[id].active_state
            if condition_1 or condition_2:
                requirements_met = False
                break
        
        return requirements_met
    
    
    def update_ultra_state_machine(self, pre_states_data: dict[int, PreStateData]) -> dict[int, Any]:
        results_dict: dict[int, Any] = {}
        for id, state in self.states_dict.items():
            active = False
            activation_requirements = state.get_next_activation_requirement()
            if pre_states_data[id].active:
                requirements_met = self._check_activation_requirements(activation_requirements=activation_requirements)
                if requirements_met:
                    active = True
            result = state.update_state(active=active, args=pre_states_data[id].args, kwargs=pre_states_data[id].kwargs)
            results_dict[id] = result

        return results_dict