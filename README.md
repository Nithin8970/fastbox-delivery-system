# FastBox Mystery Delivery System

## Run

Requires Python 3.8+ and no third-party packages.

```bash
python delivery_system.py
```

The program reads `data.json` and creates `report.json` and
`top_performer.csv`.

## Implementation

1. Parse JSON using Python's standard `json` module.
2. Calculate Euclidean distance between each agent and each package warehouse.
3. Assign every package to the nearest agent.
4. Simulate `current location -> warehouse -> destination`.
5. Keep the agent at the delivery destination for the next assigned package.
6. Calculate:
   `efficiency = total_distance / packages_delivered`
7. Report the agent with the lowest average distance per package.
8. Validate that every input package was assigned exactly once.

The code also accepts both the PDF's dictionary format and the supplied
`base_case.json` list-of-objects format.

## Test cases

The supplied `test_cases/` directory contains 10 additional inputs.
Copy any one of them to `data.json` and run the program again.

Example on Windows:

```bat
copy test_cases\test_case_2.json data.json
python delivery_system.py
```

Example on Linux/macOS:

```bash
cp test_cases/test_case_2.json data.json
python delivery_system.py
```

## Bonus

`top_performer.csv` is generated automatically, and `report.json` includes
per-package route details.
