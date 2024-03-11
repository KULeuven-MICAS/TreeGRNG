import cocotb
import numpy as np
import pytest
import math
import random
import statistics
from scipy.stats import kstest

from cocotb.triggers import Timer, RisingEdge
from cocotb_test.simulator import run
from cocotb.types import Array, Range
from matplotlib import pyplot as plt
from cocotb.binary import BinaryValue
from cocotb.clock import Clock

resultlist = []

@cocotb.test()
async def comp_test(dut):
    N_TESTS = 1000000
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.LD_seed.value = 1
    await RisingEdge(dut.clk)
    dut.LD_seed.value = 0
    for i in range(N_TESTS):
        await RisingEdge(dut.clk)
        resultlist.append(myint(dut.result.value))
    stats = statisticsGaussian4(N_TESTS,resultlist)
    #with open("/users/micasgst/jcrols/gitProjects/GaussianRandomNumberGenerator/statistics/decisiontree_based/non_pipelined/acc14_len4/accuracy.txt", "w") as fOut:
    #   print(f'RMS: {stats[0]} \n STD_DEV: {stats[1]} \n MEAN: {stats[2]} \n KLD: {stats[3]} \n KST: {stats[4]}', file=fOut)
    #cocotb.log.info(f'RMS: {stats[0]} \n STD_DEV: {stats[1]} \n MEAN: {stats[2]} \n KLD: {stats[3]}')
    #assert stats[0] < N_TESTS/10000
    #assert stats[1] > 31.5 and stats[1] < 32.5
    #assert stats[2] > 127 and stats[2] < 128
    plt.hist(resultlist, [x/32 for x in range(-128, 128)])
    #reference = getReferenceGaussian(N_TESTS)
    #plt.hist([reference,resultlist], [x for x in range(256)], label=['reference','design'])
    #plt.show()
    #plt.savefig("/users/micasgst/jcrols/gitProjects/GaussianRandomNumberGenerator/latestresult.png")
    plt.savefig("/users/micasgst/jcrols/gitProjects/GaussianRandomNumberGenerator/resultFixedPoint.png")

def myint(getal):
    flipped = int(getal)
    if flipped >= 128:
        flipped = flipped-256
    return flipped/32

def getReferenceGaussian(N_TESTS):
    reference = []
    for i in range(256):
        for j in range(int(math.comb(4095, 1920+i)/(2**4095)*N_TESTS)):
            reference.append(i)
    return reference

def statisticsGaussian(N_TESTS, resultlist):
    averageSQR = 0
    kullleib = 0
    for i in range(256):
        freq = resultlist.count(i)
        refi = int(math.comb(4095, 1920+i)/(2**4095)*N_TESTS)
        delta  = (freq-refi)
        if freq!= 0 and refi != 0:
            relta = math.comb(4095, 1920+i)/(2**4095)*math.log2(refi/freq)
            kullleib += relta
        averageSQR += delta**2
    stddev = math.sqrt(statistics.variance(resultlist))
    mean = statistics.mean(resultlist)
    RelRMS = math.sqrt(averageSQR/256)
    KST = kstest([(x-127.5)/32 for x in resultlist], 'norm')
    return [RelRMS, stddev, mean, kullleib, KST] 

def getReferenceGaussian4(N_TESTS):
    reference = []
    for i in range(16):
        for j in range(int(math.comb(15, i)/(2**15)*N_TESTS)):
            reference.append(i)
    return reference

def statisticsGaussian4(N_TESTS, resultlist):
    averageSQR = 0
    kullleib = 0
    for i in range(16):
        freq = resultlist.count(i)
        refi = int(math.comb(15, i)/(2**15)*N_TESTS)
        delta  = (freq-refi)
        if freq!= 0 and refi != 0:
            relta = math.comb(15, i)/(2**15)*math.log2(refi/freq)
            kullleib += relta
        averageSQR += delta**2
    stddev = math.sqrt(statistics.variance(resultlist))
    mean = statistics.mean(resultlist)
    RelRMS = math.sqrt(averageSQR/16)
    KST = kstest([(x-7.5)/2 for x in resultlist], 'norm')
    return [RelRMS, stddev, mean, kullleib, KST] 

@pytest.mark.parametrize(
"parameters", [
    {}
])

def test_top(parameters):
    # Get file sources
    include_folders = ['']
    rtl_sources = ['hdl/decisiontree_based/decisiontree/simpledecisiontree8.sv', \
                 'hdl/decisiontree_based/pbit/lfsr.sv',  \
                 'hdl/decisiontree_based/pbit/comparator.sv', \
                 'hdl/decisiontree_based/topgrng/topgrng12_8.sv']
    toplevel    =  'compGRNG'
    run(
        includes=include_folders,
        verilog_sources=rtl_sources,
        toplevel=toplevel,    # top level HDL
        module="test_top", # name of the file that contains @cocotb.test() -- this file
        #simulator="xcelium",
        #sim_args=[''],      
        simulator="questa",
        sim_args=['-64'],       
        waves=True,
        parameters = parameters,
        #parameters=parameters,
        #extra_env=parameters,
        
        sim_build="unittests/sim_build/{}/".format(
            toplevel) + ",".join((f"{key}={value}" for key, value in parameters.items())),
    )        
    

