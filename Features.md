# Goal

1. Use the pydantic library to rewrite the Network and Circuit objects from scikit-rf library into Pydantic models so that they can be easily serialized/deserialized as JSON or other formats (like YAML). This will make it easier to work with these objects in Python scripts.
3. Based on the schema, we can convert the Json file to Python objects so that I can use scikit-rf library to do the other calculations.

## Enhanced Data Validation on Initialization
- Validates length parity of `frequency`, `s_parameters`, and `z0`.
- Ensures that `s_parameters` and `z0` align with the specified `nports`.
- Properly enforces validation during object initialization to catch invalid data, such as incorrect dimensions for `z0` or `s_parameters`, as tested in unit tests.

## Allow the user to do S-parameter cascade calculation
Adds the ability to perform S-parameter cascade calculations between multiple network objects, returning a new combined network. This optimizes network analysis and simplifies parts of the design process.

# Recent Changes
- Enhanced validation in `from_network` method of the `Network` class to handle inconsistencies in S-parameters, `z0`, and `nports`, ensuring accurate deserialization from scikit-rf networks.
- Rewrote the `__init__` function in the `Network` class to leverage Pydantic's built-in validation, ensuring robust data validation during initialization and passing unit tests for invalid data scenarios.

# File Architecture

1. The Data is used to store datasets used for test.
2. The Touchstone data is used to store the frequency response of a network object.
3. The Src is used to store those scripts.
4. The Tests is used to store test results and output from tests in the Python environment.

Here is the current file architecture:
- **SCHEMA_SKRF**
  - data
    - Touchstone
      - Agilant_E5071B.s4p
      - cst_example_4ports.s4p
      - cst_example_6ports_V2.s6p
      - cst_example_6ports_V2.ts
      - cst_example_6ports.s6p
      - designer_variable_coupler_ideal_20deg.s4p
      - designer_variable_coupler_ideal_75deg.s4p
      - designer_wilkinson_splitter.s3p
      - fet.s2p
      - hfss_18_2.s3p
      - hfss_19_2.s8p
      - hfss_19_2.s10p
      - hfss_oneport_powerwave.s1p
      - hfss_oneport.s1p
      - hfss_threeport_DB_500Mhm.s3p
      - hfss_threeport_DB.s3p
      - hfss_threeport_MA_500Mhm_without_gamma_20_500Mhm.s3p
      - hfss_threeport_MA.s3p
      - hfss_twoport.s2p
      - LFCN-2352+_Plus25degC.s2p
      - LFCN-2352+_Plus125degC.s2p
      - ntwk_noise_interp.s2p
      - ntwk_noise.s2p
      - ntwk1.s32p
      - ntwk1.s2p
      - ntwk2.s2p
      - ntwk3.s2p
      - ntwk4_n.s2p
      - ntwk4.s2p
      - RS_ZNB8.s4p
      - thru.s2p
  - Src
    - Models
      - Network.py
      - Circuit.py
  - Tests