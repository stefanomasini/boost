from collections import namedtuple


class CommandTurn(namedtuple('CommandTurn', 'direction target to speed')):
    def execute(self, execution_context):
        motor = execution_context.get_symbol(self.target)
        motor.turn(self.direction, self.to, self.speed)

        execution_context.advance_pc()
        return False  # Non blocking - continue executing following commands


class CommandTimeFromStart(namedtuple('CommandTimeFromStart', 'millis')):
    def execute(self, execution_context):
        execution_context.schedule_next_execution_at_time(self.millis)
        execution_context.advance_pc()
        return True  # Blocking - stop executing other commands


class CommandTimeJump(namedtuple('CommandTimeJump', 'millis')):
    def execute(self, execution_context):
        execution_context.schedule_next_execution_in_ms(self.millis)
        execution_context.advance_pc()
        return True  # Blocking - stop executing other commands


class CommandFunctionCall(namedtuple('CommandFunctionCall', 'function_name params')):
    def execute(self, execution_context):
        function = execution_context.functions[self.function_name]
        symbol_mapping = []
        if function.parameter and len(self.params) > 0:
            symbol_mapping.append( (function.parameter, self.params[0]) )
        execution_context.advance_pc()
        execution_context.push_scope(function.commands, symbol_mapping)
        return False  # Non blocking - continue executing following commands
