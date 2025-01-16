module tb;


// Mode Control
reg BIST;
			
reg AWT;
// Normal Mode Input
reg PD;
reg CLK;
reg CEB;
reg WEB;
reg [10:0] A;
reg  [31:0] D;
reg [31:0] BWEB;

// BIST Mode Input
reg  CEBM;
reg WEBM;
reg [10:0] AM;
reg [31:0] DM;
reg [31:0] BWEBM;

// Data Output
wire [31:0] Q;

// Test Mode
reg [1:0] RTSEL;
reg [1:0] WTSEL;


TS1N40LPB2048X32M4FWBA sram (
	PD, CLK, CEB, WEB,
			CEBM, WEBM,
                        AWT,
                        A, D, 
                        BWEB,
                        AM, DM, 
                        BWEBM,
			BIST,
                        RTSEL, WTSEL, 
                        Q);
initial begin
CLK = 0;
forever begin
 #2; CLK <= ~CLK;
end
end

initial begin
$dumpfile("sram.vcd");
$dumpvars(0, tb);
end;


task preloadData;
endtask

initial begin
CEB = 0;
CEBM = 1;
WEB = 1;//READ
WEBM = 1;
AWT=0;
BIST = 0;

BWEB = 32'hffffffff;

PD = 0;
A  = 0;
D = 1;
RTSEL = 2'b01;
WTSEL = 2'b01;
#10;
A = 1;
#10;
A = 2;
#10;
$finish;
end


endmodule