# OSCAR: An Open-Source Comprehensive AI Accelerator Generator with Accurate Architectural Power Model

OSCAR is a comprehensive AI generator and accurate power estimator. It is comprised of several modules that allow for accurate modeling and generation of AI accelerators.
1. Primitive Generation (Chisel or Verilog)
2. ML power-based modeling (Python)
3. Power Estimation at Architectural Level (Python)
4. Architecture Analysis and Architecture Generation (Python/C++) --> Chisel or Verilog)
5. Simple Design Space Exploration based on surrogate models (Python)

Primitive generation involves configuration of chisel/verilog templates to generate the key building blocks of an AI accelerator hardware. ML power-based modeling refers to the modeling of each primitive and hardware module via ML methodologies using data-sensitive toggling features to capture detailed power variations due to data. Power estimation at the architectural level is the overall calculation of the power at the higher level, based on adding the sub-module powers. Architectural analysis and generation refers to the synthesis of AI accelerators at the core-level with automatic testbenchs. Simple Design Space Exploration refers to the search of designs within generatable designs to find the optimal performance and power AI accelerators.

Note: The code is in-preparation of finalization and cleaning and removal of any 3rd party IPs.

Here are several sample flows that OSCAR is capable of running:
## 1. Primitive Generation and Power Modeling Training
### Example1. How to create training data and use ML to model the power of the multiplier primitive
```
sbt "test:runMain multipliers.Multiplier2Spec"
python3 src/main/python/train_primitives.py Multiplier2 train
```

## 2. Power Inference
### Example1. For a testing sequence at the primitive-level
```
python3 src/main/python/train_primitives.py Multiplier2 test
```

### Example2. For an architecture
```
python3 src/main/python/SystolicConv.py
python3 src/main/python/SparseConv.py 
python3 src/main/python3/WinogradConv.py
```

## 3. Design Generation
### Testing Individual Primitives, for example a multiplier or adder or crossbar
```
sbt "test:runMain multipliers.Multiplier2Spec"
sbt "test:runMain adders.AdderN"
sbt "test:runMain networks.Crossbar"
```

### From a json file
```
python3 src/main/python/GenerateDesign.py arch.json
```

## 4. Design exploration, simple search method
### Multiple passes to find solutions at the Pareto Front
```
python3 src/main/python/DSE.py
python3 src/main/python/DSE_secondpass.py
python3 src/main/python/DSE_thirdpass.py
python3 src/main/python/DSE_fourthpass.py
python3 src/main/python/DSE_reconfig.py
```

Notes:
Because the paper uses confidential technologies (TSMC40), we do not provide the trained power models but do provide the scripts for generating power models.
