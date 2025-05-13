# Schema_skrf Features

## Recent Updates

1. Integrated with Tidy3d base model system
2. Enhanced model validation and type safety
3. Added type discrimination for all components
4. Fixed component type preservation in Circuit model
5. Improved test stability for simulation components
6. Added comprehensive type validation system
7. Enhanced component identification mechanism
8. Streamlined circuit testing framework
9. Improved impedance handling with default 50Ω behavior
10. Enhanced z0 and z0_port validation in components
11. Improved z0 type flexibility (support for both 1D and 2D arrays)
12. Enhanced scikit-rf Circuit conversion robustness
13. Fixed network list handling in Circuit conversions
14. Optimized Network instantiation with direct parameter passing

## Circuit Model
### Core Features
* Tidy3d Integration
  * Built on Tidy3d's base model system
  * Enhanced validation and type safety
  * Consistent with Tidy3d's component architecture
* Unified Component Interface
  * Seamless integration of Network and Component models
  * Support for RLGC components (Resistors, Inductors, Capacitors, Conductors)
  * Support for Microwave components (Attenuators, Isolators, Splitters, Couplers)
  * Support for Simulation components (Port, Ground, Open)
* Type System
  * Explicit type field for all components
  * Frozen type literals to prevent modification
  * Automatic type validation during instantiation
  * Type-safe component conversion

### Validation & Safety
* Component Type Safety
  * Literal type fields for precise type checking
  * Immutable type definitions
  * Runtime type validation
  * Preserved type information during conversion
* Frequency Compatibility
  * Automatic validation of frequency points across components
  * Ensures consistent frequency ranges in circuit simulations
  * Early error detection for mismatched components
* Connection Management
  * Validates all network references before circuit creation
  * Supports flexible port connection specifications
  * Handles multi-port component connections
  * Maintains network naming consistency

### Integration Features
* Scikit-RF Compatibility
  * Bidirectional conversion with scikit-rf Circuit objects
  * Preserves network names and port assignments
  * Maintains S-parameter integrity during conversion
  * Automatic handling of component-specific conversions

## Component Models
### Base Features
* Tidy3d Base Model
  * Enhanced validation through Tidy3d's model system
  * Robust error handling and type checking
  * Consistent with Tidy3d's component architecture
* Common Attributes
  * Type identification field
  * Frequency specification
  * Port impedance configuration
  * Network conversion capabilities

### RLGC Components

* Type-Specific Features
  * R: Resistance with type='R'
  * L: Inductance with type='L'
  * G: Conductance with type='G'
  * C: Capacitance with type='C'
* Common Features
  * Frequency-dependent behavior
  * Port impedance specification (default 50Ω)
  * Automatic impedance normalization
  * Network conversion capabilities

### Microwave Components
* Attenuator (type='Attenuator')
  * dB/linear mode support
  * Delay parameter with ps/ns/deg units
  * Impedance matching validation
* Isolator (type='Isolator')
  * Bidirectional isolation (port 0/1)
  * Return loss verification
  * Reverse isolation >60dB
* Power Splitter (type='Splitter')
  * Multi-port configurations (3/4 ports)
  * Equal power division
  * Port impedance consistency
* Coupler (type='Coupler')
  * Coupling value in dB (auto-normalized)
  * Phase offset with auto-wrapping (0-360°)
  * Four-port configuration:
    * Port 0: Insertion
    * Port 1: Transmit
    * Port 2: Coupled
    * Port 3: Isolated

### Simulation Components
* Port (type='Port')
  * Named port termination
  * Perfect impedance matching
  * Automatic port attribute tagging
  * Ideal for circuit boundary definitions
* Ground (type='Ground')
  * Named ground termination
  * Perfect short circuit (S11 = -1)
  * Automatic ground attribute tagging
  * Ideal for circuit reference planes
* Open (type='Open')
  * Named open termination
  * Perfect open circuit (S11 = 1)
  * Automatic open attribute tagging
  * Ideal for stub terminations

## Component Integration
* Mixed Component Circuits
  * Type-safe integration of all component types:
    * RLGC (passive components)
    * Microwave (RF devices)
    * Simulation (terminations)
  * Automatic frequency point alignment
  * Consistent port numbering
  * Preserved component attributes and types

## Testing & Validation
* Component Tests

  * Type preservation verification
  * Network conversion validation
  * RLGC component functionality
  * Microwave component behavior
  * Impedance configuration validation
  * Default impedance behavior testing
* Simulation Component Tests
  * Port matching characteristics
  * Ground reflection coefficient
  * Open circuit verification
  * Type consistency checks
* Circuit Integration Tests
  * Mixed component type handling
  * Connection validation
  * Type safety verification
  * Attribute preservation

## Project Structure
Schema_skrf/
* Data/
  * Measurement datasets
  * Touchstone files
    * Calibration kits (3.5mm/2.92mm)
    * Device models (Transistor/SMD)
* Src/
  * Models/
    * Circuit.py (Circuit composition and validation)
    * Component.py (Component model definitions)
    * Network.py (Network parameter handling)
    * Microwave.py (Microwave components)
  * tests/
    * test_Circuit.py (Circuit integration tests)
    * test_Component.py (Component validation tests)
    * test_RLGC.py (Model validation suite)
    * test_Network.py (Network I/O tests)
    * test_Circuit.py (Circuit conversion tests)