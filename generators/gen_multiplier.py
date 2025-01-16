def analyze_floating(supported_dtypes):
    float_d = []


    P = 0
    E = 0
    M = 0
    
    
    for dt in supported_dtypes:
        if("FP" in dt):
            PREC = int(dt.split("FP")[1])
            
            #posits
            if("P" == dt[0] and "E" in dt and "M" in dt):
                P = int(dt.split("P")[1].split("E")[0])
                E = int(dt.split("E")[1].split("M")[0])
                M = int(dt.split("M")[1].split("_")[0])
                
            #floating exponent e mantissa
            elif("E" in dt and "M" in dt):
                P = 0
                E = int(dt.split("E")[1].split("M")[0])
                M = int(dt.split("M")[1].split("_")[0])
            elif("M" in dt):
                P = 0
                M = int(dt.split("M")[1].split("_")[0])
                E = PREC - M
            #special cas
            elif("FP16" == dt):
                P = 0
                E = 5
                M = 10
            elif("BFP16" == dt):
                P = 0
                E = 8
                M = 7
            elif("FP32" == dt):
                P = 0
                E = 8
                M = 23
            elif("FP8" == dt):
                P = 0
                E = 3
                M = 4
            else:
                print("unsupported floating")
            #sign, posit regime, exponent, fraction
            float_d.append([1, P,E,M, PREC])
    return float_d

def analyze_int(supported_dtypes):
    int_d = []

    for dt in supported_dtypes:
        if("INT" in dt):
            int_d.append(int(dt.split("INT")[1]))

    return int_d

def max_floating_props(analyze):
    Ps = []
    Es = []
    Ms = []
    for sign, P, E, M, PREC in analyze:
        Ps.append(P)
        Es.append(E)
        Ms.append(M)

    return max(Ps), max(Es), max(Ms)
    
def gen_multiplier(hardware_config, meta_config, macro_config):

    
    if("WINOGRAD" in [hardware_config["TILINGS"]["CONV2D"][df]["DATAFLOW"] for df in hardware_config["TILINGS"]["CONV2D"]]):\
        WINOGRAD_EN = True
    else:
        WINOGRAD_EN = False


    if(WINOGRAD_EN):
        WEI_NAME = "WINO_MAX_WEI_PRECISION_INT"
        ACT_NAME = "WINO_MAX_ACT_PRECISION_INT"
    else:
        WEI_NAME = "MAX_WEI_PRECISION_INT"
        ACT_NAME = "MAX_ACT_PRECISION_INT"        
        
    print("\n// GEN_MULTIPLIER VERILOG\n")

    f = open(meta_config["dossier"]+"/multiplier.v", "w")
    s = ""

    if(hardware_config["MULT_TYPE_INT"] not in ["BITFUSION_TXTY_TN","ADAPTIVE_TXTY_TN", "ADAPTIVE_OUTER"]):
        s += "module MULT_INT(\n\
                input clk,\n\
                input rst_n,\n\
                input en, //power gating\n\
                            \n\
                input [5:0] wei_precision, // 4, 8, 16, 32 assumed to be max, not going to go to 64 or more\n\
                input [5:0] act_precision, // 4, 8, 16, 32 \n\
                    input signed [`"+WEI_NAME+"-1:0] jia,\n\
                    input signed [`"+ACT_NAME+"-1:0] yi,\n\
                    output reg signed [(`"+WEI_NAME+"+`"+ACT_NAME+") - 1: 0] zi,\n\
                            \n\
                input valid,//data is valid and ready for processing\n\
                output reg ready, // data is ready and multiplied , because at most 16/2 cycles\n\
                            \n\
                output reg last, \n\
                output reg start, \n\
                            \n\
                input pe_all_ready\n\
        );\n"

    
    #1. Basic Multiplier
    #there is no bit adaptation at all here ! only bit padding
    if(hardware_config["MULT_TYPE_INT"] == "BASIC"):
        if( macro_config["MAX_WEI_PRECISION_INT"] != 0 and macro_config["MAX_ACT_PRECISION_INT"] != 0):

            '''
            s += "//Basic multiplier  \n\
                module MULT_INT(\n\
                    input clk,\n\
                    input rst_n,\n\
                    input en, //power gating\n\
                        \n\
                    input [5:0] wei_precision, // 4, 8, 16, 32 assumed to be max, not going to go to 64 or more\n\
                    input [5:0] act_precision, // 4, 8, 16, 32 \n\
                    input signed [`"+WEI_NAME+"-1:0] jia,\n\
                    input signed [`"+ACT_NAME+"-1:0] yi,\n\
                    output reg signed [(`"+WEI_NAME+"+`"+ACT_NAME+") - 1: 0] zi,\n\
                        \n\
                    input valid,//data is valid and ready for processing\n\
                    output reg ready, // data is ready and multiplied , because at most 16/2 cycles\n\
                    output reg last\n\
                    );\n"
            '''
            s += "            \n\
                        always@(posedge clk or negedge rst_n) begin\n\
                            last <= rst_n;\n\
                        end\n\
                        //assign last = rst_n;    \n\
                        \n\
                   //Precision is un-used\n\
                   wire clk_gate;\n\
                   assign clk_gate = en & clk;\n\
                   always@(posedge clk_gate or negedge rst_n) begin\n\
                       if (~rst_n) begin\n\
                           ready <= 0;\n\
                           zi <= 0;\n\
                           //last <= 0;\n\
                       end  else begin\n\
                          if(valid) begin\n\
                           zi <= jia * yi; // Most simple implementation, but most costly in PPA\n\
                           ready <= 1;\n\
                           //last <= 1;\n\
                          end else  begin\n\
                           zi <= zi;\n\
                           ready <= 0; \n\
                           //last <=0;\n\
                          end \n\
                       end \n\
                   end\n\
                endmodule\n"

    #Multiplier characteristics
    #Pipeline = False/True, Mult_Cycles = 8/Act/Wei/ActWei/Act_non_zero/..., Shift = Act or Wei
    elif(hardware_config["MULT_TYPE_INT"] == "UNIVERSAL_SERIAL_MULT"):
        RADIX = str(hardware_config["MULT_TYPE_INT_META"]["RADIX"])
        MULTICANT = hardware_config["MULT_TYPE_INT_META"]["MULTICANT"]
        PIPELINE =  hardware_config["MULT_TYPE_INT_META"]["PIPELINE"] #TODOS
        BIT_STRIPE_ZEROS=  hardware_config["MULT_TYPE_INT_META"]["BIT_STRIPE_ZEROS"] #TODOS

        '''
        s += "//Shifter Multiplier  \n\
                module MULT_INT(\n\
                    input clk,\n\
                    input rst_n,\n\
                    input en, //power gating\n\
                        \n\
                    input [5:0] wei_precision, // 4, 8, 16, 32 assumed to be max, not going to go to 64 or more\n\
                    input [5:0] act_precision, // 4, 8, 16, 32 \n\
                    input signed [`MAX_WEI_PRECISION_INT-1:0] jia,\n\
                    input signed [`MAX_ACT_PRECISION_INT-1:0] yi,\n\
                    output reg signed [(`MAX_WEI_PRECISION_INT+`MAX_ACT_PRECISION_INT) - 1: 0] zi,\n\
                        \n\
                    input valid,//data is valid and ready for processing\n\
                    output reg ready, // data is ready and multiplied , because at most 16/2 cycles\n\
                        \n\
                        output reg last, \n\
                        output reg start, \n\
                        \n\
                      input pe_all_ready\n\
                    );\n\
                        \n\
        '''


        #3 states
        #1. stalling, working
        s += "reg [2:0] state;\n" 
        s += "`define TING 0\n"
        s += "`define GONG 1\n"

        s += "reg [5:0] qi;\n"

        s += "reg signed [(`MAX_WEI_PRECISION_INT+`MAX_ACT_PRECISION_INT) - 1: 0] cheng;\n"
        s += "reg signed [(`MAX_WEI_PRECISION_INT+`MAX_ACT_PRECISION_INT) - 1: 0] cheng2;\n"
        s += "reg double_buffer_id;\n"
  
                        
        s += "//Precision is un-used\n\
                   reg  clk_gate;\n\
                always@(*) begin\n\
                        clk_gate = en & clk;\n\
                   end\n"

        s += "reg valid_;\n"
        s += "always@(*) begin\n\
                valid_ <= valid;\n\
              end\n"

        if(hardware_config["MULT_TYPE_INT_META"].get("DOUBLE_BUFFER_OUTPUT", True)):

            corrected_len = "0"
        else:
            corrected_len = "1"
        
        if(BIT_STRIPE_ZEROS == "NONE"):
            if(MULTICANT == "ACT"):
                #act is shifted
                s += "wire signed [`MAX_ACT_PRECISION_INT-1:0] yin = yi;\n"
                s += "wire signed [`MAX_WEI_PRECISION_INT-1:0] shu = jia;\n"
                s += "wire [5:0] zhou = act_precision+"+corrected_len+";\n"
                
                s += "wire [5:0] stripe_zhou = act_precision+"+corrected_len+";\n"
                s += "wire [5:0] stripe_zhou_ = act_precision+"+corrected_len+";\n"
                
            else:
                #default to weight
                s += "wire signed[`MAX_ACT_PRECISION_INT-1:0] shu = yi;\n"
                s += "wire signed[`MAX_WEI_PRECISION_INT-1:0] yin = jia;\n"
                s += "wire [5:0] zhou = wei_precision+"+corrected_len+";\n"

                
                s += "wire [5:0] stripe_zhou = wei_precision+"+corrected_len+";\n"
                s += "wire [5:0] stripe_zhou_ = wei_precision+"+corrected_len+";\n"
                
        elif(BIT_STRIPE_ZEROS == "SINGLE"):
            if(MULTICANT == "ACT"):
                #default to act
                s += "wire signed[`MAX_WEI_PRECISION_INT-1:0] shu = jia;\n"
                s += "wire signed[`MAX_ACT_PRECISION_INT-1:0] yin = yi;\n"
                s += "reg [5:0] stripe_zhou;\n"
                s += "reg [5:0] stripe_zhou_;\n"
                s += "reg [5:0] stripe_zhou_zhou;\n"
                
                stripe_terms = []
                #print(macro_config["MAX_WEI_PRECISION_INT"])
                for idx,i in enumerate( range(1, macro_config["MAX_ACT_PRECISION_INT"]+1)):
                    s += "wire stripe_"+str(idx)+" = (yin[`MAX_ACT_PRECISION_INT-1:"+str(idx)+"] == 0);"
                    stripe_terms.append("stripe_"+str(idx))

                s += "always@(*) begin\n\
                        if(yin == 0) stripe_zhou <= 1;\n"
                for idx,i in enumerate(range(1,macro_config["MAX_ACT_PRECISION_INT"]+1)):
                    s += "else if(stripe_"+str(idx)+") stripe_zhou <= "+str(idx)+"+"+corrected_len+";\n"
                s += "else stripe_zhou <= "+str(idx)+"+"+corrected_len+";\n"
                s += "end\n"


                
                s += "always@(posedge clk_gate or negedge rst_n) begin\n\
                        if(~rst_n) stripe_zhou_ <= 0;\n\
                        else begin \n\
                        if(qi == 0 | pe_all_ready) begin\n\
                         stripe_zhou_<=stripe_zhou;\n\
                      end\n\
                      end\n\
                      end\n"
                s += "wire [5:0] zhou = act_precision+"+corrected_len+";\n"
                
            else:
                #default to weight
                s += "wire signed[`MAX_ACT_PRECISION_INT-1:0] shu = yi;\n"
                s += "wire signed[`MAX_WEI_PRECISION_INT-1:0] yin = jia;\n"
                s += "reg [5:0] stripe_zhou;\n"
                s += "reg [5:0] stripe_zhou_;\n"
                s += "reg [5:0] stripe_zhou_zhou;\n"
                
                stripe_terms = []
                #print(macro_config["MAX_WEI_PRECISION_INT"])
                for idx,i in enumerate( range(1, macro_config["MAX_WEI_PRECISION_INT"]+1)):
                    s += "wire stripe_"+str(idx)+" = (yin[`MAX_WEI_PRECISION_INT-1:"+str(idx)+"] == 0);"
                    stripe_terms.append("stripe_"+str(idx))

                s += "always@(*) begin\n\
                        if(yin == 0) stripe_zhou <= 1;\n"
                for idx,i in enumerate(range(1,macro_config["MAX_WEI_PRECISION_INT"]+1)):
                    s += "else if(stripe_"+str(idx)+") stripe_zhou <= "+str(idx)+"+"+corrected_len+";\n"
                s += "else stripe_zhou <= "+str(idx+1)+"+"+corrected_len+";\n"
                s += "end\n"


                
                s += "always@(posedge clk_gate or negedge rst_n) begin\n\
                        if(~rst_n) stripe_zhou_ <= 0;\n\
                        else begin \n\
                        if(qi == 0 | pe_all_ready) begin\n\
                         stripe_zhou_<=stripe_zhou;\n\
                      end\n\
                      end\n\
                      end\n"
                s += "wire [5:0] zhou = wei_precision +"+corrected_len+";\n"
                
        else:#DUAL
            s += "reg sel_yin;\n"
            
            s += "wire signed [(`MAX_WEI_PRECISION_INT+`MAX_ACT_PRECISION_INT) - 1: 0] shu = sel_yin ? yi : jia;\n"
            s += "wire signed [(`MAX_WEI_PRECISION_INT+`MAX_ACT_PRECISION_INT) - 1: 0] yin = sel_yin ? jia: yi;\n"

            #(TODOS)
                
        s += "reg  signed [(`MAX_WEI_PRECISION_INT+`MAX_ACT_PRECISION_INT) - 1: 0] shift_yin;\n"
        s += "reg  signed [(`MAX_WEI_PRECISION_INT+`MAX_ACT_PRECISION_INT) - 1: 0] shift_shu;\n"


        #SIGN TREATMENT
        

        #radix = 1
        s += "always@(*) begin\n\
                  last <= ("+RADIX+"+"+corrected_len+">=zhou)? 1 : ~(qi==0)&((stripe_zhou_<=2)?  stripe_zhou<=2? 1 :  ~ready  :  ((("+RADIX+">=zhou)?  1 : (qi+2*"+RADIX +" >= zhou) | qi + 2*"+RADIX+" >= stripe_zhou_)) & ~pe_all_ready);\n\
                  ready <=  (qi + "+RADIX +" >= zhou | ((stripe_zhou_ <=2)?  qi + "+RADIX+" >= stripe_zhou_ : qi + "+RADIX+" >= stripe_zhou_)) & (state == `GONG);\n"

        if(hardware_config["MULT_TYPE_INT_META"].get("DOUBLE_BUFFER_OUTPUT", True)):
            s += "    zi <=  double_buffer_id ?  cheng2 : cheng;\n"
        else:
            s += "    zi <= cheng;\n"
        
        s += "    start <= (qi == 0 );//| qi + "+RADIX +" >= zhou );\n\
              end\n"


        s += "reg init;\n"

        #
        if(hardware_config["MULT_TYPE_INT_META"].get("DOUBLE_BUFFER_OUTPUT", True)):
            s += "always@(posedge clk or negedge rst_n) begin\n\
                    if(~rst_n) double_buffer_id <= 0;\n\
                    else begin\n\
                        if(pe_all_ready) double_buffer_id <=  ~double_buffer_id ;\n\
                  end\n\
                  end\n"
            
        
        s += "always@(posedge clk_gate or negedge rst_n) begin\n\
                       if (~rst_n) begin\n\
                           state <= `TING;\n\
                           qi <= 0;\n\
                           double_buffer_id <= 0;\n\
                       end  else begin\n\
                           if(state == `TING) begin \n\
                                if(valid_) begin \n\
                                    if(qi + "+RADIX+" == zhou | qi + "+RADIX+" >= stripe_zhou) begin \n\
                                        state <=  `GONG;\n\
                                        shift_yin <= (yin >> "+RADIX +");\n\
                                        shift_shu <= (shu << "+RADIX +");\n\
                                        cheng <= yin["+RADIX+"-1:0] * shu ;\n\
                                    end else begin \n\
                                        cheng <= yin["+RADIX+"-1:0] * shu ;\n\
                                        shift_yin <= (yin >> "+RADIX +");\n\
                                        shift_shu <= (shu << "+RADIX +");\n\
                                        qi <= qi + "+RADIX +";\n\
                                        state <= `GONG;\n\
                                    end\n\
                                end\n\
                            end else if(state == `GONG) begin\n\
                                //$display(888,(qi + "+RADIX+" == zhou) | (qi + "+RADIX+" >= stripe_zhou_));\n\
                                //if(  (qi == zhou)  |    (qi >= stripe_zhou_)  )begin\n\
                                    if(pe_all_ready) begin\n\
                                        //$display(233);\n\
                                        cheng <= yin["+RADIX+"-1:0] * shu ;\n\
                                        shift_yin <= (yin >> "+RADIX +");\n\
                                        shift_shu <= (shu << "+RADIX +");\n\
                                        qi <= 0 + "+RADIX +";\n\
                                    //end else begin\n\
                                        //qi <= 0;\n\
                                       // state <= `TING;\n\
                                        //shift_yin <= (yin >> "+RADIX +");\n\
                                        //shift_shu <= (shu << "+RADIX +");\n\
                                    //end\n\
                                end else begin \n\
                                    if(qi == 0) begin\n\
                                       //$display(666);\n\
                                        cheng <= yin["+RADIX+"-1:0] * shu ;\n\
                                        shift_yin <= yin >> "+RADIX +";\n\
                                        shift_shu <= shu << "+RADIX +";\n\
                                        qi <= 0 + "+RADIX +";\n\
                                    end else if((qi + "+RADIX+" == zhou-"+corrected_len+")) begin\n"
        if(hardware_config["MULT_TYPE_INT_META"].get("SIGN_MODE", "SERIAL") == "SERIAL"):
            #print(RADIX)
            if(int(RADIX) == 1):
                s +="                   cheng <= -shift_yin["+RADIX+"-1:0]*shift_shu + cheng ;\n"
            else:
                s +="                   cheng <= -(1<<("+RADIX+"-1))*shift_yin["+RADIX+"-1:"+RADIX+"-1]*shift_shu + shift_yin["+RADIX+"-2:0]*shift_shu+ cheng ;\n"
            
        s += "\
                                        shift_yin <= shift_yin >> "+RADIX +";\n\
                                        shift_shu <= shift_shu << "+RADIX +";\n\
                                        qi <= qi + "+RADIX +";\n\
                                    end else begin\n\
                                    //$display(555);\n\
                                        cheng <= shift_yin["+RADIX+"-1:0]*shift_shu + cheng ;\n\
                                        shift_yin <= shift_yin >> "+RADIX +";\n\
                                        shift_shu <= shift_shu << "+RADIX +";\n\
                                        qi <= qi + "+RADIX +";\n\
                                    end\n\
                                end\n\
                            end\n\
                        end\n\
                    end\n"
                            

        s += "endmodule\n"
        
    #Pipeline = False     , Radix = 1,     bit_stripe_zeros:None         , Multicant = Act/wei
    elif(hardware_config["MULT_TYPE_INT"] == "SHIFT_ACCUMULATE"):

        '''
        s += "//Shift Accumulate  \n\
                module MULT_INT(\n\
                    input clk,\n\
                    input rst_n,\n\
                    input en, //power gating\n\
                        \n\
                    input [5:0] wei_precision, // 4, 8, 16, 32 assumed to be max, not going to go to 64 or more\n\
                    input [5:0] act_precision, // 4, 8, 16, 32 \n\
                    input signed [`MAX_WEI_PRECISION_INT-1:0] jia,\n\
                    input signed [`MAX_ACT_PRECISION_INT-1:0] yi,\n\
                    output reg signed [(`MAX_WEI_PRECISION_INT+`MAX_ACT_PRECISION_INT) - 1: 0] zi,\n\
                        \n\
                    input valid,//data is valid and ready for processing\n\
                    output reg ready, // data is ready and multiplied , because at most 16/2 cycles\n\
                        \n\
                        output reg last \n\
                    );\n"
        '''
        s += "\n\
                   //Precision is un-used\n\
                   wire clk_gate;\n\
                   assign clk_gate = en & clk;\n"
        if(hardware_config["MULT_TYPE_INT_META"]["MULTICANT"] == "ACT"):
            #act is shifted
            s += "wire [`MAX_ACT_PRECISION_INT-1:0] yin = yi;\n"
            s += "wire [`MAX_WEI_PRECISION_INT-1:0] shu = jia;\n"

            s += "wire zhou = act_precision;\n"
        else:
            #default to weight
            s += "wire [`MAX_ACT_PRECISION_INT-1:0] shu = yi;\n"
            s += "wire [`MAX_WEI_PRECISION_INT-1:0] yin = jia;\n"

            s += "wire [5:0] zhou = wei_precision;\n"


        s += "reg  [(`MAX_WEI_PRECISION_INT+`MAX_ACT_PRECISION_INT) - 1: 0] shift_yin;\n"
        s += "reg  [(`MAX_WEI_PRECISION_INT+`MAX_ACT_PRECISION_INT) - 1: 0] shift_shu;\n"
        
        #3 states
        #1. stalling, working
        s += "reg [2:0] state;\n" 
        s += "`define TING 0\n"
        s += "`define GONG 1\n"

        s += "reg [5:0] qi;\n"

        s += "reg [(`MAX_WEI_PRECISION_INT+`MAX_ACT_PRECISION_INT) - 1: 0] cheng;\n"

        #radix = 1
        s += "always@(*) begin\n\
                  last = (qi+2*1 == zhou);\n\
                  ready = (qi + 1 == zhou);\n\
                  zi = cheng;\n\
              end\n"
        
        s += "always@(posedge clk_gate or negedge rst_n) begin\n\
                       if (~rst_n) begin\n\
                           //ready <= 0;\n\
                           //zi <= 0;\n\
                           state <= `TING;\n\
                           qi <= 0;\n\
                       end  else begin\n\
                           if(state == `TING) begin \n\
                                if(valid) begin \n\
                                    if(qi + 1 == zhou) begin \n\
                                        state = state;\n\
                                        cheng <= yin[0] ? shu : 0 ;\n\
                                    end else begin \n\
                                        cheng <= yin[0] ? shu : 0 ;\n\
                                        shift_yin <= yin >> 1;\n\
                                        shift_shu <= shu << 1;\n\
                                        qi <= qi + 1;\n\
                                        state <= `GONG;\n\
                                    end\n\
                                end\n\
                            end else if(state == `GONG) begin\n\
                                if(qi + 1 == zhou)begin\n\
                                    if(valid) begin\n\
                                        cheng <= yin[0] ? shu : 0 ;\n\
                                        shift_yin <= yin >> 1;\n\
                                        shift_shu <= shu << 1;\n\
                                        qi <= 0;\n\
                                    end else begin\n\
                                        qi <= 0;\n\
                                        state <= `TING;\n\
                                    end\n\
                                end else begin \n\
                                    cheng <= shift_yin[0] ? cheng+shift_shu : cheng ;\n\
                                    shift_yin <= shift_yin >> 1;\n\
                                    shift_shu <= shift_shu << 1;\n\
                                    qi <= qi + 1;\n\
                                end\n\
                            end\n\
                        end\n\
                    end\n"
                            
        s += "endmodule\n"



    
    elif(hardware_config["MULT_TYPE_INT"] == "SHIFT_ACCUMULATE_PIPELINE"):
        pass
    elif(hardware_config["MULT_TYPE_INT"] == "BOOTH"):
        pass
    elif(hardware_config["MULT_TYPE_INT"] == "BOOTH_PIPELINE"):
        pass
    elif(hardware_config["MULT_TYPE_INT"] == "BIT_SERIAL"):
        pass
    elif(hardware_config["MULT_TYPE_INT"] in "BIT_PARALLEL"):
        pass

    #another adaptive allows 1 16x16, 4 8x8 (tiling along Tx + Tn), much more flexible !
    elif(hardware_config["MULT_TYPE_INT"] in ["BITFUSION_TXTY_TN","ADAPTIVE_TXTY_TN", "ADAPTIVE_OUTER"]):
    
        if( macro_config["MAX_WEI_PRECISION_INT"] != 0 and macro_config["MAX_ACT_PRECISION_INT"] != 0):
            
            if(macro_config["MIN_WEI_PRECISION_INT"] != 0):
                wei_ratio_int = macro_config["MAX_WEI_PRECISION_INT"]//macro_config["MIN_WEI_PRECISION_INT"]
            if(macro_config["MIN_ACT_PRECISION_INT"] != 0):
                act_ratio_int = macro_config["MAX_ACT_PRECISION_INT"]//macro_config["MIN_ACT_PRECISION_INT"]

            wei_int = analyze_int(hardware_config["SUPPORTED_WEI_DTYPES"])
            act_int = analyze_int(hardware_config["SUPPORTED_ACT_DTYPES"])

        
            #if(MULT_TYPE_UNIT = "BOOTH", "WALLACE", "。。。" (TODOS)
            s += "//Unit multiplier - minimum precision as unit \n\
                module MIN_PREC_MULT_INT(\n\
                    input clk,\n\
                    input rst_n,\n\
                    input en,\n\
                    input  [`MIN_WEI_PRECISION_INT-1:0] jia,\n\
                    input  [`MIN_ACT_PRECISION_INT-1:0] yi,\n\
                  output reg  [(`MIN_WEI_PRECISION_INT+`MIN_ACT_PRECISION_INT)-1:0] zi,\n\
                     input valid,\n\
                    output reg ready\n\
                    );\n\
                           //Precision is un-used\n\
                       wire clk_gate;\n\
                       assign clk_gate = en & clk;\n\
                       always@(posedge clk_gate or negedge rst_n) begin\n\
                           if (~rst_n) begin\n\
                               ready <= 0;\n\
                               zi <= 0;\n\
                           end  else begin\n\
                              if(valid) begin\n\
                               zi <= jia * yi; // Most simple implementation, but most costly in PPA\n\
                               ready <= 1;\n\
                              end else  begin\n\
                               zi <= zi;\n\
                               ready <= 0; \n\
                              end \n\
                           end \n\
                       end\n\
                "
            s += "endmodule\n"

            #(TODOS) WINOGRAD ADAPTIVE ? Tricky case.
            s += "//Basic multiplier  \n\
                module MULT_INT(\n\
                        input clk,\n\
                        input rst_n,\n\
                        input en, //power gating\n\
                        input [5:0] wei_precision, // 4, 8, 16, 32 assumed to be max, not going to go to 64 or more\n\
                        input [5:0] act_precision, // 4, 8, 16, 32 \n\
                    input signed [`"+WEI_NAME+"-1:0] jia,\n\
                    input signed [`"+ACT_NAME+"-1:0] yi,\n\
                    output reg signed [("+str(wei_ratio_int)+"*`MIN_WEI_PRECISION_INT+"+str(act_ratio_int)+"*`MIN_ACT_PRECISION_INT) - 1: 0] zi,\n"
            '''
                        input signed [`MAX_WEI_PRECISION_INT-1:0] jia,\n\
                        input signed [`MAX_ACT_PRECISION_INT-1:0] yi,\n"
            s +=  "     output reg   [ ("+str(wei_ratio_int)+"*`MIN_WEI_PRECISION_INT+"+str(act_ratio_int)+"*`MIN_ACT_PRECISION_INT) - 1: 0] zi,\n"
            #            output reg  [`MAX_PSUM_PRECISION_INT  - 1: 0] zi,\n\     
            '''
            s += "     input valid,//data is valid and ready for processing\n\
                        output reg ready // data is ready and multiplied , because at most 16/2 cycles\n\
                        );\n"

            s += " reg [`MAX_WEI_PRECISION_INT-1:0] jia_natural;\n"
            s += " reg [`MAX_ACT_PRECISION_INT-1:0] yi_natural;\n"

            #change +/- ---> +
            s += "always@(*) begin\n"
            for w in wei_int:
                for a in act_int:
                    w_ratio = macro_config["MAX_WEI_PRECISION_INT"]//w
                    a_ratio = macro_config["MAX_ACT_PRECISION_INT"]//a
                    s += "if( act_precision == " + str(a) + " &&  wei_precision == " + str(w) + ") begin\n"
                    for i in range(w_ratio):
                        s+="jia_natural[("+str(i)+"+1)*"+str(w)+"-1:"+str(i)+"*"+str(w)+"] =(jia[("+str(i)+"+1)*"+str(w)+"-1]== 0)?  jia[("+str(i)+"+1)*"+str(w)+"-1:"+str(i)+"*"+str(w)+"] : -jia[("+str(i)+"+1)*"+str(w)+"-1:"+str(i)+"*"+str(w)+"];\n"
                    for i in range(a_ratio):
                        s+="yi_natural[("+str(i)+"+1)*"+str(a)+"-1:"+str(i)+"*"+str(a)+"] =(yi[("+str(i)+"+1)*"+str(a)+"-1] == 0)?  yi[("+str(i)+"+1)*"+str(a)+"-1:"+str(i)+"*"+str(a)+"] : -yi[("+str(i)+"+1)*"+str(a)+"-1:"+str(i)+"*"+str(a)+"];\n"
                    s+="end\n"
            s += "end\n"
            
                        
            #s += " assign jia_natural = jia"
            psum_ready = []
            for l in range(act_ratio_int):
                for k in range(wei_ratio_int):
                    no = str(l)+"_"+str(k)
                    s += "    wire [(`MIN_WEI_PRECISION_INT + `MIN_ACT_PRECISION_INT)-1:0] psum_"+no+";\n"
                    s += "    wire psum_ready_"+no+";\n"
                    s += "    MIN_PREC_MULT_INT mpmi_"+no+"(.clk(clk),.rst_n(rst_n), .en(en), .jia(jia_natural[`MIN_ACT_PRECISION_INT*"+str((k+1))+"-1:`MIN_WEI_PRECISION_INT*"+str(k)+"]), \
                                    .yi(yi_natural[`MIN_ACT_PRECISION_INT*"+str((l+1))+"-1:`MIN_ACT_PRECISION_INT*"+str(l)+"]), .zi(psum_"+no+"), .valid(valid), .ready(psum_ready_"+no+"));\n"
                    

                    psum_ready.append("psum_ready_"+no)
            s += "always@(posedge clk) begin\n"
            s += " ready = " + "&".join(psum_ready) + ";\n"
            s += "end\n"
            
            s += " reg [  "+str(act_ratio_int)+"*"+str(wei_ratio_int)+"*(`MIN_WEI_PRECISION_INT+`MIN_ACT_PRECISION_INT) - 1: 0] zi_natural;\n"
            s += "always@(*) begin\n"
            for w in wei_int:
                for a in act_int:
                    w_ratio = macro_config["MAX_WEI_PRECISION_INT"]//w
                    a_ratio = macro_config["MAX_ACT_PRECISION_INT"]//a

                    w_blocks =(w//macro_config["MIN_WEI_PRECISION_INT"])
                    a_blocks = (a//macro_config["MIN_ACT_PRECISION_INT"])

                    


                    s += "if( act_precision == " + str(a) + " &&  wei_precision == " + str(w) + ") begin\n"
                    equationes = ""#"zi_natural = "
                    terms = [[] for i in range(w_ratio*a_ratio)] #TN TX/TY order
                    for l in range(act_ratio_int):
                        for k in range(wei_ratio_int):
                            no = str(l)+"_"+str(k)
                            terms[a_ratio*(k // w_blocks)     +      (l // a_blocks)].append( "(psum_"+no + " << " + str( (l % a_blocks ) * macro_config["MIN_ACT_PRECISION_INT"]   +   (k% w_blocks )*macro_config["MIN_WEI_PRECISION_INT"]) +")")
                    #print(a,w)#l // a_blocks  == k // w_blocks
                    #print(terms)
                    zi_res = []
                    #for i in range(a_ratio):
                    #    for j in range(w_ratio):
                    #        zi_res.append("+".join(terms[i*a_blocks*w_blocks: (i+1)*a_blocks*w_blocks]))
                    for idx,t in enumerate(terms):
                        #zi_res.append("+".join(t))
                        equationes += "zi_natural[("+str(idx)+"+1)*"+str(w+a)+"-1:"+str(idx)+"*"+str(w+a)+"] = "+"+".join(t)+" ;\n"
                    #equationes += ";\n"
                    s += equationes
                    s += "end\n"

            s += "end\n"
            #zi_natural -> zi, (-) to (+)

            for i in range(8):
                for j in range(8):
                    s+= "reg sign_"+str(i)+"_"+str(j)+";\n"

            s += "always@(posedge clk) begin\n"
            for w in wei_int:
                for a in act_int:
                    w_ratio = macro_config["MAX_WEI_PRECISION_INT"]//w
                    a_ratio = macro_config["MAX_ACT_PRECISION_INT"]//a
                    s += "if( act_precision == " + str(a) + " &&  wei_precision == " + str(w) + ") begin\n"
                    for i in range(a_ratio):
                        for j in range(w_ratio):  
                            s+="sign_"+str(i)+"_"+str(j)+" <= ((jia[("+str(k)+"+1)*"+str(w)+"-1] ^  yi[("+str(j)+"+1)*"+str(a)+"-1]) == 0   ) ;    \n"
                    s+="end\n"
            s += "end\n"


            
            s += "always@(*) begin\n"
            for w in wei_int:
                for a in act_int:
                    w_ratio = macro_config["MAX_WEI_PRECISION_INT"]//w
                    a_ratio = macro_config["MAX_ACT_PRECISION_INT"]//a
                    if(w_ratio == a_ratio):
                        s += "if( act_precision == " + str(a) + " &&  wei_precision == " + str(w) + ") begin\n"
                        for i in range(a_ratio):
                            s+="zi[("+str(i)+"+1)*"+str(w+a)+"-1:"+str(i)+"*"+str(w+a)+"] = (sign_"+str(i)+"_"+str(j)+") ? \
                                    zi_natural[("+str(i)+"+1)*"+str(w+a)+"-1:"+str(i)+"*"+str(w+a)+"] : -zi_natural[("+str(i)+"+1)*"+str(w+a)+"-1:"+str(i)+"*"+str(w+a)+"];\n"
                            #s+="jia_natural[("+str(i)+"+1)*"+str(w)+"-1:"+str(i)+"*"+str(w)+"] =(jia[("+str(i)+"+1)*"+str(w)+"-1]== 0)?  jia[("+str(i)+"+1)*"+str(w)+"-1:"+str(i)+"*"+str(w)+"] : -jia[("+str(i)+"+1)*"+str(w)+"-1:"+str(i)+"*"+str(w)+"];\n"
                            #s+="yi_natural[("+str(i)+"+1)*"+str(a)+"-1:"+str(i)+"*"+str(a)+"] =(yi[("+str(i)+"+1)*"+str(a)+"-1] == 0)?  yi[("+str(i)+"+1)*"+str(a)+"-1:"+str(i)+"*"+str(a)+"] : -yi[("+str(i)+"+1)*"+str(a)+"-1:"+str(i)+"*"+str(a)+"];\n"
                        s+="end\n"
            s += "end\n"




            s += "endmodule\n"

    ################################################################################################################################
    #This adaptive allows for example, 1 MAX_WEI * MAX_ACT, 2 MAX_WEI//2xMAX_ACT//2, 4 MAX_WEI//4 x MAX_ACT//4... (tiling along TI)
    elif(hardware_config["MULT_TYPE_INT"] in ["BITFUSION_TI", "ADAPTIVE_TI", "ADAPTIVE_INNER"]): 

        if( macro_config["MAX_WEI_PRECISION_INT"] != 0 and macro_config["MAX_ACT_PRECISION_INT"] != 0):
            
            if(macro_config["MIN_WEI_PRECISION_INT"] != 0):
                wei_ratio_int = macro_config["MAX_WEI_PRECISION_INT"]//macro_config["MIN_WEI_PRECISION_INT"]
            #if(macro_config["MIN_WEI_PRECISION_FP"] != 0):
            #    wei_ratio_fp = macro_config["MAX_WEI_PRECISION_FP"]//macro_config["MIN_WEI_PRECISION_FP"]
            if(macro_config["MIN_ACT_PRECISION_INT"] != 0):
                act_ratio_int = macro_config["MAX_ACT_PRECISION_INT"]//macro_config["MIN_ACT_PRECISION_INT"]
            #if(macro_config["MIN_ACT_PRECISION_FP"] != 0):
            #    act_ratio_fp = macro_config["MAX_ACT_PRECISION_FP"]//macro_config["MIN_ACT_PRECISION_FP"]

            wei_int = analyze_int(hardware_config["SUPPORTED_WEI_DTYPES"])
            act_int = analyze_int(hardware_config["SUPPORTED_ACT_DTYPES"])
            
            #if(MULT_TYPE_UNIT = "BOOTH", "WALLACE", "。。。" (TODOS)
            s += "//Unit multiplier - minimum precision as unit \n\
                module MIN_PREC_MULT_INT(\n\
                    input clk,\n\
                    input rst_n,\n\
                    input en,\n\
                    input  [`MIN_WEI_PRECISION_INT-1:0] jia,\n\
                    input  [`MIN_ACT_PRECISION_INT-1:0] yi,\n\
                    output  reg [(`MIN_WEI_PRECISION_INT+`MIN_ACT_PRECISION_INT)-1:0] zi,\n\
                    input valid,\n\
                    output reg ready\n\
                    );\n\
                           //Precision is un-used\n\
                       wire clk_gate;\n\
                       assign clk_gate = en & clk;\n\
                       always@(posedge clk_gate or negedge rst_n) begin\n\
                           if (~rst_n) begin\n\
                               ready <= 0;\n\
                               zi <= 0;\n\
                           end  else begin\n\
                              if(valid) begin\n\
                               zi <= jia * yi; // Most simple implementation, but most costly in PPA]\n\
                               ready <= 1;\n\
                              end else  begin\n\
                               zi <= zi;\n\
                               ready <= 0; \n\
                              end \n\
                           end \n\
                       end\n\
                "
            s += "endmodule\n"
            
            s += "//Basic multiplier  \n\
                module MULT_INT(\n\
                        input clk,\n\
                        input rst_n,\n\
                        input en, //power gating\n\
                        input [5:0] wei_precision, // 4, 8, 16, 32 assumed to be max, not going to go to 64 or more\n\
                        input [5:0] act_precision, // 4, 8, 16, 32 \n\
                        input signed [`MAX_WEI_PRECISION_INT-1:0] jia,\n\
                        input signed [`MAX_ACT_PRECISION_INT-1:0] yi,\n\
                        output reg  [`MAX_PSUM_PRECISION_INT  - 1: 0] zi,\n\
                        input valid,//data is valid and ready for processing\n\
                        output reg ready // data is ready and multiplied , because at most 16/2 cycles\n\
                        );\n"

            s += " reg [`MAX_WEI_PRECISION_INT-1:0] jia_natural;\n"
            s += " reg [`MAX_ACT_PRECISION_INT-1:0] yi_natural;\n"

            #change +/- ---> +
            s += "always@(*) begin\n"
            for w in wei_int:
                for a in act_int:
                    w_ratio = macro_config["MAX_WEI_PRECISION_INT"]//w
                    a_ratio = macro_config["MAX_ACT_PRECISION_INT"]//a
                    if(w_ratio == a_ratio):
                        s += "if( act_precision == " + str(a) + " &&  wei_precision == " + str(w) + ") begin\n"
                        for i in range(a_ratio):
                            s+="jia_natural[("+str(i)+"+1)*"+str(w)+"-1:"+str(i)+"*"+str(w)+"] =(jia[("+str(i)+"+1)*"+str(w)+"-1]== 0)?  jia[("+str(i)+"+1)*"+str(w)+"-1:"+str(i)+"*"+str(w)+"] : -jia[("+str(i)+"+1)*"+str(w)+"-1:"+str(i)+"*"+str(w)+"];\n"
                            s+="yi_natural[("+str(i)+"+1)*"+str(a)+"-1:"+str(i)+"*"+str(a)+"] =(yi[("+str(i)+"+1)*"+str(a)+"-1] == 0)?  yi[("+str(i)+"+1)*"+str(a)+"-1:"+str(i)+"*"+str(a)+"] : -yi[("+str(i)+"+1)*"+str(a)+"-1:"+str(i)+"*"+str(a)+"];\n"
                        s+="end\n"
            s += "end\n"
            

            psum_ready = []
            #s += " assign jia_natural = jia"
            for l in range(act_ratio_int):
                for k in range(wei_ratio_int):
                    no = str(l)+"_"+str(k)
                    s += "    wire signed [(`MIN_WEI_PRECISION_INT + `MIN_ACT_PRECISION_INT)-1:0] psum_"+no+";\n"
                    s += "    wire psum_ready_"+no+";\n"
                    s += "    MIN_PREC_MULT_INT mpmi_"+no+"(.clk(clk),.rst_n(rst_n), .en(en), .jia(jia_natural[`MIN_ACT_PRECISION_INT*"+str((k+1))+"-1:`MIN_WEI_PRECISION_INT*"+str(k)+"]), \
                                    .yi(yi_natural[`MIN_ACT_PRECISION_INT*"+str((l+1))+"-1:`MIN_ACT_PRECISION_INT*"+str(l)+"]), .zi(psum_"+no+"), .valid(valid), .ready(psum_ready_"+no+"));\n"
                        #cross bar , from psum --> zi (TODOS)
                        # 8, 8 -->   2
                        # 4，4 -->   4
                        # 8, 16 -->  2
                        # 16, 16 --> 1
                        # 4, 8   --> 4
                        # assign zi = ...
                        #            for a_prec in act_int:
                        #                 for w_prec in wei_int:
                        #                       if(...)
                        #                          zi = {}
                    psum_ready.append("psum_ready_"+no)

            s += "always@(posedge clk) begin\n"
            s += " ready = " + "&".join(psum_ready) + ";\n"
            s += "end\n"
            
            s += "reg [(`MAX_WEI_PRECISION_INT+`MAX_ACT_PRECISION_INT)-1:0] zi_natural;\n"
            s += "always@(*) begin\n"
            for w in wei_int:
                for a in act_int:
                    w_ratio = macro_config["MAX_WEI_PRECISION_INT"]//w
                    a_ratio = macro_config["MAX_ACT_PRECISION_INT"]//a

                    w_blocks =(w//macro_config["MIN_WEI_PRECISION_INT"])
                    a_blocks = (a//macro_config["MIN_ACT_PRECISION_INT"])

                    

                    if(w_ratio == a_ratio):
                        s += "if( act_precision == " + str(a) + " &&  wei_precision == " + str(w) + ") begin\n"
                        equationes = ""#"zi_natural = "
                        terms = []
                        #if(w_ratio == 1):# and a_ratio == 1):
                        #    for l in range(act_ratio_int):
                        #        for k in range(wei_ratio_int):
                        #            no = str(l)+"_"+str(k)
                        #            terms.append( "(psum_"+no + " << " + str(l * macro_config["MIN_ACT_PRECISION_INT"]   +   k*macro_config["MIN_WEI_PRECISION_INT"]) +")" )
                        #    equationes += "+".join(terms)
                        #elif(w_ratio == 2):
                        for l in range(act_ratio_int):
                            for k in range(wei_ratio_int):
                                no = str(l)+"_"+str(k)
                                if( l // a_blocks  == k // w_blocks ):
                                    terms.append( "(psum_"+no + " << " + str( (l % a_blocks ) * macro_config["MIN_ACT_PRECISION_INT"]   +   (k% w_blocks )*macro_config["MIN_WEI_PRECISION_INT"]) +")")

                        zi_res = []
                        for i in range(a_ratio):
                            zi_res.append("+".join(terms[i*a_blocks*w_blocks: (i+1)*a_blocks*w_blocks]))
                            equationes += "zi_natural[("+str(i)+"+1)*"+str(w+a)+"-1:"+str(i)+"*"+str(w+a)+"] = "+zi_res[i]+" ;\n"
                        #equationes += "{" + ",".join(zi_res) +  "}" #"{" +  "+".join(terms[0:a_blocks*w_blocks]) + ","  + "+".join(terms[a_blocks*w_blocks:]) + "}"
                        #elif(w_ratio == 4 and a_ratio == 4):
                        #    pass
                        #    #equationes = "zi = "
                        #    #todos
                        #    #s += equationes
                        #elif(w_ratio == 8 and a_ratio == 8):
                        #    #equationes = "zi = "
                        #    #todos
                        #    #s += equationes
                        #    pass
                    
                        equationes += ";\n"
                        s += equationes
                        s += "end\n"

            s += "end\n"
            #zi_natural -> zi, (-) to (+)
            for i in range(8):
                for j in range(8):
                    s+= "reg sign_"+str(i)+"_"+str(j)+";\n"

            s += "always@(posedge clk) begin\n"
            for w in wei_int:
                for a in act_int:
                    w_ratio = macro_config["MAX_WEI_PRECISION_INT"]//w
                    a_ratio = macro_config["MAX_ACT_PRECISION_INT"]//a
                    s += "if( act_precision == " + str(a) + " &&  wei_precision == " + str(w) + ") begin\n"
                    for i in range(a_ratio):
                        for j in range(w_ratio):  
                            s+="sign_"+str(i)+"_"+str(j)+" <= ((jia[("+str(k)+"+1)*"+str(w)+"-1] ^  yi[("+str(j)+"+1)*"+str(a)+"-1]) == 0   ) ;    \n"
                    s+="end\n"
            s += "end\n"


            
            s += "always@(*) begin\n"
            for w in wei_int:
                for a in act_int:
                    w_ratio = macro_config["MAX_WEI_PRECISION_INT"]//w
                    a_ratio = macro_config["MAX_ACT_PRECISION_INT"]//a
                    if(w_ratio == a_ratio):
                        s += "if( act_precision == " + str(a) + " &&  wei_precision == " + str(w) + ") begin\n"
                        for i in range(a_ratio):
                            s+="zi[("+str(i)+"+1)*"+str(w+a)+"-1:"+str(i)+"*"+str(w+a)+"] = (sign_"+str(i)+"_"+str(j)+") ? \
                                    zi_natural[("+str(i)+"+1)*"+str(w+a)+"-1:"+str(i)+"*"+str(w+a)+"] : -zi_natural[("+str(i)+"+1)*"+str(w+a)+"-1:"+str(i)+"*"+str(w+a)+"];\n"
                            #s+="jia_natural[("+str(i)+"+1)*"+str(w)+"-1:"+str(i)+"*"+str(w)+"] =(jia[("+str(i)+"+1)*"+str(w)+"-1]== 0)?  jia[("+str(i)+"+1)*"+str(w)+"-1:"+str(i)+"*"+str(w)+"] : -jia[("+str(i)+"+1)*"+str(w)+"-1:"+str(i)+"*"+str(w)+"];\n"
                            #s+="yi_natural[("+str(i)+"+1)*"+str(a)+"-1:"+str(i)+"*"+str(a)+"] =(yi[("+str(i)+"+1)*"+str(a)+"-1] == 0)?  yi[("+str(i)+"+1)*"+str(a)+"-1:"+str(i)+"*"+str(a)+"] : -yi[("+str(i)+"+1)*"+str(a)+"-1:"+str(i)+"*"+str(a)+"];\n"
                        s+="end\n"
            s += "end\n"



            
                           
            '''
            for l in range(act_ratio_int):
                for k in range(wei_ratio_int):
                    
            s += "if( act_precision == " + str(l) + "*`MIN_ACT_PRECISION_INT   &&  wei_precision == " + str(k) + "*`MIN_WEI_PRECISION_INT) begin\n"
                if(l == 1 and kk == 1 
            s += "    zi = {  " + "  } ;  \n"     
            
            s += "end\n"
            '''
            #s += "end\n"
            s += "\
                    endmodule\n"




    elif(hardware_config["MULT_TYPE_INT"] == "BitPragmatic"):
        pass

    elif(hardware_config["MULT_TYPE_INT"] == "Wallace"):
        pass
    elif(hardware_config["MULT_TYPE_INT"] == "BoothRadix2"):
        pass
    elif(hardware_config["MULT_TYPE_INT"] == "BoothRadix3"):   
        pass
    else:
        print(hardware_config["MULT_TYPE_INT"], "UNDEFINED MULTIPLIER TYPE")






    if(hardware_config["MULT_TYPE_FP"] == "BASIC"):
        if( macro_config["MAX_WEI_PRECISION_FP"] != 0 and macro_config["MAX_ACT_PRECISION_FP"] != 0):

            wei_float = analyze_floating(hardware_config["SUPPORTED_WEI_DTYPES"])
            act_float = analyze_floating(hardware_config["SUPPORTED_ACT_DTYPES"])
            MAX_A_P, MAX_A_E, MAX_A_M = max_floating_props(act_float)
            MAX_W_P, MAX_W_E, MAX_W_M = max_floating_props(wei_float)

            s += "//Basic multiplier  \n\
module MULT_FP(\n\
                    input clk,\n\
                    input rst_n,\n\
                    input en, //power gating\n\
                    input [5:0] wei_precision, // 4, 8, 16, 32 assumed to be max, not going to go to 64 or more\n\
                    input [5:0] act_precision, // 4, 8, 16, 32,  \n\
                    input [5:0] wei_mantissa, \n\
                    input [5:0] act_mantissa, \n\
                    input [5:0] wei_exponent, \n\
                    input [5:0] act_exponent, \n\
                    input [5:0] wei_regime, \n\
                    input [5:0] act_regime, \n\
                    input  [`MAX_WEI_PRECISION_FP-1:0] jia,\n\
                    input  [`MAX_ACT_PRECISION_FP-1:0] yi,\n\
                    output reg [(`MAX_ACT_PRECISION_FP) - 1: 0] zi,\n\
                        \n\
                    input valid,//data is valid and ready for processing\n\
                    output reg ready // data is ready and multiplied , because at most 16/2 cycles\n\
                    );\n\
                        \n"


            if(MAX_A_P > 0):
                s += "reg ["+str(MAX_A_P)+" - 1 : 0] act_p;\n"
            s += "reg ["+str(MAX_A_E)+" - 1 : 0] act_e;\n"
            s += "reg ["+str(MAX_A_M)+" - 1 : 0] act_m;\n"
            if(MAX_W_P > 0):
                s += "reg ["+str(MAX_W_P)+" - 1 : 0] wei_p;\n"
            s += "reg ["+str(MAX_W_E)+" - 1 : 0] wei_e;\n"
            s += "reg ["+str(MAX_W_M)+" - 1 : 0] wei_m;\n"
            s += "reg act_s;\n"
            s += "reg wei_s;\n"

            if(MAX_W_P > 0 and MAX_A_P > 0):
                s += "reg [] psum_p;\n" #(TODOS)

                
            s += "wire ["+str(MAX_A_E)+":0] psum_e;\n" #addition
            s += "reg ["+str(MAX_A_M+MAX_W_M+2)+":0] psum_m;\n" #multiplie mantissa and do some shifting
            s += "wire psum_s;\n" #sign
            s += "reg ["+str(MAX_A_E)+"-1:0] zi_e;\n"
            s += "reg ["+str(MAX_A_M+MAX_W_M+2)+"-1:0] zi_m;\n"
            s += "wire zi_s;\n"

            if(MAX_A_P > 0 and MAX_W_P > 0):
                s += "zi_p = (todos"
            s += "assign psum_s = wei_s ^ act_s;\n"
            s += "assign psum_e = wei_e + act_e  + 2 - ((1<<(wei_exponent-1))-1);\n" #This is the exact exponent
            #s += "assign zi_e = psum_e + ;\n"

            s += "always@(*)begin\n"
            for a_s, a_p, a_e, a_m, a_prec in act_float:
                for w_s, w_p, w_e, w_m, w_prec in wei_float:
                    s += "if(wei_mantissa == 6'd"+str(w_m) + " && \
                                  act_mantissa == 6'd"+str(a_m)+") begin \n"
                    s += "      psum_m = {1'b1, wei_m["+str(w_m)+"-1:0]}*{1'b1, act_m["+str(a_m)+"-1:0]};\n"

                    for idx, i in enumerate(range(w_m+a_m+2-1, a_m, -1)):
                        if(idx == 0):
                            s += "    if(psum_m["+str(i)+"] == 1'b1) begin\n"
                        else:
                            s += "    end else if (psum_m["+str(i)+"] == 1'b1) begin\n"
                        s += "        zi_m = psum_m << "+str(idx+1)+";\n"
                        s += "        zi_e = psum_e - "+str(idx+1)+";\n"
                        #s += "      zi_m = ???;\n"

                    s += "end\n"
                    s += "end\n"    
            s += "end\n"


            #s += "end\n"

            s += "assign zi_s = psum_s;\n"

            s += "always@(act_mantissa or act_precision or act_exponent or act_regime) begin\n"
            for sign, P, E, M, PREC in act_float:
                s += "    if(act_mantissa == 6'd"+str(M)+" && act_precision == 6'd" + str(PREC) + " && act_exponent == 6'd" + str(E) + " && act_regime == 6'd" + str(P) + ") begin \n"
                s += "          act_m = yi["+str(M)+"-1:0]  ;\n"
                s += "          act_e = yi["+str(E+M)+"-1:"+str(M)+"]  ;\n"
                if(P != 0):
                    s += "          act_p = yi["+str(P+E+M)+"-1:"+str(E+M)+"]  ;\n"
                s += "          act_s = yi["+str(PREC)+"-1]  ;\n"
                s += "end\n"
            s += "end\n"
            
            s += "always@( wei_mantissa or wei_precision or wei_exponent or wei_regime) begin\n"
            
            for sign, P, E, M, PREC in wei_float:
                s += "    if(wei_mantissa == 6'd"+str(M)+" && wei_precision == 6'd" + str(PREC) + " && wei_exponent == 6'd" + str(E) + " && wei_regime == 6'd" + str(P) + ") begin \n"
                s += "          wei_m = jia["+str(M)+"-1:0]  ;\n"
                s += "          wei_e = jia["+str(E+M)+"-1:"+str(M)+"]  ;\n"
                if(P != 0):
                    s += "          wei_p = jia["+str(P+E+M)+"-1:"+str(E+M)+"]  ;\n"
                s += "          wei_s = jia["+str(PREC)+"-1]  ;\n"
                s += "end\n"
            
            s += "end\n"

            s += "wire clk_gate;\n\
                   assign clk_gate = en & clk;\n\
                   always@(posedge clk_gate or negedge rst_n) begin\n\
                       if (~rst_n) begin\n\
                           ready <= 0;\n\
                           zi <= 0;\n\
                       end  else begin\n\
                          if(valid) begin\n"            
            for a_s, a_p, a_e, a_m, a_prec in act_float:
                for w_s, w_p, w_e, w_m, w_prec in wei_float:
                    s += "if(wei_mantissa == 6'd"+str(w_m)+" && wei_precision == 6'd" + str(w_prec) + " && wei_exponent == 6'd" + str(w_e) + " && wei_regime == 6'd" + str(w_p) + " && \
                                  act_mantissa == 6'd"+str(a_m)+" && act_precision == 6'd" + str(a_prec) + " && act_exponent == 6'd" + str(a_e) + " && act_regime == 6'd" + str(a_p) + ") begin \n"
                    if(macro_config["MAX_ACT_PRECISION_FP"] - (a_e+a_m+1) <= 0):
                        s += "    zi <= {zi_s,  zi_e["+str(a_e)+"-1:0], zi_m["+str(a_m+w_m+2)+"-1:"+str(w_m+2)+"]      };\n"
                    else:
                        s += "    zi <= {"+str(macro_config["MAX_ACT_PRECISION_FP"] - (a_e+a_m+1) )+"'b0, zi_s,  zi_e["+str(a_e)+"-1:0], zi_m["+str(a_m+w_m+2)+"-1:"+str(w_m+2)+"]      };\n"
                    s += "end\n"
            s += "             ready <= 1;\n\
                          end else  begin\n\
                           zi <= zi;\n\
                           ready <= 0; \n\
                          end \n\
                       end \n\
                   end\n\
                endmodule\n"            
            

    elif(hardware_config["MULT_TYPE_FP"] == "ADAPTIVE"):
        pass


    print(s)
    f.write(s)
    f.close()
        
    print("\n// GEN_MULTIPLIER VERILOG - DONE\n")
