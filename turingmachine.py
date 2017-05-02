import sys
import time
import os

from collections import namedtuple

PRINT_PADDING = 15
SLEEP_DELAY = 0.1

MachineState = namedtuple('MachineState', ('number', 'read', 'write', 'move', 'next', ))


class Tape:
    head_position = 0

    def __init__(self, string=''):
        self.tape = dict(enumerate(string))
        self.tape_length = len(string)

    def values(self):
        return [str(i[1]) if i[1] != 'B' else ' ' for i in sorted(self.tape.items())]

    def __str__(self):
        padding_left = [' '] * (PRINT_PADDING * 2)
        padding_right = [' '] * (PRINT_PADDING * 2 + 1)

        head_pos = self.head_position + (PRINT_PADDING * 2)

        start = head_pos - PRINT_PADDING
        end = head_pos + PRINT_PADDING + 1

        tape = (padding_left + self.values() + padding_right)[start:end]
        return '|{}|'.format('|'.join(tape))

    def __len__(self):
        return len([x for x in self.tape.values() if x not in {'', ' ', 'B'}])

    def get_position(self):
        return self.head_position

    def read(self):
        try:
            return self.tape[self.get_position()]
        except KeyError:
            return 'B'

    def write(self, value):
        self.tape[self.get_position()] = value

    def move(self, direction):
        if direction == 'L':
            self.head_position -= 1
        elif direction == 'R':
            self.head_position += 1
        elif direction == 'N':
            pass
        else:
            raise NotImplementedError('Unknown direction {}'.format(direction))


class TuringMachine:
    steps = 0

    states = [
        MachineState(
            number=0,
            read='0BB',
            write='B0B',
            move='RRN',
            next=0,
        ),
        MachineState(
            number=0,
            read='1BB',
            write='BBB',
            move='RNN',
            next=1,
        ),
        MachineState(
            number=1,
            read='0BB',
            write='0BB',
            move='NLN',
            next=2,
        ),
        MachineState(
            number=1,
            read='BBB',
            write='BBB',
            move='NNN',
            next=None,
        ),
        MachineState(
            number=2,
            read='00B',
            write='00B',
            move='NLN',
            next=2,
        ),
        MachineState(
            number=2,
            read='0BB',
            write='0BB',
            move='NRN',
            next=3,
        ),
        MachineState(
            number=3,
            read='0BB',
            write='BBB',
            move='RNN',
            next=1,
        ),
        MachineState(
            number=3,
            read='00B',
            write='000',
            move='NRR',
            next=3,
        ),
    ]

    def __init__(self, multiplier, multiplicand):
        self.multiplier = multiplier
        self.multiplicand = multiplicand

        initial_state = '1'.join(('0' * multiplier, '0' * multiplicand))

        self.tapes = [
            Tape(initial_state),
            Tape(),
            Tape(),
        ]

    def get_state(self, previous_state=None):
        key = ''.join((t.read() for t in self.tapes))
        for state in self.states:
            if state.read == key:
                if not previous_state:
                    return state
                elif previous_state.next == state.number:
                    return state

        raise RuntimeError(
            'No state for key {} and number {} found!'.format(key, previous_state.next)
        )

    def apply_state(self, state):
        for index, tape in enumerate(self.tapes):
            tape.write(state.write[index])
            tape.move(state.move[index])

    def print_info(self, state):
        print('Computing {} x {}\n'.format(self.multiplier, self.multiplicand))
        state_info = 'Current State:\n Number: {}\n Read:   {}\n Write:  {}\n Move:   {}\n Next:   {}\n'
        if state:
            print(
                state_info.format(
                    state.number,
                    state.read,
                    state.write,
                    state.move,
                    state.next,
                )
            )
        else:
            print(state_info.format(*([''] * 5)))

        print('Step #{}\n'.format(self.get_steps()))

        print(' ' * PRINT_PADDING * 2, 'R')
        for tape in self.tapes:
            print(tape)

    def get_result(self):
        return len(self.tapes[2])

    def get_steps(self):
        return self.steps

    def step(self, previous_state):
        state = self.get_state(previous_state=previous_state)
        self.apply_state(state)
        return state

    def run(
        self,
        interactive=False,
        sleep=None,
        print_steps=False,
        clear_screen=False,
    ):
        state = None
        halt = False
        while not halt:
            self.steps += 1
            if clear_screen:
                os.system('clear')
            if print_steps:
                print()
                self.print_info(state)
            if sleep:
                time.sleep(SLEEP_DELAY)
            state = self.step(state)
            if state.next is None:
                halt = True
            if interactive:
                input()

        print(
            '\nComputing done: {} x {} = {} in {} steps.'.format(
                self.multiplier, self.multiplicand,
                machine.get_result(), machine.get_steps()
            )
        )


if __name__ == '__main__':
    try:
        multiplier_arg = int(sys.argv[1])
        multiplicand_arg = int(sys.argv[2])
    except (IndexError, TypeError, ValueError):
        sys.exit(
            'Invalid arguments. Usage: python turingmachine.py multiplier multiplicand '
            '[--interactive] [--sleep] [--print] [--clear]'
        )

    machine = TuringMachine(multiplier_arg, multiplicand_arg)
    machine.run(
        interactive='--interactive' in sys.argv or '-i' in sys.argv,
        sleep='--sleep' in sys.argv or '-s' in sys.argv,
        print_steps='--print' in sys.argv or '-p' in sys.argv,
        clear_screen='--clear' in sys.argv or '-c' in sys.argv,
    )
