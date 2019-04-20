from collections import namedtuple
from functools import partial
from .language.errors import ProgramSyntaxError


TURN_TO_RANGE = (1, 64)
SPEED_RANGE = (1, 5)


class CommandTurn(namedtuple('CommandTurn', 'direction target to speed')):
    @classmethod
    def parse(cls, program_line, function_name, params_string, locals_dict, errors):
        try:
            command = eval(cls.__name__ + params_string, {cls.__name__: partial(cls, function_name)}, locals_dict)
        except Exception as err:
            errors.append(ProgramSyntaxError(program_line.line_num, 'Parsing exception: {0}'.format(err)))
            return
        if not isinstance(command.to, int):
            errors.append(ProgramSyntaxError(program_line.line_num, '"to" parameter must be an integer'))
            return
        if not (TURN_TO_RANGE[0] <= command.to <= TURN_TO_RANGE[1]):
            errors.append(ProgramSyntaxError(program_line.line_num, '"to" parameter must be in range {0}-{1}'.format(*TURN_TO_RANGE)))
            return
        if not isinstance(command.speed, int):
            errors.append(ProgramSyntaxError(program_line.line_num, '"speed" parameter must be an integer'))
            return
        if not (SPEED_RANGE[0] <= command.speed <= SPEED_RANGE[1]):
            errors.append(ProgramSyntaxError(program_line.line_num, '"speed" parameter must be in range {0}-{1}'.format(*SPEED_RANGE)))
            return
        return command

    def execute(self, execution_context):
        motor = execution_context.get_symbol(self.target)
        motor.turn(self.direction, self.to, self.speed)

        execution_context.advance_pc()
        return False  # Non blocking - continue executing following commands


class CommandStop(namedtuple('CommandStop', 'target')):
    @classmethod
    def parse(cls, program_line, function_name, params_string, locals_dict, errors):
        try:
            command = eval(cls.__name__ + params_string, {cls.__name__: cls}, locals_dict)
        except Exception as err:
            errors.append(ProgramSyntaxError(program_line.line_num, 'Parsing exception: {0}'.format(err)))
            return
        return command

    def execute(self, execution_context):
        motor = execution_context.get_symbol(self.target)
        motor.stop()

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
