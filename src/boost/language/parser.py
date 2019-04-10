from collections import namedtuple
from functools import partial
import re
from ..commands import CommandTurn, CommandTimeFromStart, CommandTimeJump, CommandFunctionCall


TURN_TO_RANGE = (1, 30)
SPEED_RANGE = (1, 10)


ProgramLine = namedtuple('ProgramLine', 'text indentation line_num')
CommentLine = namedtuple('CommentLine', 'text indentation line_num')

BlockFunction = namedtuple('BlockFunction', 'name parameter lines')
BlockRoot = namedtuple('BlockRoot', 'lines')

Function = namedtuple('Function', 'parameter commands')

Program = namedtuple('Program', 'commands functions')

ProgramSyntaxError = namedtuple('ProgramSyntaxError', 'line_num message')


INDENTATION_RE = re.compile(r'^\ +')
FUNCTION_DEFINITION_RE = re.compile(r'^([a-zA-Z]\w+)(?:\(([A-Z])?\))$')
FUNCTION_EXECUTION_RE = re.compile(r'^([a-zA-Z]\w+)(\(.*)$')
TIME_FROM_START_RE = re.compile(r'^(?:(\d?\d):)?(\d?\d):(\d\d)$')
TIME_JUMP_RE = re.compile(r'^\+(?:(\d?\d):)?(\d?\d):(\d\d)$')


def parse_lines(program, errors):
    for idx, raw_line in enumerate(program.split('\n')):
        line_num = idx + 1
        raw_line = raw_line.rstrip()

        # Skip empty lines
        if not raw_line:
            continue

        indentation_mo = INDENTATION_RE.match(raw_line)
        indentation = 0
        if indentation_mo:
            indentation_spaces = indentation_mo.group(0)
            if len(indentation_spaces) % 4 != 0:
                errors.append(ProgramSyntaxError(line_num, 'Indentation must be multiple of 4 characters'))
            else:
                indentation = len(indentation_spaces) // 4

        line = raw_line.lstrip()
        if line.startswith('#'):
            yield CommentLine(line, indentation, line_num)
        else:
            yield ProgramLine(line, indentation, line_num)


def parse_blocks(program, errors):
    lines_errors = []
    lines = list(parse_lines(program, lines_errors))
    if lines_errors:
        errors.extend(lines_errors)
        return

    program_lines = [l for l in lines if isinstance(l, ProgramLine)]

    expected_indentation = 0
    current_function_name = None
    current_function_parameter = None
    current_block = []
    for program_line in program_lines:
        if program_line.indentation > expected_indentation:
            errors.append(ProgramSyntaxError(program_line.line_num, 'Unexpected indentation'))
        elif current_function_name and program_line.indentation == expected_indentation-1:
            yield BlockFunction(current_function_name, current_function_parameter, current_block)
            current_block = []
            current_function_name = None
            expected_indentation -= 1
        elif program_line.indentation != expected_indentation:
            errors.append(ProgramSyntaxError(program_line.line_num, 'Unexpected indentation'))

        tokens = [t for t in program_line.text.split(' ') if t]

        if tokens[0] == 'def':
            if len(tokens) != 2:
                errors.append(ProgramSyntaxError(program_line.line_num, 'Too many tokens in line'))
                break
            if not tokens[1].endswith(':'):
                errors.append(ProgramSyntaxError(program_line.line_num, 'Function definition must end with colon (:)'))
                break
            function_mo = FUNCTION_DEFINITION_RE.match(tokens[1][:-1])
            if not function_mo:
                errors.append(ProgramSyntaxError(program_line.line_num, 'Invalid function definition'))
                break

            if current_block:
                yield BlockRoot(current_block)

            current_function_name = function_mo.group(1)
            current_function_parameter = function_mo.group(2) if len(function_mo.groups()) == 2 else None
            expected_indentation += 1
            current_block = []

        else:
            current_block.append(program_line)

    if current_block:
        yield BlockRoot(current_block)


def parse_program_line(program_line, functions, symbol_names, errors):
    function_execution_mo = FUNCTION_EXECUTION_RE.match(program_line.text)
    if function_execution_mo:
        return parse_function_call(function_execution_mo, program_line, functions, symbol_names, errors)

    time_from_start_mo = TIME_FROM_START_RE.match(program_line.text)
    if time_from_start_mo:
        millis = parse_time_from_start(time_from_start_mo, program_line, errors)
        return CommandTimeFromStart(millis)

    time_jump_mo = TIME_JUMP_RE.match(program_line.text)
    if time_jump_mo:
        millis = parse_time_from_start(time_jump_mo, program_line, errors)
        return CommandTimeJump(millis)

    errors.append(ProgramSyntaxError(program_line.line_num, 'Invalid command'))
    return


def parse_function_call(function_execution_mo, program_line, functions, symbol_names, errors):
    function_name = function_execution_mo.group(1)
    params_string = function_execution_mo.group(2)
    locals_dict = dict((v, v) for v in symbol_names)
    if function_name in ('left', 'right'):
        try:
            command = eval('CommandTurn' + params_string, {'CommandTurn': partial(CommandTurn, function_name)}, locals_dict)
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
    elif function_name in functions:
        try:
            param_list = eval('tuple' + params_string, locals_dict)
        except Exception as err:
            errors.append(ProgramSyntaxError(program_line.line_num, 'Parsing exception: {0}'.format(err)))
            return
        if len(param_list) > 1:
            errors.append(ProgramSyntaxError(program_line.line_num, 'Too many parameters in function call'))
            return
        return CommandFunctionCall(function_name, param_list)
    else:
        errors.append(ProgramSyntaxError(program_line.line_num, 'Unknown function "{0}"'.format(function_name)))
        return


def parse_time_from_start(mo, program_line, errors):
    groups = mo.groups()
    hours = int(groups[0]) if groups[0] else 0
    minutes = int(groups[-2])
    seconds = int(groups[-1])
    if not (0 <= minutes < 60):
        errors.append(ProgramSyntaxError(program_line.line_num, 'Invalid time format'))
        return
    if not (0 <= seconds < 60):
        errors.append(ProgramSyntaxError(program_line.line_num, 'Invalid time format'))
        return
    millis = ((hours * 60 + minutes) * 60 + seconds) * 1000
    return millis


def parse_program(program_text, symbol_names, errors):
    block_errors = []
    blocks = list(parse_blocks(program_text, block_errors))
    if block_errors:
        errors.extend(block_errors)
        return

    root_blocks = [b for b in blocks if isinstance(b, BlockRoot)]
    if len(root_blocks) == 0:
        errors.append(ProgramSyntaxError(None, 'Missing root-level commands'))
        return
    if len(root_blocks) > 1:
        errors.append(ProgramSyntaxError(None, 'Multiple root-level blocks of commands are not allowed'))
        return
    root_block = root_blocks[0]

    function_blocks = [b for b in blocks if isinstance(b, BlockFunction)]
    function_names = set(b.name for b in function_blocks)

    commands = parse_commands(root_block.lines, function_names, symbol_names, errors)
    functions = dict((b.name, Function(b.parameter, parse_commands(b.lines, function_names, list(symbol_names) + ([b.parameter] if b.parameter else []), errors))) for b in function_blocks)
    return Program(commands, functions)


def parse_commands(program_lines, functions, symbol_names, errors):
    return [parse_program_line(program_line, functions, symbol_names, errors) for program_line in program_lines]

