
from power_models.AccumulatorPrimitive import AccumulatorPrimitive
from power_models.AdderNPrimitive import AdderNPrimitive
from power_models.Multiplier2Primitive import Multiplier2Primitive
from power_models.ConstantMultiplierPrimitive import ConstantMultiplierPrimitive
	

SBT = "/afs/ee.ust.hk/staff/ee/jaymok/.local/share/coursier/bin/sbt"


def test_sram():
	config = {
		"EDAVerification": true,
		"entry_bits": 16,
		"rows": 32,
		"sram_type": "Reg",	

	} 

if __name__ == "__main__":


	#SYSTOLIC UNIT

	#Assume an ideal case, all the hardware units can be sepeartely configured
	
	#Memory Wei

	primitive = "SRAMS"

	f'{SBT}  "test:runMain {primitive}SpecFromFile {TRACE_FILES} {JSON_FILE}"'



