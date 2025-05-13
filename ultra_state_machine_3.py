from typing import Callable, Any


class State:
    def __init__(
            self,
            state_id: int,
            initialization: bool,
            state_definition: Any,
            state_function: Callable | None
            ) -> None:
        self.state_id = state_id
        self.active = initialization
        self.state_definition = state_definition
        self.state_function = state_function
    

    def activate_state(self) -> None:
        self.active = True
    

    def deactivate_state(self) -> None:
        self.active = False
    
    
    def run_state_function(self, *args, **kwargs) -> Any:
        result: Any = None
        if self.state_function is not None:
            result = self.state_function(args, kwargs=kwargs)
        
        return result
    

    def get_state_definition(self) -> Any:
        return self.state_definition


class StateTransition:
    def __init__(
            self,
            initial_state: State,
            final_state: State,
            ) -> None:
        self.initial_state = initial_state
        self.final_state = final_state


class UltraStateMachine:
    def __init__(self, states_data, states_transitions: dict[int, list[int]]) -> None:
        self.states = self._define_states(states_data=states_data)
        self.current_state: int
        self.states_transitions = self._configure_state_transitions(states_transitions=states_transitions)


    def _define_states(self, states_data) -> None:
        states: dict[int, State] = {}
        for state_id, data in states_data:
            states[state_id] = State(
                state_id=state_id,
                initialization=data["initialization"],
                state_definition=data["state_definition"],
                state_function=data["state_function"]
                )
        
        return states


    def _configure_state_transitions(self, states_transitions: dict[int, list[int]]) -> None:
        transitions: dict[int, StateTransition] = {}
        for transition_id, state_transition in states_transitions:
            initial_state = state_transition[0]
            final_state = state_transition[1]
            opposite_direction = False
            try:
                state_transition[2]
            except:
                pass
            else:
                opposite_direction = state_transition[2]
            transitions[transition_id] = StateTransition(
                initial_state=initial_state,
                final_state=final_state,
                opposite_direction=opposite_direction
                )

        return transitions


    def update_state_machine(self, signals: dict[str, bool]) -> None:
        pass