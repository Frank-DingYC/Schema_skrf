# Goal

1. Use the pydantic library to rewrite the Network and Circuit objects from scikit-rf library into Pydantic models so that they can be easily serialized/deserialized as JSON or other formats (like YAML). This will make it easier to work with these objects in Python scripts.
3. Based on the schema, we can convert the Json file to Python objects so that I can use scikit-rf library to do the other calculations.

## 核心功能

### 网络参数支持
- S参数矩阵转换
- 阻抗参数(z0)处理
- 多端口网络验证

### 变更历史
2023-05-01：移除实验性噪声参数支持，优化基础转换逻辑稳定性

## Enhanced Data Validation on Initialization
- Validates length parity of `frequency`, `s_parameters`, and `z0`.
- Ensures that `s_parameters` and `z0` align with the specified `nports`.
- Properly enforces validation during object initialization to catch invalid data, such as incorrect dimensions for `z0` or `s_parameters`, as tested in unit tests.

## Allow the user to do S-parameter cascade calculation
Adds the ability to perform S-parameter cascade calculations between multiple network objects, returning a new combined network. This optimizes network analysis and simplifies parts of the design process.

# Recent Changes
- Enhanced validation in `from_network` method of the `Network` class to handle inconsistencies in S-parameters, `z0`, and `nports`, ensuring accurate deserialization from scikit-rf networks.
- Rewrote the `__init__` function in the `Network` class to leverage Pydantic's built-in validation, ensuring robust data validation during initialization and passing unit tests for invalid data scenarios.

## Directory Structure
```
Schema_skrf/
├── Data/
│   └── Touchstone/       # RF measurement datasets
│       ├── Agilent_E5071B.s4p
│       ├── cst_example_4ports.s4p
│       ├── hfss_twoport.s2p
│       └── ...30+ .s*p files
├── Src/
│   ├── Models/
│   │   ├── Network.py    # RF network model
│   │   └── Circuit.py   # Circuit analysis
│   └── tests/           # Unit tests
└── Features.md          # This documentation
```

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

## Core Components
- **Network.py**: Implements S-parameter validation and frequency domain analysis
- **Test files**: Pytest-based validation suite