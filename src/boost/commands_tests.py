from datetime import datetime, timedelta
import unittest
from boost.language.parser import parse_program
from .executor import ExecutionContext, WarningRuntimeMessage


CODE_SAMPLE_1 = """
def main():
    right(A, to=12, speed=1)
    
    0:06 
    left(A, to=6, speed=4)
    left(B, to=6, speed=4)
    
def test(X):
    left(X, to=1, speed=2)

0:01
main()
test(A)

+0:03
left(B, to=10, speed=2)
main()

1:00
test(B)
right(B, to=10, speed=2)
"""


class FakeClock(object):
    def __init__(self, now):
        self._now = now

    def now(self):
        return self._now

    def add(self, td):
        self._now = self._now + td


class FakeMotor(object):
    def __init__(self, clock, name, emit_log):
        self.clock = clock
        self.name = name
        self.emit_log = emit_log

    def turn(self, direction, to, speed):
        self.emit_log('{0} MOTOR {1} TURN {2} {3} {4}'.format(self.clock.now(), self.name, direction, to, speed))


class CommandsTestSuite(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock(datetime(2019, 4, 9, 22, 5, 0))  # 9 Apr 2019 - 22:05
        self.log_lines = []
        self.symbols = {'A': FakeMotor(self.clock, 'A', self.log_lines.append), 'B': FakeMotor(self.clock, 'B', self.log_lines.append)}

    def _compile_program(self, program_code):
        errors = []
        program = parse_program(program_code, self.symbols.keys(), errors)
        self.assertEqual(errors, [])
        return program

    def test_running_program(self):
        program = self._compile_program(CODE_SAMPLE_1)
        execution_context = ExecutionContext(program, self.clock, self.symbols, lambda m: self.log_lines.append(m.message))
        self.assertTrue(execution_context.execute_if_scheduled())
        self.assertFalse(execution_context.execute_if_scheduled())
        for _ in range(10000):
            self.clock.add(timedelta(milliseconds=100))
            execution_context.execute_if_scheduled()
            if execution_context.terminated:
                break
        self.assertTrue(execution_context.terminated)
        self.assertEqual(self.log_lines, [
            '2019-04-09 22:05:01 MOTOR A TURN right 12 1',
            '2019-04-09 22:05:06 MOTOR A TURN left 6 4',
            '2019-04-09 22:05:06 MOTOR B TURN left 6 4',
            '2019-04-09 22:05:06 MOTOR A TURN left 1 2',
            '2019-04-09 22:05:09 MOTOR B TURN left 10 2',
            '2019-04-09 22:05:09 MOTOR A TURN right 12 1',
            'Scheduling execution in the past',
            '2019-04-09 22:05:09 MOTOR A TURN left 6 4',
            '2019-04-09 22:05:09 MOTOR B TURN left 6 4',
            '2019-04-09 22:06:00 MOTOR B TURN left 1 2',
            '2019-04-09 22:06:00 MOTOR B TURN right 10 2'
        ])
