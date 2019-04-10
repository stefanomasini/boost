import unittest
from .parser import parse_lines, parse_program_line, parse_program, \
    ProgramLine, CommentLine, \
    parse_blocks, ProgramSyntaxError, \
    BlockFunction, BlockRoot, \
    CommandTurn, CommandTimeFromStart, CommandTimeJump, CommandFunctionCall, Function


CODE_SAMPLE_INDENTATION_ERROR = """
def main():
     right(A, to=12, speed=1)
    
    # Another comment
    0:06 
    left(A, to=6, speed=4)
   left(B, to=6, speed=4)
    
def test(X):
    left(X, to=1, time=2)

"""


CODE_SAMPLE_1 = """
# One comment
def main():
    right(A, to=12, speed=1)
    
    # Another comment
    0:06 
    left(A, to=6, speed=4)
    left(B, to=6, speed=4)
    
def test(X):
    left(X, to=1, time=2)

0:00
main()
test(A)

1:00
test(B)
"""


CODE_SAMPLE_2 = """
# One comment
def main():
    right(A, to=12, speed=1)
    
    # Another comment
    0:06 
    left(A, to=6, speed=4)
    left(B, to=6, speed=4)
    
def test(X):
    left(X, to=1, speed=2)

0:00
main()
test(A)

1:00
test(B)
"""


class ParserTestSuite(unittest.TestCase):
    def setUp(self):
        self.local_variables = ('A', 'B')

    def test_indentation_error(self):
        errors = []
        list(parse_lines(CODE_SAMPLE_INDENTATION_ERROR, errors))
        self.assertEqual(errors, [
            ProgramSyntaxError(line_num=3, message='Indentation must be multiple of 4 characters'),
            ProgramSyntaxError(line_num=8, message='Indentation must be multiple of 4 characters'),
        ])

    def test_parsing_lines(self):
        errors = []
        lines = list(parse_lines(CODE_SAMPLE_1, errors))
        self.assertEqual(errors, [])
        self.assertEqual(lines, [
            CommentLine(text='# One comment', indentation=0, line_num=2),
            ProgramLine(text='def main():', indentation=0, line_num=3),
            ProgramLine(text='right(A, to=12, speed=1)', indentation=1, line_num=4),
            CommentLine(text='# Another comment', indentation=1, line_num=6),
            ProgramLine(text='0:06', indentation=1, line_num=7),
            ProgramLine(text='left(A, to=6, speed=4)', indentation=1, line_num=8),
            ProgramLine(text='left(B, to=6, speed=4)', indentation=1, line_num=9),
            ProgramLine(text='def test(X):', indentation=0, line_num=11),
            ProgramLine(text='left(X, to=1, time=2)', indentation=1, line_num=12),
            ProgramLine(text='0:00', indentation=0, line_num=14),
            ProgramLine(text='main()', indentation=0, line_num=15),
            ProgramLine(text='test(A)', indentation=0, line_num=16),
            ProgramLine(text='1:00', indentation=0, line_num=18),
            ProgramLine(text='test(B)', indentation=0, line_num=19),
        ])

    def test_parsing_blocks(self):
        errors = []
        blocks = list(parse_blocks(CODE_SAMPLE_2, errors))
        self.assertEqual(errors, [])
        self.assertEqual(blocks, [
            BlockFunction(name='main', parameter=None, lines=[
                ProgramLine(text='right(A, to=12, speed=1)', indentation=1, line_num=4),
                ProgramLine(text='0:06', indentation=1, line_num=7),
                ProgramLine(text='left(A, to=6, speed=4)', indentation=1, line_num=8),
                ProgramLine(text='left(B, to=6, speed=4)', indentation=1, line_num=9)
            ]),
            BlockFunction(name='test', parameter='X', lines=[
                ProgramLine(text='left(X, to=1, speed=2)', indentation=1, line_num=12)
            ]),
            BlockRoot(lines=[
                ProgramLine(text='0:00', indentation=0, line_num=14),
                ProgramLine(text='main()', indentation=0, line_num=15),
                ProgramLine(text='test(A)', indentation=0, line_num=16),
                ProgramLine(text='1:00', indentation=0, line_num=18),
                ProgramLine(text='test(B)', indentation=0, line_num=19)
            ])
        ])

    def test_parsing_command_right(self):
        errors = []
        command = parse_program_line(ProgramLine(text='right(A, to=12, speed=1)', indentation=1, line_num=4), {}, self.local_variables, errors)
        self.assertEqual(errors, [])
        self.assertEqual(command, CommandTurn(direction='right', target='A', to=12, speed=1))

    def test_parsing_command_left(self):
        errors = []
        command = parse_program_line(ProgramLine(text='left(A, to=12, speed=1)', indentation=1, line_num=4), {}, self.local_variables, errors)
        self.assertEqual(errors, [])
        self.assertEqual(command, CommandTurn(direction='left', target='A', to=12, speed=1))

    def test_parsing_command_left_with_local_var(self):
        errors = []
        command = parse_program_line(ProgramLine(text='left(X, to=12, speed=1)', indentation=1, line_num=4), {}, self.local_variables + ('X',), errors)
        self.assertEqual(errors, [])
        self.assertEqual(command, CommandTurn(direction='left', target='X', to=12, speed=1))

    def test_parsing_function_call(self):
        errors = []
        command = parse_program_line(ProgramLine(text='foo(A)', indentation=1, line_num=4), {'foo'}, self.local_variables, errors)
        self.assertEqual(errors, [])
        self.assertEqual(command, CommandFunctionCall(function_name='foo', params=('A',)))

    def test_parsing_command_time_from_start(self):
        errors = []
        command = parse_program_line(ProgramLine(text='0:03', indentation=1, line_num=4), {}, self.local_variables, errors)
        self.assertEqual(errors, [])
        self.assertEqual(command, CommandTimeFromStart(millis=3000))

    def test_parsing_command_time_jump(self):
        errors = []
        command = parse_program_line(ProgramLine(text='+1:03', indentation=1, line_num=4), {}, self.local_variables, errors)
        self.assertEqual(errors, [])
        self.assertEqual(command, CommandTimeJump(millis=63000))

    def test_parsing_program(self):
        errors = []
        commands, functions = parse_program(CODE_SAMPLE_2, self.local_variables, errors)
        self.assertEqual(errors, [])
        self.assertEqual(commands, [
            CommandTimeFromStart(millis=0),
            CommandFunctionCall(function_name='main', params=()),
            CommandFunctionCall(function_name='test', params=('A',)),
            CommandTimeFromStart(millis=60000),
            CommandFunctionCall(function_name='test', params=('B',))
        ])
        self.assertEqual(functions, {
            'main': Function(parameter=None, commands=[
                CommandTurn(direction='right', target='A', to=12, speed=1),
                CommandTimeFromStart(millis=6000),
                CommandTurn(direction='left', target='A', to=6, speed=4),
                CommandTurn(direction='left', target='B', to=6, speed=4)
            ]),
            'test': Function(parameter='X', commands=[
                CommandTurn(direction='left', target='X', to=1, speed=2)
            ])
        })
