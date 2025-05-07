#Readme for OSCAR

OSCAR is a comprehensive AI generator and accurate power estimator. It is comprised of several modules that allow for accurate modeling and generation of AI accelerators.
1. Primitive Generation (Chisel or Verilog)
2. ML power-based modeling (Python)
3. Power Estimation at Architectural Level (Python)
4. Architecture Analysis and Architecture Generation (Python/C++) --> Chisel or Verilog)
5. Simple Design Space Exploration based on surrogate models (Python)

Here are several sample flows that OSCAR is capable of running:
1. Primitive Generation and Power Modeling Training
##Example1. How to create training data and use ML to model the power of the multiplier primitive
sbt "test:runMain multipliers.Multiplier2Spec"
python3 src/main/python/train_primitives.py Multiplier2 train

2. Power Inference
##Example1. For a testing sequence
python3 src/main/python/train_primitives.py Multiplier2 test

##Example2. For an architecture
python3 src/main/python/SystolicConv.py
python3 src/main/python/SparseConv.py 
python3 src/main/python3/WinogradConv.py

3. Design Generation
##From a json file
python3 src/main/python/GenerateDesign.py arch.json

4. Design exploration, simple search method
##Multiple passes to find solutions at the Pareto
python3 src/main/python/DSE.py
python3 src/main/python/DSE_secondpass.py
python3 src/main/python/DSE_thirdpass.py
python3 src/main/python/DSE_fourthpass.py
python3 src/main/python/DSE_reconfig.py

Notes:
Because the paper uses confidential technologies (TSMC40), we do not provide the trained power models but do provide the scripts for generating power models.
