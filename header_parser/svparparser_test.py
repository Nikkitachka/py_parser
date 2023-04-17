# This test uses SVParParser to parse parameters
# from test modules and print parse log

import PyVerilog_Parser as pyvp

parser = pyvp.PyVerilog_Parser("/home/nikkitachka/Desktop/py_parser/header_parser/test_modules/test_module_1.v")
parser.head_parse()
parser.parse_file_log()
parser.PyVerilog()
parser.ast_parse()