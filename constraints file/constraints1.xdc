create_clock -period 10.000 -name clk -waveform {0.000 5.000} [get_ports clk]

set_input_delay -clock [get_clocks clk] -min -add_delay 0.200 [get_ports reset]
set_input_delay -clock [get_clocks clk] -max -add_delay 0.200 [get_ports reset]
set_input_delay -clock [get_clocks clk] -min -add_delay 0.200 [get_ports rx]
set_input_delay -clock [get_clocks clk] -max -add_delay 0.200 [get_ports rx]
set_output_delay -clock [get_clocks clk] -min -add_delay 0.000 [get_ports tx]
set_output_delay -clock [get_clocks clk] -max -add_delay 0.200 [get_ports tx]

set_property IOSTANDARD LVCMOS18 [get_ports clk]
set_property PACKAGE_PIN W5 [get_ports clk]

set_property IOSTANDARD LVCMOS18 [get_ports rx]
set_property PACKAGE_PIN B18 [get_ports rx]

set_property IOSTANDARD LVCMOS18 [get_ports reset]
set_property PACKAGE_PIN R2 [get_ports reset]

set_property IOSTANDARD LVCMOS18 [get_ports tx]
set_property PACKAGE_PIN A18 [get_ports tx]
