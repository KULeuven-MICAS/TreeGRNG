include load_etc.tcl


set DESIGN compGRNG
set POW_EFF high
set SYN_EFF high
set MAP_EFF high

set _OUTPUTS_PATH outputs
set _REPORTS_PATH reports
set _LOG_PATH logs
set _RESULTS_PATH results


#shell rm -rf logs/ outputs/ rc.* reports/ results/

set DK_PATH /users/micasgst/jcrols/gitProjects/GaussianRandomNumberGenerator

set lib_svt_worst_1_0V "${DK_PATH}/synth/45nm_1.10V_25C_0mV.lib"

#set lef_svt_worst_1_0V "${DK_PATH}/LEF/cmos065_7m4x0y2z_Worst.lef \  
#                        ${DK_PATH}/LEF/CORE65LPSVT.lef" 

#set captables "${DK_PATH}/captable/cmos065_7m4x0y2z_Worst.captable"

set_attribute library ${lib_svt_worst_1_0V}
#set_attribute lef_library ${lef_svt_worst_1_0V}
#set_attribute cap_table_file ${captables}

set scrit_path "/users/micasgst/jcrols/gitProjects/GaussianRandomNumberGenerator"
set hdl_path "/users/micasgst/jcrols/gitProjects/GaussianRandomNumberGenerator/hdl/decisiontree_based/"
set_attribute script_search_path ${scrit_path} /
set_attribute hdl_search_path ${hdl_path} /

set_attribute find_takes_multiple_names true

#HDL ERRORS
set_attribute hdl_unconnected_input_port_value 0
set_attribute hdl_undriven_output_port_value   0
set_attribute hdl_undriven_signal_value        0

set_attribute hdl_error_on_blackbox true 
set_attribute hdl_error_on_latch true 
set_attribute hdl_error_on_negedge true 

#set_attribute wireload_mode top 
set_attribute information_level 7 
set_attribute lp_power_unit uW 


#set_attr interconnect_mode ple 
set_attribute hdl_track_filename_row_col true 
#set_attribute hdl_max_loop_limit 4096


read_hdl -sv topgrng/topgrng8_8.sv pbit/lfsr.sv pbit/comparator.sv decisiontree/simpledecisiontree8.sv decisiontree/simpledecisiontree4.sv
elaborate $DESIGN
check_design -unresolved
#read_sdc constraints.sdc

report timing -lint

set_attribute lp_power_analysis_effort $POW_EFF

#set_attr dp_perform_csa_operations false 
#set_attr lp_insert_operand_isolation true
syn_gen

timestat GENERIC

syn_map 

#synthesize -to_mapped -eff $MAP_EFF -incr  

check_design -all 


report qor

write_hdl -mapped > statistics/decisiontree_based/non_pipelined/acc8_len8/netlist.v
write_hdl -generic > statistics/decisiontree_based/non_pipelined/acc8_len8/fastcrosslayer.v

puts "Final Runtime & Memory."
timestat FINAL
puts "============================"
puts "Synthesis Finished ........."
puts "============================"

report timing > statistics/decisiontree_based/non_pipelined/acc8_len8/timing.log

report gates  > statistics/decisiontree_based/non_pipelined/acc8_len8/gates.log

report area  -normalize_with_gate NAND2_X1 > statistics/decisiontree_based/non_pipelined/acc8_len8/area.log

report power  > statistics/decisiontree_based/non_pipelined/acc8_len8/power.log

quit
