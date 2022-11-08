# PROBSAT
3-SAT solver written in python. Compiled to c++ using Cython.

## Examples
run on one file:

```bash
python run.py --max_tries 1 --max_flips 300 --data ../uf20-91/uf20-01.cnf -r 1000
```

run on multiple files:

```bash
python run.py --max_tries 1 --max_flips 300 --files ../uf20-91 -s -r 1000
```




compile to Cython:

```bash
python setup.py build_ext --inplace 
```
