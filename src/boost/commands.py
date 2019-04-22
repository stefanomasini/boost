from collections import namedtuple
from functools import partial
from .language.errors import ProgramSyntaxError


class CommandTurn(namedtuple('CommandTurn', 'direction target speed to', defaults=(None,))):
    @classmethod
    def parse(cls, program_line, function_name, params_string, locals_dict, runtime_parameters, errors):
        turn_to_range = (1, runtime_parameters.num_turn_sections)
        speed_range = (1, runtime_parameters.num_speeds)
        try:
            command = eval(cls.__name__ + params_string, {cls.__name__: partial(cls, function_name)}, locals_dict)
        except Exception as err:
            errors.append(ProgramSyntaxError(program_line.line_num, 'Parsing exception: {0}'.format(err)))
            return
        if command.to is not None:
            if not isinstance(command.to, int):
                errors.append(ProgramSyntaxError(program_line.line_num, '"to" parameter must be an integer'))
                return
            if not (turn_to_range[0] <= command.to <= turn_to_range[1]):
                errors.append(ProgramSyntaxError(program_line.line_num, '"to" parameter must be in range {0}-{1}'.format(*turn_to_range)))
                return
        if not isinstance(command.speed, int):
            errors.append(ProgramSyntaxError(program_line.line_num, '"speed" parameter must be an integer'))
            return
        if not (speed_range[0] <= command.speed <= speed_range[1]):
            errors.append(ProgramSyntaxError(program_line.line_num, '"speed" parameter must be in range {0}-{1}'.format(*speed_range)))
            return
        return command

    def execute(self, execution_context):
        if self.to:
            execution_context.log_message('{0} turning {1} to {2} at speed {3}'.format(self.target, self.direction, self.to, self.speed))
        else:
            execution_context.log_message('{0} turning {1} at speed {2}'.format(self.target, self.direction, self.speed))
        motor = execution_context.get_symbol(self.target)
        motor.turn(self.direction, self.to, self.speed)

        execution_context.advance_pc()
        return False  # Non blocking - continue executing following commands


class CommandStop(namedtuple('CommandStop', 'target')):
    @classmethod
    def parse(cls, program_line, function_name, params_string, locals_dict, runtime_parameters, errors):
        try:
            command = eval(cls.__name__ + params_string, {cls.__name__: cls}, locals_dict)
        except Exception as err:
            errors.append(ProgramSyntaxError(program_line.line_num, 'Parsing exception: {0}'.format(err)))
            return
        return command

    def execute(self, execution_context):
        execution_context.log_message('Stopping {0}'.format(self.target))
        motor = execution_context.get_symbol(self.target)
        motor.stop()

        execution_context.advance_pc()
        return False  # Non blocking - continue executing following commands


class CommandRestartProgram(object):
    @classmethod
    def parse(cls, program_line, function_name, params_string, locals_dict, runtime_parameters, errors):
        return cls()

    def execute(self, execution_context):
        execution_context.log_message('Restarting program')
        execution_context.initialize_execution()
        return True  # "blocking" - really, just restarting and scheduling next execution at time 0 (i.e. ASAP)


class CommandTimeFromStart(namedtuple('CommandTimeFromStart', 'millis')):
    def execute(self, execution_context):
        execution_context.log_message('Waiting until second {0:.2f}'.format(self.millis / 1000.0))
        execution_context.schedule_next_execution_at_time(self.millis)
        execution_context.advance_pc()
        return True  # Blocking - stop executing other commands


class CommandTimeJump(namedtuple('CommandTimeJump', 'millis')):
    def execute(self, execution_context):
        execution_context.log_message('Waiting {0:.2f} seconds'.format(self.millis / 1000.0))
        execution_context.schedule_next_execution_in_ms(self.millis)
        execution_context.advance_pc()
        return True  # Blocking - stop executing other commands


class CommandFunctionCall(namedtuple('CommandFunctionCall', 'function_name params')):
    def execute(self, execution_context):
        execution_context.log_message('Calling function {0}'.format(self.function_name))
        function = execution_context.functions[self.function_name]
        symbol_mapping = []
        if function.parameter and len(self.params) > 0:
            symbol_mapping.append( (function.parameter, self.params[0]) )
        execution_context.advance_pc()
        execution_context.push_scope(function.commands, symbol_mapping)
        return False  # Non blocking - continue executing following commands
