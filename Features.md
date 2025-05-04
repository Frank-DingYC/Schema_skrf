# Goal

1. Use the pydantic library to rewrite the Network and Circuit objects from scikit-rf library into Pydantic models so that they can be easily serialized/deserialized as JSON or other formats (like YAML). This will make it easier to work with these objects in Python scripts.
3. Based on the schema, we can convert the Json file to Python objects so that I can use scikit-rf library to do the other calculations.

## Core Features

### RLGC Model Validation
- Parameterized tests for all L/C creation variants
- Explicit error handling for invalid parameter combinations
- Type validation through Pydantic models

### Network Analysis
- S-parameter validation (shape, magnitude bounds)
- Port consistency checks
- Frequency range normalization

### File Interoperability
- Touchstone file import/export
- JSON serialization/deserialization
- Network data validation

### Network Parameter Support
- S-parameter matrix conversion (implemented in `Network.from_network`/`to_network`)
- Impedance parameter (z0) interpolation (see `Network.interpolate_z0`)
- Multi-port validation (via `nports` validator)

### Circuit Model
- Bi-directional conversion with scikit-rf Circuit (implemented in `Circuit.from_circuit`/`to_circuit`)
- Connection consistency validation (enforced by `connections` type constraints)

## Enhanced Validation
- Array length parity check for frequency/S-parameters/z0 (tested in `test_z0_dimension_validation`)
- S-parameter matrix dimension validation (see `test_s_parameters_validation`)
- Validates length parity of `frequency`, `s_parameters`, and `z0`.
- Ensures that `s_parameters` and `z0` align with the specified `nports`.
- Properly enforces validation during object initialization to catch invalid data, such as incorrect dimensions for `z0` or `s_parameters`, as tested in unit tests.

## Allow the user to do S-parameter cascade calculation
Adds the ability to perform S-parameter cascade calculations between multiple network objects, returning a new combined network. This optimizes network analysis and simplifies parts of the design process.

## New Features

### RLGC Parameter Support
- Adapter pattern implementation (`RLGCAdapter`)
- Bi-directional conversion with Network objects
- Matrix validation for R/L/G/C parameters
- Frequency-dependent parameter handling

### Enhanced Conversions
- S-parameters ↔ RLGC parameters (using scikit-rf's conversion methods)
- JSON/YAML serialization support for RLGC data

## RLGC Models

### New Features
- Implemented R/L/G/C distributed circuit models with:
  - Frequency-dependent parameters
  - Multi-port support
  - Direct conversion to skrf.Network format via `to_r()`/`to_l()` methods

### Test Coverage
- Full parameter combination validation for L/C models:
  - Basic component creation
  - Q-factor dependent models
  - DC resistance compensation variants
- 100% branch coverage for network generation logic
- Cross-verification with scikit-rf reference implementations
- Validation of network parameter dimensions
- Impedance matching verification
- Port count consistency checks
- Frequency range validation
- Network type conversion tests

## Removed Features
- ~~S-parameter cascade calculation (currently unimplemented)~~
- ~~Experimental noise parameter support (removed)~~

# Recent Changes
- Added Touchstone file interoperability (`Network.from_touchstone`)
- Enhanced JSON serialization support (`Config.json_encoders` configuration)
- Improved validation in `Network.from_network` for S-parameters/z0/nports consistency
- Refactored `Network.__init__` using Pydantic validation
- Added parameter validation for RLGC models
- Implemented frequency unit specification
- Refactored network conversion methods
- Enhanced test coverage reporting

## Project Structure
Schema_skrf/
├── Data/                 # Measurement datasets
│   └── Touchstone/       
│       ├── Calibration/  # VNA calibration kits (3.5mm/2.92mm)
│       └── Device_Models/ # Transistor/SMD component models
├── Src/
│   ├── Models/
│   │   ├── RLGC.py       # R/L/G/C distributed models
│   │   ├── Network.py    # Multi-port network operations  
│   │   ├── Circuit.py    # Circuit analysis/synthesis
│   │   └── Microwave.py  # Microwave components
│   └── tests/
│       ├── test_RLGC.py    # Model validation suite
│       ├── test_Network.py # Network I/O tests
│       └── test_Circuit.py # Circuit conversion tests
├── Examples/            # Usage notebooks
│   ├── Basic_Network_Analysis.ipynb
│   └── Touchstone_Import_Export.ipynb 
└── Features.md          # This documentation

## Touchstone Datasets
Contains 35+ real-world RF measurement files for:
- Network analysis
- Device characterization
- Test validation

File formats include:
- S1P (1-port)
- S2P (2-port)
- S4P (4-port)
- Up to S32P (32-port)