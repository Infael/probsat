import os
import statistics
import sys
import random as r
import time

MAX_TRIES_FLAG = "--max_tries" 
MAX_TRIES_DEFAULT = 300
MAX_FLIPS_FLAG = "--max_flips"
MAX_FLIPS_DEFAULT = 300
INPUT_FILE_FLAG = "--data"
FILES_FLAG = '--files'
CM_FLAG = "--cm"
CM = 0
CB_FLAG = "--cb"
CB = 2.3
REPEAT_FLAG = "-r"
REPEAT = 1
SORT_DATA_FILES_FLAG = '-s'

def find_indices(list_to_check, item_to_find):
    return [idx for idx, value in enumerate(list_to_check) if value == item_to_find]

class SAT:
    def __init__(self, data: list, vars_count: int, clause_count: int, random: bool = False ) -> None:
        self.vars_count = int(vars_count)
        self.clause_count = int(clause_count)
        self.clauses = data
        self.evaluation = [not not r.getrandbits(1) if random else True for _ in range(self.vars_count)]

    def __str__(self) -> str:
        return f"vars: {self.vars_count}\nclauses: {self.clause_count}\ndata: {self.clauses}\nactual evaluation: {self.evaluation}"

    def is_eval_satisfying(self):
        return not False in self.clauses_evaluation()

    def clauses_evaluation(self):
        return [True in [(self.evaluation[abs(int(y)) - 1] if int(y) > 0 else not self.evaluation[abs(int(y)) - 1]) for y in x] for x in self.clauses]

    def satisfied_clauses_count(self):
        return sum(1 for i in self.clauses_evaluation() if i)
    
    def flip(self, index_of_var_to_flip):
        self.evaluation[index_of_var_to_flip] = not self.evaluation[index_of_var_to_flip]

    def _get_weights(self, clause, actual_eval, cm, cb):
        weights = []
        for var in clause:
            self.flip(abs(int(var))-1)
            m, b = 0, 0
            new_eval = self.clauses_evaluation()
            for n_eval, a_eval in zip(new_eval, actual_eval):
                if n_eval == True and a_eval == False:
                    m += 1
                elif n_eval == False and a_eval == True:
                    b += 1
            weights.append(m**cm / (b + sys.float_info.epsilon)**cb)
            self.flip(abs(int(var))-1)
        return [x/sum(weights) for x in weights]
            


    def probSAT_flip(self, cm, cb):
        actual_evaluation = self.clauses_evaluation()
        indecis = find_indices(actual_evaluation, False)
        clause = self.clauses[r.choice(indecis)]
        # print(f"{clause=}")
        weights = self._get_weights(clause, actual_evaluation, cm, cb)
        # print(f"{weights=}")
        variable = r.choices(clause, weights=weights)
        # print(f"{variable=}")
        self.flip(abs(int(variable[0])) - 1)

    def random_evaluation_assign(self):
        self.evaluation = [not not r.getrandbits(1) for _ in range(self.vars_count)]
    


def handle_input_sat(file_name):
    vars_count = 0
    clauses_count = 0
    data = []
    with open(file_name, "r") as file:
        while True:
            line = file.readline()
            if not line:
                break
            if line.startswith("c"):
                continue
            if line.startswith("p"):
                vars_count = line.split()[-2]
                clauses_count = line.split()[-1]
            else:
                data.append(line.split()[:-1])

    return SAT(data, vars_count, clauses_count, True)


def probSAT(sat: SAT, max_tries, max_flips, cm, cb):
    tries, flips = 0, 0
    for i in range(max_tries):
        tries += 1
        sat.random_evaluation_assign()
        for j in range(max_flips):
            if sat.is_eval_satisfying():
                return (flips, sat.satisfied_clauses_count(), sat.clause_count)
            flips += 1
            sat.probSAT_flip(cm, cb)
    return (flips, sat.satisfied_clauses_count(), sat.clause_count)


def main(argv: list):
    max_tries = MAX_TRIES_DEFAULT
    if MAX_TRIES_FLAG in argv:
        try:
            max_tries = int(argv[argv.index(MAX_TRIES_FLAG)+1])
        except Exception:
            raise "Wrong max tries argument"

    max_flips = MAX_FLIPS_DEFAULT
    if MAX_FLIPS_FLAG in argv:
        try:
            max_flips = int(argv[argv.index(MAX_FLIPS_FLAG)+1])
        except Exception:
            raise "Wrong max flips argument"

    cm = CM
    if CM_FLAG in argv:
        try:
            cm = float(argv[argv.index(CM_FLAG)+1])
        except Exception:
            raise "Wrong cm argument"

    cb = CB
    if CB_FLAG in argv:
        try:
            cb = float(argv[argv.index(CB_FLAG)+1])
        except Exception:
            raise "Wrong cb argument"

    repeat = REPEAT
    if REPEAT_FLAG in argv:
        try:
            repeat = int(argv[argv.index(REPEAT_FLAG)+1])
        except Exception:
            raise "Wrong repeat argument"

    if not INPUT_FILE_FLAG in argv and not FILES_FLAG in argv:
        raise "Missing input file flag"
    if INPUT_FILE_FLAG in argv:
        try:
            input_file_name = argv[argv.index(INPUT_FILE_FLAG)+1]
        except Exception:
            raise "Missing input file name"
        
        sat = handle_input_sat(input_file_name)
        if repeat == 1:
            print(probSAT(sat, max_tries, max_flips, cm, cb))
        else:
            flips, satisfied_clauses, all_clauses = [], [], []
            start_time = time.time()
            for i in range(repeat):
                n_flips , n_satisfied_clauses, n_all_clauses = probSAT(sat, max_tries, max_flips, cm, cb)
                flips.append(n_flips)
                satisfied_clauses.append(n_satisfied_clauses)
                all_clauses.append(n_all_clauses)
                if i % 100 == 0:
                    print(f"{i/10000*repeat}%")
            print('100%')
            with open(input_file_name+'_out.txt', 'w') as out:
                for line in zip(flips, satisfied_clauses, all_clauses):
                    out.write(f"{line[0]};{line[1]};{line[2]}\n")

            print(f"--- finished in {round(time.time() - start_time, 2)} s ---")

    if FILES_FLAG in argv:
        try:
            path = argv[argv.index(FILES_FLAG)+1]
        except Exception:
            raise "Missing path"
        for (dirpath, dirnames, filenames) in os.walk(path):
            files = filenames
            break
        
        # sort files in folder by number specific for school data
        if SORT_DATA_FILES_FLAG in argv:
            files.sort(key=lambda file_name:int(file_name[5:-4]))

        # create new path if don't exist
        newpath = path+'-out'
        if not os.path.exists(newpath):
            os.makedirs(newpath)

        start_time = time.time()
        for file_name in files:
            sat = handle_input_sat(os.path.join(path,file_name))
            if repeat == 1:
                print(probSAT(sat, max_tries, max_flips, cm, cb))
            else:
                tries, flips = [], []
                for i in range(repeat):
                    n_flips , n_satisfied_clauses, n_all_clauses = probSAT(sat, max_tries, max_flips, cm, cb)
                    flips.append(n_flips)
                    satisfied_clauses.append(n_satisfied_clauses)
                    all_clauses.append(n_all_clauses)
                    if i % 100 == 0:
                        print(f"{file_name}: {i/10000*repeat}%")
                print(f'{file_name}: 100%')
                with open(file_name+'_out.txt', 'w') as out:
                    for line in zip(flips, satisfied_clauses, all_clauses):
                        out.write(f"{line[0]};{line[1]};{line[2]}\n")
        print(f"--- finished in {round(time.time() - start_time, 2)} s ---")


if __name__ == "__main__":
    main(sys.argv[1:])