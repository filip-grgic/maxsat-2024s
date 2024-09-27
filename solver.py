from pysat.solvers import Solver
from pysat.formula import CNF, WCNF
from pysat.card import CardEnc, EncType
from copy import deepcopy
import random
import argparse


class MaxSATSolver:
    def __init__(self, solver_name: str, formula_file: str = None):
        self.original_formula = CNF(from_file=formula_file)
        self.formula = WCNF()
        self.weight = 0

        # Use new_literal to keep track of the highest free literal signifier to use
        new_literal = self.original_formula.nv + 1

        # Turn into WCNF instance including Blocking Variable Transformation
        for clause in self.original_formula.clauses:
            if len(clause) > 1:
                # add new hard clause with new literals negated as a new disjunct
                new_clause = deepcopy(clause)
                new_clause.append(-new_literal)

                # add new soft clause with new literal as a new disjunct and weight 1
                self.formula.append(clause=new_clause)
                self.formula.append(clause=[new_literal], weight=1)

                new_literal = self.formula.nv + 1
            elif len(clause) == 1:
                self.formula.append(clause=clause, weight=1)

        self.solver_name = solver_name
        self.sat_solver = Solver(name=solver_name, bootstrap_with=self.formula.hard)

    def solve(self):
        pass

    def get_model(self):
        pass


class BinarySearchMaxSATSolver(MaxSATSolver):
    def __init__(self, solver_name: str, formula_file: str = None):
        super().__init__(solver_name, formula_file)
        self.model = []
        self.full_model = []

    def solve(self):
        upper_bound = len(self.formula.soft)
        lower_bound = 0

        best_model = []
        full_best_model = []

        satisfied = False

        while upper_bound > lower_bound + 1:
            print("running")
            mid = (upper_bound + lower_bound) // 2
            round_formula = deepcopy(self.formula)

            card_layer = CardEnc.equals([cl[0] for cl in self.formula.soft], bound=mid, top_id=self.formula.nv, encoding=EncType.totalizer).clauses
            round_formula.extend(card_layer)
            round_solver = Solver(name=self.solver_name, bootstrap_with=round_formula.hard)

            if round_solver.solve():
                full_best_model = round_solver.get_model()
                best_model = [lit for lit in round_solver.get_model() if abs(lit) <= self.original_formula.nv]
                print(best_model)
                self.weight = mid
                print(self.weight)
                lower_bound = mid
                satisfied = True
            else:
                upper_bound = mid

            round_solver.delete()

        if satisfied:
            self.full_model = full_best_model
            self.model = best_model

        return satisfied

    def get_model(self):
        return self.model

    def get_full_model(self):
        return self.full_model


class MSU3MaxSatSolver(MaxSATSolver):
    def __init__(self, solver_name: str, formula_file: str = None):
        super().__init__(solver_name, formula_file)
        self.model = []

    def solve(self):
        card_layer = []
        assumptions = [clause[0] for clause in self.formula.soft if len(clause) == 1]
        in_card = []

        hard_clauses = self.formula.hard
        cost = 0
        satisfied = False

        while not satisfied and len(assumptions) > 0:
            solver = Solver(name=self.solver_name, bootstrap_with=(hard_clauses + card_layer))
            satisfied = solver.solve(assumptions=assumptions)

            if not satisfied:
                core = solver.get_core()
                in_card.extend([-lit for lit in core])
                assumptions = [lit for lit in assumptions if lit not in core]
                cost += 1
                card_layer = CardEnc.atmost([lit for lit in in_card if lit < 0], bound=cost, top_id=self.formula.nv, encoding=EncType.totalizer).clauses
            else:
                self.model = [lit for lit in solver.get_model() if abs(lit) <= self.original_formula.nv]

    def get_model(self):
        return self.model


class IHSMaxSatSolver(MaxSATSolver):
    def __init__(self, solver_name: str, formula_file: str = None):
        super().__init__(solver_name, formula_file)
        self.model = []

    def solve(self):
        assumptions = [clause[0] for clause in self.formula.soft if len(clause) == 1]
        satisfied = False
        solver = Solver(name=self.solver_name, bootstrap_with=self.formula.hard)

        while not satisfied and len(assumptions) > 0:
            satisfied = solver.solve(assumptions=assumptions)
            if not satisfied:
                core = solver.get_core()
                chosen_element = random.choice(core)
                assumptions = [lit for lit in assumptions if lit != chosen_element]
            else:
                self.model = [lit for lit in solver.get_model() if abs(lit) <= self.original_formula.nv]

        return satisfied

    def get_model(self):
        return self.model


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='MaxSat Solver',
        description='This is a MaxSat Solver implemented during the course of "SAT Solving and Extensions" at '
                    'TU Vienna in the summer semester 2024. It is able to solve unweighted and non-partial MaxSat '
                    'problems using different algorithms like Binary Search, MSU3 and IHS.')

    parser.add_argument('-f', '--filename', dest="filename", action='store', type=str,
                        help='A problem instance in CNF format')
    parser.add_argument('-s', '--sat-solver', dest="sat_solver", action='store', type=str,
                        help='Specify which SAT solver should be used according to the available PySAT list',
                        default='g4')
    parser.add_argument('-m', '--maxsat-solver', dest="maxsat_solver",
                        action='store', choices=['binary', 'msu3', 'ihs'],
                        help='Specify which MaxSAT solver should be used. Choose between "binary", "msu3" and "ihs".')

    args = parser.parse_args()

    sat_solver = args.sat_solver
    maxsat_solver = None
    filename = args.filename

    if args.maxsat_solver == 'binary':
        maxsat_solver = BinarySearchMaxSATSolver(sat_solver, filename)
    elif args.maxsat_solver == 'msu3':
        maxsat_solver = MSU3MaxSatSolver(sat_solver, filename)
    elif args.maxsat_solver == 'ihs':
        maxsat_solver = IHSMaxSatSolver(sat_solver, filename)

    maxsat_solver.solve()

    print(maxsat_solver.get_model())
