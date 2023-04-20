# This test uses SVParParser to parse parameters
# from test modules and print parse log

import PyVerilog_Parser as vp
# import PyVerilog_Parser as pyvp

ver_parser = vp.Verilog_Parser("/home/nikkitachka/Desktop/py_parser/header_parser/test_modules/test_module_4.v")
pyver_parser = vp.PyVerilog_Parser("/home/nikkitachka/Desktop/py_parser/header_parser/test_modules/test_module_4.v","/home/nikkitachka/Desktop/py_parser/header_parser/out/pyverilog_log.txt")
ver_parser.head_parse()
ver_parser.parse_file_log()
pyver_parser.PyVerilog()  # парсинг файла через pyverilog
pyver_parser.ast_parse()  # построковое чтение из файла