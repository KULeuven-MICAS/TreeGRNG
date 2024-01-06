import math
import random
from scipy.stats import norm


#CHANGE PARAMETERS HERE
##############################################################
#WEIGHTS list contains frequency of getting result = x relative to total sum of list, length is ALWAYS 2**RESULTLENGTH
#RESULTLENGTH is amount of bits in final result. default = 8
#INTERNAL_ACC determines the length of the tresholds that are used internally. default = 12
#SIMPLIFY determines if lower layers should be simplified to avoid exponantial of hardware.
#SYMMETRIC determines if result is symmetric. if SIMPLIFY is False, SYMMETRIC will be False.
#PRINT_ADDR determines file to wich verilog will be written, will create file if not exist yet, uses absolute path
#LFSR_AMOUNT determines how many different lengths off LFSR's will be used to reduce repeating patterns. max 8. default = 4
#TWOSCOMPLEMENT determines whether the first negative values are present. if True, WEIGHTS will be projected onto
#               (-2**(RESULTLENGTH-1), 2**(RESULTLENGTH-1)). if False, WEIGHTS will be projected onto (0, 2**RESULTLENGTH).
WEIGHTS = [norm.pdf(x/32 - 4) for x in range(0, 256)]
RESULTLENGTH = 8
INTERNAL_ACC = 8
SIMPLIFY = True
SYMMETRIC = True
PRINT_ADDR = ''
LFSR_AMOUNT = 4
TWOSCOMPLEMENT = True
##############################################################



lfsrthings = ['-1','','+1','-2', '+2', '-3', '+3', '-4']
lfsrthingsplus1 = ['','+1','+2','-1', '+3', '-2', '+4', '-3']
lfsrthingsint = [0, 1, 2, -1, 3, -2, 4, -3]

def getKansLowerHelft(start, einde, weightsvar):
    lowersum = sum([weightsvar[x] for x in range(start, (start + einde) // 2)])
    uppersum = sum([weightsvar[x] for x in range(start, einde)])
    return lowersum/uppersum

def getRandomStartLFSR(accuracy):
    result = f'{accuracy}\'b'
    for i in range(accuracy):
        result += str(random.randint(0,1))
    return result



def getTresholds(weightsvar, bitlength):
    resultlist = [[] for x in range(bitlength)]
    for k in range(bitlength):
        for i in range(2**k):
            resultlist[k].append(getKansLowerHelft(2**(bitlength-k) * i,2**(bitlength-k) + 2**(bitlength-k) * i, weightsvar ))
    return resultlist

def convertInt(sample):
    if sample <= 0.0001:
        return 0
    return sample


#print(f'', file=fOut)
#values has exactly length 2**bitlength
def printVerilog(values, print_addr, bitlength=8, accuracy=12,  lfsr_amount=4 , simplify=True, symmetric=True, twoscomplement=True):
    with open(print_addr, 'w') as fOut:
        print(f'module RandDist #(parameter BITNUMS = {accuracy}) (input clk, input LD_seed, ', file=fOut)
        print(f'    output[{bitlength-1}:0] result', file=fOut)
        print(f');', file=fOut)
        print(f'\n\n', file=fOut)
        print(f'wire pBit0;', file=fOut)

        if symmetric:
            print(f'wire pBit1;', file=fOut)
            for i in range(2,bitlength):
                if i<= 5 or not simplify:
                    print(f'wire[{(2**(i-1)-1)}:0] pBit{i};', file=fOut)
                elif i<=6:
                    print(f'wire[15:0] pBit{i};', file=fOut)
                else:
                    print(f'wire[7:0] pBit{i};', file=fOut)
        else:
            print(f'wire pBit1[1:0];', file=fOut)
            for i in range(2,bitlength):
                if i<= 5 or not simplify:
                    print(f'wire[{(2**(i)-1)}:0] pBit{i};', file=fOut)
                elif i<=6:
                    print(f'wire[31:0] pBit{i};', file=fOut)
                else:
                    print(f'wire[15:0] pBit{i};', file=fOut)

        print(f'\n\n', file=fOut)

        print(f'wire[BITNUMS-1:0] unfilteredLFSR0;', file=fOut)
        print(f'wire LFSR0Done;', file=fOut)
        print(f'LFSR #(.NUM_BITS(BITNUMS)) LFSR0(clk, 1\'b1, LD_seed, {getRandomStartLFSR(accuracy)}, unfilteredLFSR0, LFSR0Done); ', file=fOut)
        print(f'propabmaker #(.L2N(BITNUMS), .T({values[0][0]:.10f}*(2**(BITNUMS)-1))) prop{0}_{0}(unfilteredLFSR0, pBit0);', file=fOut)
        print(f'\n', file=fOut)

        if symmetric:
            print(f'wire[BITNUMS:0] unfilteredLFSR1;', file=fOut)
            print(f'wire LFSR1Done;', file=fOut)
            print(f'LFSR #(.NUM_BITS(BITNUMS+1)) LFSR1(clk, 1\'b1, LD_seed, {getRandomStartLFSR(accuracy+1)}, unfilteredLFSR1, LFSR1Done); ', file=fOut)
            print(f'propabmaker #(.L2N(BITNUMS+1), .T({values[1][0]:.10f}*(2**(BITNUMS+1)-1))) prop{1}_{0}(unfilteredLFSR1, pBit1);', file=fOut)
            print(f'\n', file=fOut)
            for i in range(2, bitlength):
                print(f'wire[BITNUMS{lfsrthings[i%lfsr_amount]}:0] unfilteredLFSR{i};', file=fOut)
                print(f'wire LFSR{i}Done;', file=fOut)
                print(f'LFSR #(.NUM_BITS(BITNUMS{lfsrthingsplus1[i%lfsr_amount]})) LFSR{i}(clk, 1\'b1, LD_seed, {getRandomStartLFSR(accuracy+lfsrthingsint[i%lfsr_amount])}, unfilteredLFSR{i}, LFSR{i}Done); ', file=fOut)
                if i <=5 or not simplify:
                    for k in range(2**(i-1)):
                        print(f'propabmaker #(.L2N(BITNUMS{lfsrthingsplus1[i%lfsr_amount]}), .T({values[i][k]:.10f}*(2**(BITNUMS{lfsrthingsplus1[i%lfsr_amount]})-1))) prop{i}_{k}(unfilteredLFSR{i}, pBit{i}[{k}]);', file=fOut)
                elif i <=6:
                    for k in range(16):
                        print(f'propabmaker #(.L2N(BITNUMS{lfsrthingsplus1[i%lfsr_amount]}), .T({values[i][2**(i-6) + (2**(i-5)) * k]:.10f}*(2**(BITNUMS{lfsrthingsplus1[i%lfsr_amount]})-1))) prop{i}_{k}(unfilteredLFSR{i}, pBit{i}[{k}]);', file=fOut)
                else:
                    for k in range(8):
                        print(f'propabmaker #(.L2N(BITNUMS{lfsrthingsplus1[i%lfsr_amount]}), .T({values[i][2**(i-5) + (2**(i-4)) * k]:.10f}*(2**(BITNUMS{lfsrthingsplus1[i%lfsr_amount]})-1))) prop{i}_{k}(unfilteredLFSR{i}, pBit{i}[{k}]);', file=fOut)

                print(f'\n', file=fOut)
        else:
            print(f'wire[BITNUMS:0] unfilteredLFSR1;', file=fOut)
            print(f'wire LFSR1Done;', file=fOut)
            print(f'LFSR #(.NUM_BITS(BITNUMS+1)) LFSR1(clk, 1\'b1, LD_seed, {getRandomStartLFSR(accuracy+1)}, unfilteredLFSR1, LFSR1Done); ', file=fOut)
            print(f'propabmaker #(.L2N(BITNUMS+1), .T({values[1][0]:.10f}*(2**(BITNUMS+1)-1))) prop{1}_{0}(unfilteredLFSR1, pBit1[0]);', file=fOut)
            print(f'propabmaker #(.L2N(BITNUMS+1), .T({values[1][1]:.10f}*(2**(BITNUMS+1)-1))) prop{1}_{1}(unfilteredLFSR1, pBit1[1]);', file=fOut)

            print(f'\n', file=fOut)
            for i in range(2, bitlength):
                print(f'wire[BITNUMS{lfsrthings[i%lfsr_amount]}:0] unfilteredLFSR{i};', file=fOut)
                print(f'wire LFSR{i}Done;', file=fOut)
                print(f'LFSR #(.NUM_BITS(BITNUMS{lfsrthingsplus1[i%lfsr_amount]})) LFSR{i}(clk, 1\'b1, LD_seed, {getRandomStartLFSR(accuracy+lfsrthingsint[i%lfsr_amount])}, unfilteredLFSR{i}, LFSR{i}Done); ', file=fOut)
                if i <=5 or not simplify:
                    for k in range(2**(i)):
                        print(f'propabmaker #(.L2N(BITNUMS{lfsrthingsplus1[i%lfsr_amount]}), .T({values[i][k]:.10f}*(2**(BITNUMS{lfsrthingsplus1[i%lfsr_amount]})-1))) prop{i}_{k}(unfilteredLFSR{i}, pBit{i}[{k}]);', file=fOut)
                elif i <=6:
                    for k in range(32):
                        print(f'propabmaker #(.L2N(BITNUMS{lfsrthingsplus1[i%lfsr_amount]}), .T({values[i][2**(i-6) + (2**(i-5)) * k]:.10f}*(2**(BITNUMS{lfsrthingsplus1[i%lfsr_amount]})-1))) prop{i}_{k}(unfilteredLFSR{i}, pBit{i}[{k}]);', file=fOut)
                else:
                    for k in range(16):
                        print(f'propabmaker #(.L2N(BITNUMS{lfsrthingsplus1[i%lfsr_amount]}), .T({values[i][2**(i-5) + (2**(i-4)) * k]:.10f}*(2**(BITNUMS{lfsrthingsplus1[i%lfsr_amount]})-1))) prop{i}_{k}(unfilteredLFSR{i}, pBit{i}[{k}]);', file=fOut)

                print(f'\n', file=fOut)

        print(f'decisiontree dt(pBit0',end='', file=fOut)
        for i in range(1, bitlength):
            print(f', pBit{i}',end='', file=fOut)
        print(f', result);\n', file=fOut)
        print(f'endmodule', file=fOut)



        print(f'\n\n\n\n', file= fOut)

        print(f'module decisiontree(', file=fOut)
        print(f'input pbits0,', file=fOut)
        if symmetric:
            print(f'input pbits1,', file=fOut)
            for i in range(2, bitlength):
                if i <= 5 or not simplify:
                    print(f'input[{2**(i-1)-1}:0] pbits{i},', file=fOut)
                elif i <=6:
                    print(f'input[15:0] pbits{i},', file=fOut)
                else:
                    print(f'input[7:0] pbits{i},', file=fOut)
        else:
            print(f'input pbits1[1:0],', file=fOut)
            for i in range(2, bitlength):
                if i <= 5 or not simplify:
                    print(f'input[{2**(i)-1}:0] pbits{i},', file=fOut)
                elif i <=6:
                    print(f'input[31:0] pbits{i},', file=fOut)
                else:
                    print(f'input[15:0] pbits{i},', file=fOut)

        print(f' output[{bitlength-1}:0] result);', file=fOut)
        print(f'\n', file=fOut)

        for i in range(bitlength):
            print(f'wire bit{i};', file=fOut)

        print(f'\n', file=fOut)

        if symmetric:
            for i in range(2, bitlength):
                if i<= 5 or not simplify:
                    print(f'wire[{2**(i-1)-1}:0] pbits{i}bw;', file=fOut)
                elif i <= 6:
                    print(f'wire[15:0] pbits{i}bw;', file=fOut)
                else:
                    print(f'wire[7:0] pbits{i}bw;', file=fOut)

        print(f'\n', file=fOut)

        if symmetric:
            for i in range(2, bitlength):
                if i<= 5 or not simplify:
                    print(f'reverser #(.N({2**(i-1)})) rev{i}(pbits{i}, pbits{i}bw);', file=fOut)
                elif i <= 6:
                    print(f'reverser #(.N(16)) rev{i}(pbits{i}, pbits{i}bw);', file=fOut)
                else:
                    print(f'reverser #(.N(8)) rev{i}(pbits{i}, pbits{i}bw);', file=fOut)

        print(f'\n', file=fOut)

        print(f'assign bit0 = pbits0;', file=fOut)
        if symmetric:
            print(f'mux #(.N(1)) muxbit1({{~pbits1,	pbits1}},  bit0, bit1);', file=fOut)
            for i in range(2, bitlength):
                if i<= 5 or not simplify:
                    print(f'mux #(.N({i})) muxbit{i}({{pbits{i}bw, pbits{i}}}, {{bit0 ', file=fOut, end='')
                    for j in range(1,i):
                        print(f', bit{j} ', file=fOut, end='')
                    print(f'}}, bit{i});', file=fOut)
                elif i<=6:
                    print(f'mux #(.N(5)) muxbit{i}({{pbits{i}bw, pbits{i}}}, {{bit0, bit1, bit2, bit3, bit4}}, bit{i});', file=fOut)
                else:
                    print(f'mux #(.N(4)) muxbit{i}({{pbits{i}bw, pbits{i}}}, {{bit0, bit1, bit2, bit3}}, bit{i});', file=fOut)
        else:
            print(f'mux #(.N(1)) muxbit1({{pbits1}},  bit0, bit1);', file=fOut)
            for i in range(2, bitlength):
                if i<= 5 or not simplify:
                    print(f'mux #(.N({i})) muxbit{i}({{pbits{i}}}, {{bit0 ', file=fOut, end='')
                    for j in range(1,i):
                        print(f', bit{j} ', file=fOut, end='')
                    print(f'}}, bit{i});', file=fOut)
                elif i<=6:
                    print(f'mux #(.N(5)) muxbit{i}({{pbits{i}}}, {{bit0, bit1, bit2, bit3, bit4}}, bit{i});', file=fOut)
                else:
                    print(f'mux #(.N(4)) muxbit{i}({{pbits{i}}}, {{bit0, bit1, bit2, bit3}}, bit{i});', file=fOut)

        print(f'\n', file=fOut)

        if twoscomplement:
            print(f'assign result = {{ ~bit0', file=fOut, end='')
        else:
            print(f'assign result = {{ bit0', file=fOut, end='')
        for i in range(1, bitlength):
            print(f', bit{i}', file=fOut, end='')
        print(f'}};', file=fOut)


        print(f'\n', file=fOut)

        print(f'endmodule', file=fOut)

        print(f'\n\n\n', file=fOut)

        print(f'module  mux #(parameter N = 1) (input[(2**N-1):0] entries,input[(N-1):0] sel, output result);', file=fOut)
        print(f'    if (N == 1) begin', file=fOut)
        print(f'        assign result = (sel == 1) ? entries[1] : entries[0];', file=fOut)
        print(f'    end', file=fOut)
        print(f'    else begin', file=fOut)
        print(f'        mux #(.N(N-1))uppermux(entries[2**N-1:2**(N-1)],sel[N-2:0],result1);', file=fOut)
        print(f'        mux #(.N(N-1))lowermux(entries[2**(N-1)-1:0],sel[N-2:0],result0);', file=fOut)
        print(f'        assign result = (sel[N-1] == 1) ? result1 : result0; ', file=fOut)
        print(f'    end', file=fOut)
        print(f'endmodule ', file=fOut)


        print(f'\n\n', file=fOut)
        print(f'module reverser #(parameter N = 8) (input[(N-1):0] forward, output[(N-1):0] reversed);', file=fOut)
        print(f'    for (genvar i=0; i<N; i=i+1) begin', file=fOut)
        print(f'        assign reversed[i] = ~forward[N-1-i];', file=fOut)
        print(f'    end', file=fOut)
        print(f'endmodule', file=fOut)


printVerilog(getTresholds(WEIGHTS, RESULTLENGTH),  PRINT_ADDR, RESULTLENGTH, INTERNAL_ACC, LFSR_AMOUNT, SIMPLIFY, SIMPLIFY and SYMMETRIC, TWOSCOMPLEMENT)