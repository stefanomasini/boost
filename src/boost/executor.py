from collections import namedtuple
from datetime import timedelta


WarningRuntimeMessage = namedtuple('WarningRuntimeMessage', 'message')
FatalRuntimeError = namedtuple('FatalRuntimeError', 'message')


class Scope(object):
    def __init__(self, commands, symbols):
        self.commands = commands
        self.symbols = symbols
        self.pc = 0

    def __repr__(self):
        return '<Scope PC {0}/{1}>'.format(self.pc, len(self.commands))

    def advance_pc(self):
        self.pc += 1

    def no_more_commands(self):
        return self.pc >= len(self.commands)

    def get_command_under_pc(self):
        return self.commands[self.pc] if self.pc < len(self.commands) else None


class ExecutionContext(object):
    def __init__(self, program, clock, symbols, emit_messages):
        self.clock = clock
        self.functions = program.functions
        self.program = program
        self.symbols = symbols
        self.emit_messages = emit_messages
        self.terminated = False
        self.scopes = None
        self.start_time = None
        self.next_execution_secs_from_start = None
        self.initialize_execution()

    def initialize_execution(self):
        self.scopes = [Scope(self.program.commands, self.symbols)]
        self.start_time = self.clock.now()
        self.next_execution_secs_from_start = 0

    def warning(self, message):
        self.emit_messages(WarningRuntimeMessage(message))

    def fatal_error(self, message):
        self.emit_messages(FatalRuntimeError(message))
        self.terminated = True

    def get_symbol(self, symbol_name):
        return self.scopes[-1].symbols[symbol_name]

    def schedule_next_execution_at_time(self, millis_from_start):
        if millis_from_start / 1000 < (self.clock.now() - self.start_time).total_seconds():
            self.warning('Scheduling execution in the past')
        if self.next_execution_secs_from_start is not None:
            self.warning('Overwriting scheduled execution')
        self.next_execution_secs_from_start = millis_from_start / 1000.0

    def schedule_next_execution_in_ms(self, millis):
        if self.next_execution_secs_from_start is not None:
            self.warning('Overwriting scheduled execution')
        self.next_execution_secs_from_start = (self.clock.now() + timedelta(milliseconds=millis) - self.start_time).total_seconds()

    def is_scheduled_execution_in_the_past(self):
        elapsed_secs_from_start = (self.clock.now() - self.start_time).total_seconds()
        return self.next_execution_secs_from_start and self.next_execution_secs_from_start < elapsed_secs_from_start

    def advance_pc(self):
        self.scopes[-1].advance_pc()

    def push_scope(self, commands, symbol_mapping):
        symbols = self.scopes[-1].symbols
        new_symbols = symbols.copy()
        for symbol_name, symbol_reference in symbol_mapping:
            new_symbols[symbol_name] = symbols[symbol_reference]
        self.scopes.append(Scope(commands, new_symbols))

    def get_command_to_execute(self):
        if len(self.scopes) > 0 and self.scopes[-1].no_more_commands():
            self.scopes.pop()
        if len(self.scopes) == 0:
            return None
        return self.scopes[-1].get_command_under_pc()

    def execute_next_command(self):
        command = self.get_command_to_execute()
        if not command:
            self.terminated = True
            return True
        else:
            blocking = command.execute(self)
            if blocking and self.is_scheduled_execution_in_the_past():
                blocking = False
                self.next_execution_secs_from_start = None
            return blocking

    def execute_next_commands(self):
        self.next_execution_secs_from_start = None
        while not self.execute_next_command():
            pass
        if self.next_execution_secs_from_start is None and not self.terminated:
            self.fatal_error('No more commands to execute in current cycle, no execution scheduled but program not terminated either')

    def execute_if_scheduled(self):
        if self.terminated:
            return False
        millis_from_start = (self.clock.now() - self.start_time).total_seconds()
        if self.next_execution_secs_from_start is not None and millis_from_start >= self.next_execution_secs_from_start:
            self.execute_next_commands()
            return True
        else:
            return False

