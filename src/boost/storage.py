import os
import json
from .constants import MotorControllerConstants

SAMPLE_PROGRAM_FILEPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'language', 'sample_program.txt')
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'data'))
PROGRAMS_DIR = os.path.join(DATA_DIR, 'programs')

SAMPLE_PROGRAM = open(SAMPLE_PROGRAM_FILEPATH, 'r', encoding='utf-8').read()


class Storage(object):
    def __init__(self, application_defaults):
        self.application_defaults = application_defaults
        self.data = None
        self._on_program_changed = None

    def initialize(self, on_program_changed):
        if not os.path.exists(DATA_DIR):
            self.data = self._create_default_data()
            self._create_data_folder()
        else:
            self.data = self._read_data_folder()
        self._on_program_changed = on_program_changed

    def _create_data_folder(self):
        os.makedirs(DATA_DIR)
        if not os.path.exists(PROGRAMS_DIR):
            os.makedirs(PROGRAMS_DIR)
        self._save_programs()

    def _save_programs(self):
        meta = {
            'current_program_id': self.data['programs']['current_program_id'],
            'all_programs': [(program_id, program['name']) for program_id, program in self.data['programs']['all_programs'].items()],
        }
        json.dump(meta, open(os.path.join(PROGRAMS_DIR, 'meta.json'), 'w', encoding='utf-8'))
        for program_id, program in self.data['programs']['all_programs'].items():
            open(os.path.join(PROGRAMS_DIR, '{0}.txt'.format(program_id)), 'w', encoding='utf-8').write(program['code'])

    def _read_data_folder(self):
        return {
            'programs': self._read_programs(),
        }

    def _read_programs(self):
        meta = json.load(open(os.path.join(PROGRAMS_DIR, 'meta.json'), 'r', encoding='utf-8'))
        programs = {
            'current_program_id': meta['current_program_id'],
            'all_programs': {},
        }
        for program_id, program_name in meta['all_programs']:
            programs['all_programs'][program_id] = {
                'name': program_name,
                'code': open(os.path.join(PROGRAMS_DIR, '{0}.txt'.format(program_id)), 'r', encoding='utf-8').read()
            }
        return programs

    def _create_default_data(self):
        return {
            'programs': {
                'all_programs': {
                    1: {
                        'name': 'Program 1',
                        'code': SAMPLE_PROGRAM,
                    },
                },
                'current_program_id': 1,
            }
        }

    def get_programs(self):
        return self.data['programs']

    def set_programs(self, programs):
        old_code = self.get_current_program()['code']
        programs['all_programs'] = dict((int(program_id), program) for program_id, program in programs['all_programs'].items())
        self.data['programs'] = programs
        self._save_programs()
        new_code = self.get_current_program()['code']
        if new_code != old_code:
            if not self._on_program_changed():
                return False
        return True

    def get_motors_constants(self):
        return MotorControllerConstants([0.2, 0.4, 0.6, 0.8, 1.0], 0.5)

    def get_current_program(self):
        return self.data['programs']['all_programs'][self.data['programs']['current_program_id']]
