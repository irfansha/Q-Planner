# Q-Planner
A QBF based planner without grounding.

A QBF encoding is generated for given domain and problem file in PDDL specification with out grounding.

## Dependencies:

Install Tarski: pip install tarski (further instructions available at https://tarski.readthedocs.io/en/latest/installation.html)

For generating plans:
Install CAQE solver and replace the executable in solvers path: ./solvers/qbf/caqe

For preprocessing:
(If existing bloqqer does not work) Install Bloqqer and replace the executable in tools path: ./tools/bloqqer/bloqqer

For preprocessing with plan extraction with CAQE:
(If existing bloqqer does not work) Install Bloqqer-qdo, a modified preprocessor by Leander Tentrup and place in the main directory path: ./bloqqer-qdo

Note: Bloqqer-qdo is a non-public version.

## Usage

For running tests:
python3 qplanner.py --run_tests 1

For only encoding generation (k is plan length):
python3 qplanner.py --path testing/testcases/competition/IPC2/Blocks/ --domain domain.pddl --problem prob01.pddl --plan_length 6 --run 0

For plan existence/extraction:
python3 main.py --path [path to domain and problem files] --domain [domain file name] --problem [problem file name] --plan_length [] --run 1 / --run 2

For plan existence with preprocessing (standard bloqqer works fine):
python3 main.py --path [] --domain [] --problem [] --plan_length [] --run 1 --preprocessing 1

For plan extraction with preprocessing (use bloqqer-qdo):
python3 main.py --path [] --domain [] --problem [] --plan_length [] --run 2 --preprocessing 2

## Contact
Please dont hesitate to write an email to irfansha.shaik@cs.au.dk in case of installing difficulties
