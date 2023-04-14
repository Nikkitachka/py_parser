# This test uses SVParParser to parse parameters
# from test modules and print parse log

import PyVerilog_Parser as pyvp

parser = pyvp.PyVerilog_Parser("/home/nikkitachka/Desktop/py_parser/header_parser/test_modules/test_module_1.v")
parser.head_parse()
parser.parse_file_log()
parser.PyVerilog()

# # ## NEW PART WITH PYVERILOG PARSERclear

# from __future__ import absolute_import
# from __future__ import print_function
# import sys
# import os
# from   optparse import OptionParser
# import pyverilog
# from   pyverilog.vparser.parser import parse

# def main():
#     optparser = OptionParser()
#     optparser.add_option("-v", "--version", action="store_true", dest="showversion",
#                          default=False, help="Show the version")
#     optparser.add_option("-I", "--include", dest="include", action="append",
#                          default=[], help="Include path")
#     optparser.add_option("-D", dest="define", action="append",
#                          default=[], help="Macro Definition")
#     (options, args) = optparser.parse_args()
#     print(options)

#     filelist = args
#     print(filelist)
#     # filelist = []
#     # filelist.append("test.v")
#     # print(filelist)

#     ast, directives = parse(filelist,
#                             preprocess_include=options.include,
#                             preprocess_define=options.define)

#     ast.show()

# if __name__ == '__main__':  ## проверка запуска файла напрямую
#     main()