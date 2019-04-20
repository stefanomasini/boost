from collections import namedtuple


class ProgramSyntaxError(namedtuple('ProgramSyntaxError', 'line_num message')):
    def pretty_print(self):
        return 'SyntaxError, line {0}: {1}'.format(self.line_num, self.message)

    def to_json(self):
        return {
            'type': 'SyntaxError',
            'line_num': self.line_num,
            'message': self.message,
        }
