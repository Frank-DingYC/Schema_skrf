# Schema_skrf Features

## Recent Updates

### JSON Schema Compatibility

* Replaced native complex type with ComplexNumber class for JSON Schema compatibility
* Updated z0 and z0_port fields to use ComplexNumber type
* Modified example values in Component and Media models
* Improved Circuit model serialization for JSON Schema generation

### Tutorial Enhancements

* Updated Network Tutorial with Python 3.12.0 compatibility
* Enhanced error handling for ArrayLike dimension mismatches
* Added new network visualization examples
* Improved code cell execution and output clarity
* Added comprehensive Component Tutorial
* Documented component usage and best practices

### Testing & Validation

* Added comprehensive media compatibility tests
* Enhanced component-media interaction validation
* Improved test stability for simulation components
* Added validation for component parameters and frequency matching

### Media Implementation

* Added comprehensive MicrostripLine implementation
* Enhanced media validation and parameter checks
* Added compatibility mode support
* Improved media parameter validation for transmission lines

### Component Enhancements

* Added type discrimination for all components
* Fixed component type preservation in Circuit model
* Improved impedance handling (default 50Ω)
* Enhanced z0 and z0_port validation
* Added support for 1D and 2D z0 arrays

### Integration

* Integrated with Tidy3d base model system
* Enhanced scikit-rf Circuit conversion
* Optimized Network instantiation
* Fixed network list handling

## Core Features

### Models

* Unified Component Interface
  * RLGC components (R, L, G, C)
  * Microwave components (Attenuators, Isolators, Splitters, Couplers)
  * Simulation components (Port, Ground, Open)
  * Seamless integration with Network models

* Type System
  * Explicit type fields with validation
  * Frozen type literals
  * Type-safe conversion

* Validation
  * Automatic parameter validation
  * Frequency point matching
  * Port connection verification

### Circuit Components

#### RLGC Components

* Basic Elements
  * Resistor (R): Resistance
  * Inductor (L): Inductance
  * Conductor (G): Conductance
  * Capacitor (C): Capacitance

* Features
  * Frequency-dependent behavior
  * Default 50Ω impedance
  * Automatic normalization

#### Microwave Components

* Attenuator
  * dB/linear modes
  * Configurable delay
  * Impedance matching

* Isolator
  * Bidirectional isolation
  * >60dB reverse isolation

* Power Splitter
  * 3/4 port configurations
  * Equal power division

* Coupler
  * dB coupling control
  * 0-360° phase offset
  * 4-port design

#### Simulation Components

* Port
  * Perfect impedance match
  * Circuit boundary definition

* Ground
  * Perfect short (S11 = -1)
  * Reference plane definition

* Open
  * Perfect open (S11 = 1)
  * Stub termination

## Media Support

### Transmission Line Types

* Types
  * Coaxial Line
    * Configurable diameters
    * Lossy conductor modeling
    * Dielectric loss support

  * Microstrip Line
    * Configurable dimensions
    * Multiple impedance models
    * Surface roughness effects
    * QUCS compatibility

  * Coplanar Waveguide
    * Configurable geometry
    * Substrate parameters
    * Loss modeling

  * Waveguides
    * Rectangular (RWG)
      * Flexible dimensions
      * TE/TM modes
    * Circular (CWG)
      * Variable radius
      * Mode control

### Material Properties

* Electromagnetic
  * Permittivity (εr)
  * Permeability (μr)
  * Loss tangent

* Physical
  * Conductor resistivity
  * Surface roughness

### Testing Framework

* Component Tests
  * Media compatibility
  * Port validation
  * Frequency response
  * Impedance matching

* Media Types
  * Coaxial Line
  * RWG/CWG
  * CPW/Microstrip
  * Distributed RLGC
  * Support for frequency-dependent impedance array compatibility

### Validation

* Parameters
  * Type checking
  * Range verification
  * Array validation

* Frequency
  * Point matching
  * Array consistency
  * Units and scaling

* Media
  * Type compatibility
  * Parameter validation
  * Conversion checks
  * Ground reflection coefficient
  * Open circuit verification
  * Type consistency checks

* Circuit Integration Tests
  * Mixed component type handling
  * Connection validation
  * Frequency alignment
  * Network conversion verification
  * Attribute preservation

## Project Structure

Schema_skrf/

* Data/
  * Touchstone/
    * Calibration data (Agilent_E5071B.s4p, RS_ZNB8.s4p)
    * Component models (LFCN-2352+, fet.s2p)
    * Test fixtures (various .sNp files)
    * Reference designs (splitters, couplers)
* Example/
  * Comparison.ipynb (Component comparison examples)
  * Network_Tutorial.ipynb (Network analysis and visualization examples)
  * Component_Tutorial.ipynb (Component usage and implementation guide)
* Src/
  * Models/
    * Circuit.py (Circuit composition and validation)
    * Component.py (Component model definitions)
    * Network.py (Network parameter handling)
    * Media.py (Media component definitions)
* Tests/
  * test_Circuit.py (Circuit integration tests)
  * test_Component.py (Component validation tests)
  * test_Network.py (Network I/O tests)