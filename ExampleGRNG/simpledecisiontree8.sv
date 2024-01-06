module  gaussianSimplified8(input pbits7,input pbits6, input[0:1] pbits5, 
		input[0:3] pbits4, input[0:7] pbits3, input[0:15] pbits2,
		input[0:15] pbits1, input[0:7] pbits0,
    		output[7:0] result
);

wire bit7;
wire bit6;
wire bit5;
wire bit4;
wire bit3;
wire bit2;
wire bit1;
wire bit0;

wire[1:0] pbits5bw;
wire[3:0] pbits4bw;
wire[7:0] pbits3bw;
wire[15:0] pbits2bw;
wire[15:0] pbits1bw;
wire[7:0] pbits0bw;


reverser #(.N(2))  rev5(pbits5, pbits5bw);
reverser #(.N(4))  rev4(pbits4, pbits4bw);
reverser #(.N(8))  rev3(pbits3, pbits3bw);
reverser #(.N(16)) rev2(pbits2, pbits2bw);
reverser #(.N(16)) rev1(pbits1, pbits1bw);
reverser #(.N(8)) rev0(pbits0, pbits0bw);

assign bit7 = pbits7;
mux #(.N(1)) muxbit6({~pbits6,	pbits6},  bit7, bit6);
mux #(.N(2)) muxbit5({pbits5bw, pbits5}, {bit7, bit6}, bit5);
mux #(.N(3)) muxbit4({pbits4bw, pbits4}, {bit7, bit6, bit5}, bit4);
mux #(.N(4)) muxbit3({pbits3bw, pbits3}, {bit7, bit6, bit5, bit4}, bit3);
mux #(.N(5)) muxbit2({pbits2bw, pbits2}, {bit7, bit6, bit5, bit4, bit3}, bit2);
mux #(.N(5)) muxbit1({pbits1bw, pbits1}, {bit7, bit6, bit5, bit4, bit3}, bit1);
mux #(.N(4)) muxbit0({pbits0bw, pbits0}, {bit7, bit6, bit5, bit4}, bit0);

assign result = {~bit7, bit6, bit5, bit4, bit3, bit2, bit1, bit0};

    


    
endmodule


module  mux #(parameter N = 1) (input[(2**N-1):0] entries,input[(N-1):0] sel, output result);
    if (N == 1) begin
        assign result = (sel == 1) ? entries[1] : entries[0];
    end
    else begin
        mux #(.N(N-1))uppermux(entries[2**N-1:2**(N-1)],sel[N-2:0],result1);
        mux #(.N(N-1))lowermux(entries[2**(N-1)-1:0],sel[N-2:0],result0);
        assign result = (sel[N-1] == 1) ? result1 : result0; 
    end
endmodule 

module reverser #(parameter N = 8) (input[(N-1):0] forward, output[(N-1):0] reversed);
    for (genvar i=0; i<N; i=i+1) begin
        assign reversed[i] = ~forward[N-1-i];
    end
endmodule


