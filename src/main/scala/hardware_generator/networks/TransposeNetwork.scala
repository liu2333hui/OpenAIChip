package networks

//

//If the input is of shape (Tx, Ty, Tn)
//We want the output to be of shape (Tx, Tn, Ty)
//We simply do a wiring renaming
//This implementation is a static one (fixed wiring)
//For a dynamic, use "Crossbar"


