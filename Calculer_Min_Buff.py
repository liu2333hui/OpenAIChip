
t = ["B", "N", "X", "Y", "KX", "KY", "I",] #mid ?
t = ["B", "N", "Y", "KY", "I","X", "KX", ] #min
#t = ["B", "N", "Y", "KY", "I","KX","X", ] #min
#t = ["KX","X","B", "N", "Y", "KY", "I", ] #max
#t = ["KX","X","B", "N", "Y", "KY", "I", ] #complex
t = ["B", "X", "N", "Y", "KY", "I","TXX", "KX", ] #min
t = ["B", "X", "N", "Y", "KY", "I","KX", "TXX", ] #min
t = ["B", "X", "N", "Y", "KY", "I","KX", "TXX", ] #min
t = ["B", "X", "N", "Y", "KY", "I","TXX", "KX", ] #min


t = ["B", "X","Y","N", "I","TYY", "KY", "TXX", "KX", ] #min
###1D_SYSTOLIC
###2D_SYSTOLIC

SYSTOLIC_VAR = "X"


def last_x(seq):
    for s in seq[::-1]:
        if(s == "TX" or s == "TXX" or s == "X" or s == "KX"):
            return s
    return ""

def last_y(seq):
    for s in seq[::-1]:
        if(s == "TY" or s == "TYY" or s == "Y" or s == "KY"):
            return s
    return ""



def scratchpad_size_1D_X(t, leaky_filter=False):
    SP = "1"

    seq = []
    for tt in t[::-1]:
        print(tt)
        der = last_x(seq)
        if(tt == "KX"):
            if("X" == der):
                print("-->", "SP ", SP)
                #SP += "*(X-1)"
            elif("TXX" == der):
                print("-->", "SP ", SP)
                #if("TXX" > "KX"):
                #SP += "*(TXX-1)"
            else:
                SP += "*(KX-1)"
                
            ##if("*X" in SP):
            #    SP += "//X*(X-1)"
            #    print("-->", "SP ", SP)
            #else:
            #    SP += "*" + "(KX-1)"

        elif(tt == "X"):
            if("TXX" == der):
                if(leaky_filter):
                    print("-->", "SP " , SP)
                SP += "//(TXX-1)*(X-1)"
            elif(der == "KX" and ("TXX" not in seq or leaky_filter)):
                print("-->", "SP ", SP)
                SP += "//(KX-1)*(X-1)"
            else:
                SP += "*(X-1)"
                
        elif(tt == "TXX"):
            if("KX" == der):
                print("-->", "SP ", SP)
                SP += "//(KX-1)*(KX+TXX-1)"
            else:
                SP += "*(TXX-1)"


            
        elif(tt == "TII" or tt == "I"):
            SP += "*" + tt
        elif(tt == "KY"):
            SP += "*" + tt
        elif(tt == "Y"):
            if("KY" in SP):
                SP += "//KY"
            SP += "*" + tt


        elif(tt == "N"):
            continue
        elif(tt == "B"):
            SP += "*" + tt
        '''             
        elif(tt == "X"):
            if("*(KX" in SP):
                print("-->", "SP ", SP)
            else:
                SP += "*X"
        elif(tt == "TXX"):
            SP += "*" + tt
        '''
        seq.append(tt)


def scratchpad_size_1D_Y(t, leaky_filter=False):
    SP = "1"

    seq = []
    for tt in t[::-1]:
        print(tt)
        dery = last_y(seq)

        if(tt == "KY"):
            if("Y" == dery):
                print("-->", "SP ", SP)
                #SP += "*(X-1)"
            elif("TYY" == dery):
                print("-->", "SP ", SP)
                #if("TXX" > "KX"):
                #SP += "*(TXX-1)"
            else:
                SP += "*(KY-1)"
        elif(tt == "Y"):
            #print(dery, tt, der == "KY")
            if("TYY" == dery):
                if(leaky_filter):
                    print("-->", "SP " , SP)
                SP += "//(TYY-1)*(Y-1)"
            elif(dery == "KY" and ("TYY" not in seq or leaky_filter)):
                print("-->", "SP ", SP)
                SP += "//(KY-1)*(Y-1)"
            else:
                SP += "*(Y-1)"
        elif(tt == "TYY"):
            if("KY" == dery):
                print("-->", "SP ", SP)
                SP += "//(KY-1)*(KY+TYY-1)"
            else:
                SP += "*(TYY-1)"


            
        elif(tt == "TII" or tt == "I"):
            SP += "*" + tt

            
        elif(tt == "KX"):
            SP += "*" + tt
        elif(tt == "TXX"):
            if("KX" in SP):
                SP += "//KX*(TXX+KX-1)"
        elif(tt == "X"):
            if("KX" in SP):
                SP += "//KX*X"
            elif("TXX" in SP):
                SP += "//TXX*X"
            SP += "*" + tt


        elif(tt == "N"):
            continue
        elif(tt == "B"):
            SP += "*" + tt
        seq.append(tt)

        

#Both X and Y can shift in the input side
def scratchpad_size_2D(t, leaky_filter=False):
    SP = "1"
    seq = []
    for tt in t[::-1]:
        print(tt)
        der = last_x(seq)
        dery = last_y(seq)
        if(tt == "KX"):
            if("X" == der):
                print("-->", "SP ", SP)
                #SP += "*(X-1)"
            elif("TXX" == der):
                print("-->", "SP ", SP)
                #if("TXX" > "KX"):
                #SP += "*(TXX-1)"
            else:
                SP += "*(KX-1)"
        elif(tt == "X"):
            if("TXX" == der):
                if(leaky_filter):
                    print("-->", "SP " , SP)
                SP += "//(TXX-1)*(X-1)"
            elif(der == "KX" and ("TXX" not in seq or leaky_filter)):
                print("-->", "SP ", SP)
                SP += "//(KX-1)*(X-1)"
            else:
                SP += "*(X-1)"
        elif(tt == "TXX"):
            if("KX" == der):
                print("-->", "SP ", SP)
                SP += "//(KX-1)*(KX+TXX-1)"
            else:
                SP += "*(TXX-1)"


        elif(tt == "KY"):
            if("Y" == dery):
                print("-->", "SP ", SP)
                #SP += "*(X-1)"
            elif("TYY" == dery):
                print("-->", "SP ", SP)
                #if("TXX" > "KX"):
                #SP += "*(TXX-1)"
            else:
                SP += "*(KY-1)"
        elif(tt == "Y"):
            #print(dery, tt, der == "KY")
            if("TYY" == dery):
                if(leaky_filter):
                    print("-->", "SP " , SP)
                SP += "//(TYY-1)*(Y-1)"
            elif(dery == "KY" and ("TYY" not in seq or leaky_filter)):
                print("-->", "SP ", SP)
                SP += "//(KY-1)*(Y-1)"
            else:
                SP += "*(Y-1)"
        elif(tt == "TYY"):
            if("KY" == dery):
                print("-->", "SP ", SP)
                SP += "//(KY-1)*(KY+TYY-1)"
            else:
                SP += "*(TYY-1)"

                

        elif(tt == "TII" or tt == "I"):
            SP += "*" + tt
        elif(tt == "N"):
            continue
        elif(tt == "B"):
            SP += "*" + tt
        seq.append(tt)

#Eyeriss-V1 Like
def scratchpad_size_diagonal(t, leaky_filter=False):
    pass

scratchpad_size_1D_Y(t)
print("------------------------")
scratchpad_size_1D_X(t)
print("-----------------------")
scratchpad_size_2D(t)
