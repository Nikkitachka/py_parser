from __future__                 import absolute_import
from __future__                 import print_function

import io
import re
import os
import sys
import ply
import warnings
import itertools
import pyverilog

import numpy                    as     np
import pandas                   as     pd

from   tabulate                 import tabulate
from   prettytable              import PrettyTable
from   optparse                 import OptionParser
from   pyverilog.vparser.ast    import *
from   pyverilog.vparser.parser import parse
# /home/nikkitachka/.local/lib/python3.10/site-packages/pyverilog/vparser - расположение pyverilog

class Verilog_Parser:
    def __init__(self, filepath: str):

        self.filepath = filepath
        self.head_signal_typ = []
        self.head_signal_d_t = []
        self.head_signal_n_r = []
        self.head_signal_v_w = []
        self.head_signal_nam = []
        self.head_signal_arr = []
        self.head_signal_clk = []
        self.head_signal_rst = []

    def head_parse(self):
        print(self.filepath)
        with open(self.filepath, "r") as input_file:
            for line in input_file:
                signal_type = ["input",  "output"]                                                                  # типы сигналов (входные / выходные)
                for st in signal_type:
                    if( st in line):
                        self.head_signal_typ.append(st)
                        signal_str_default = re.search('(.*)\n', line).group(1)                                     # захват всей строки в signal_str_default
                        signal_str         = signal_str_default                                                     # дублирование signal_str_default в signal_str
                        signal_str         = re.search(st + '(.*)', signal_str_default).group(1)                    # ищет в строке 'input/output' + (бесконечно символов)' и удаляет (input/output)
                        signal_str         = re.sub(',', '', re.sub('\s', '', signal_str))                          # удаление пробелов (\s - соответствует любому символу пробела ~ [ \t\n\r\f\v]) и запятых

                        data_type = ["reg", "wire", "integer", "real", "time", "realtime",                          # типы данных Verilog
                                     "logic", "bit", "byte", "shortint", "int", "longint", "shortreal"]             # типы данных SystemVerilog
                        self.head_signal_d_t.append('')                                                             # поиск типа данных сигнала ...
                        for dt in data_type:
                            if (re.search(dt, line)):
                                signal_data_type = dt
                                self.head_signal_d_t[len(self.head_signal_d_t)-1] = signal_data_type
                                signal_str = re.search(dt + '(.*)', signal_str).group(1)                            #                           ...

                        num_representation = ["signed", "unsigned"]                                                 # представление чисел (знак / беззнак)
                        self.head_signal_n_r.append('')                                                             # поиск представления чисел ...
                        for nr in num_representation:
                            if (re.search(nr, line)):
                                signal_num_representation = nr
                                self.head_signal_n_r[len(self.head_signal_n_r)-1] = signal_num_representation
                                signal_str = re.search(nr + '(.*)', signal_str).group(1)                            #                           ...

                        signal_vector_width, flag_v_m  = self.get_signal_v_w(signal_str)                            # извлечение ширины (измерения) сигнала
                        self.head_signal_v_w.append(signal_vector_width)
                        if (flag_v_m):
                            signal_str = signal_str.replace(signal_vector_width, '', 1)

                        signal_array_size, flag_arr  = self.get_signal_arr(signal_str)                              # извлечение размера массива сигнала
                        self.head_signal_arr.append(signal_array_size)
                        if (flag_arr):
                            signal_str = signal_str.replace(signal_array_size, '', 1)

                        signal_name = signal_str
                        self.head_signal_nam.append(signal_name)

                        signal_clk = ["clk", "CLK", "clock"]                                                        # CLK - используется в параметрах,но пока тут пусть побудет
                        self.head_signal_clk.append('')
                        for clk in signal_clk:
                            if (re.search(clk, signal_name)):
                                self.head_signal_clk[len(self.head_signal_clk)-1] = 'clk'
                                # self.head_signal_clk.append(clk)

                        signal_rst = ["rst", "RST", "reset"]
                        self.head_signal_rst.append('')
                        for rst in signal_rst:
                            if (re.search(rst, signal_name)):
                                self.head_signal_rst[len(self.head_signal_rst)-1] = 'rst'
                                # self.head_signal_rst.append(rst)

    #############################################################################################################################

    def get_signal_v_w(self, param_str: str):
        """
        Parameters
        ----------

        param_str: str
            String with parameter definition.
        """

        if('[' in param_str):
            if  (re.search(r"\][^\[](.*)", param_str) and re.search(r"(.*)[^\]]\[", param_str)):
                param_ind = (re.match(r"\[(.*)\][^\[]", param_str).group(1))
                param_ind = '[' + param_ind + ']'
                flag = 1
            elif(re.search(r"\][^\[](.*)", param_str)):
                param_ind = (re.match(r"\[(.*)\]", param_str).group(0))
                flag = 1
            else:
                param_ind = [1]
                flag = 0
        else:
            param_ind = [1]
            flag = 0
        return param_ind, flag

    #############################################################################################################################

    def get_signal_arr(self, param_str: str):
        """
        Parameters
        ----------

        param_str: str
            String with parameter definition.
        """

        if('[' in param_str):
            if  (re.search(r"\[(.*)\]", param_str)):
                param_ind = (re.search(r"\[(.*)\]", param_str).group(1))
                param_ind = '[' + param_ind + ']'
                flag = 1
            else:
                param_ind = [1]
                flag = 0
        else:
            param_ind = [1]
            flag = 0
        return param_ind, flag

    #############################################################################################################################
    # txt file output

    def parse_file_log(self):
        with io.open("/home/nikkitachka/Desktop/py_parser/header_parser/out/parser_log.txt", "w", encoding="utf-16") as f:
            f.write("PyVerilog_Parser log:\n")
            def_head_params_str = '{} header defined signal(s) was(were) founded:\n'

            f.write(def_head_params_str.format(str(len(self.head_signal_nam))))

            head_signals = {'Signal\ntype'          : self.head_signal_typ,
                            'Data\ntype'            : self.head_signal_d_t,
                            'Number\nrepresentation': self.head_signal_n_r,
                            'Vector width'          : self.head_signal_v_w,
                            'Name'                  : self.head_signal_nam,
                            'Array size'            : self.head_signal_arr,
                            'Clock'                 : self.head_signal_clk,
                            'Reset'                 : self.head_signal_rst}

            table_def_head_params = pd.DataFrame(head_signals)
            f.write(str(tabulate(table_def_head_params, headers='keys', tablefmt='grid', stralign='center', numalign="center")) + '\n')

            f.close()
            if f.closed:
                print('file is closed')

        with io.open("/home/nikkitachka/Desktop/py_parser/header_parser/out/parser_log.txt", "r", encoding="utf-16") as f:    # вывод данных из файла в терминал
            print(f.read())
            f.close()
            if f.closed:
                print('file is closed')

class PyVerilog_Parser:
    def __init__(self, filepath, filepars: str):

        self.filepath = filepath
        self.filepars = filepars
        self.head_signal_typ = []
        self.head_signal_d_t = []
        self.head_signal_n_r = []
        self.head_signal_v_w = []
        self.head_signal_nam = []
        self.head_signal_arr = []
        self.head_signal_clk = []
        self.head_signal_rst = []
        self.head_signal_lin = []

    #############################################################################################################################

    def PyVerilog(self):
        filelist = []
        filelist.append(self.filepath)

        if os.path.isfile(self.filepars):
            os.remove(self.filepars)
            print("Success\n")
        else:
            print("File doesn't exists!")

        ast, directives = parse(filelist,
                                preprocess_include = [],
                                preprocess_define  = [])

        ast.show()
        print("\n")

        # with io.open(self.filepars, "r") as f:
        #     print(f.read())
        #     f.close()
        #     if f.closed:
        #         print('file is closed')

    #############################################################################################################################
    
    def ast_parse(self):

        print(self.filepath, "\n")
        print(self.filepars, "\n")

        signal_type = ["Input",  "Output"]

        data_type =   ["reg", "wire", "integer", "real", "time", "realtime",                                    # типы данных Verilog
                       "logic", "bit", "byte", "shortint", "int", "longint", "shortreal"]  

        operation =   []

        with open(self.filepars, "r") as parsed_file:
            for line in parsed_file:
                print(line)
                # Module name parse
                if ( "ModuleDef" in line ):                                                                     # считывание названия модуля
                    def_line = re.search('(.*)\n', line).group(1)                                               # захват всей строки в def_line
                    def_line = re.search("ModuleDef:" + '(.*)', def_line).group(1)                              # ищет в строке 'ModuleDef' + (бесконечно символов)' и удаляет (ModuleDef)
                    def_line = re.sub(',', '', re.sub('\s', '', re.sub(r'\([^\)]+\)', '', def_line)))           # удаление лишнего (\s - соответствует любому символу пробела ~ [ \t\n\r\f\v]) и запятых
                    self.module_name = def_line
                    continue                                                                                    # переход к следующей итерации во внешнем цикле

                # Parameter parse
                if ( "Parameter" in line ):                                                                     # считывание параметров модуля
                    self.head_signal_typ.append("Parameter")                                                    # тип сигнала - праметр
                    self.head_signal_d_t.append('')
                    self.head_signal_clk.append('')
                    self.head_signal_rst.append('')
                    self.head_signal_n_r.append('')                                                             # знаковый/беззнаковый параметр
                    if ( "True" in line ):
                        self.head_signal_n_r[len(self.head_signal_n_r)-1] = "signed"
                    def_line = re.search('(.*)\n', line).group(1)                                               # захват всей строки в def_line
                    def_line = re.search("Parameter:" + '(.*)', def_line).group(1)                              # ищет в строке 'Parameter' + (бесконечно символов)' и удаляет (Parameter)
                    self.head_signal_lin.append(re.sub('\s', '',(re.sub(r'^.*?\([a][t][ ]', '', (re.sub(r'\)', '', line))))))  # вычленение номера строки кода с которой работаем 
                    def_line = re.sub(',', '', re.sub('\s', '', re.sub(r'\,[^\)]+\)', '', def_line)))           # удаление лишнего (\s - соответствует любому символу пробела ~ [ \t\n\r\f\v]) и запятых
                    self.head_signal_nam.append(def_line)
                    continue                                                                                    # переход к следующей итерации во внешнем цикле

                if not self.head_signal_lin:
                    print("List number of code lines is empty")
                # else:
                elif ( self.head_signal_lin[-1] == re.sub('\s', '',(re.sub(r'^.*?\([a][t][ ]', '', (re.sub(r'\)', '', line)))))):
                    print(self.head_signal_lin[-1])



                # if ( "Rvalue" in line ):
                #     print("pipi-pupu") 

                    # self.head_signal_typ = [] +
                    # self.head_signal_d_t = [] +
                    # self.head_signal_n_r = [] +
                    # self.head_signal_v_w = [] -
                    # self.head_signal_nam = [] +
                    # self.head_signal_arr = [] -
                    # self.head_signal_clk = [] +
                    # self.head_signal_rst = [] +

                # searched_strs = ["Input", "Output", "Inout", "Tri", "Wire", "Reg"]
                # for st in searched_strs:
                #     if( st in line):
                #         self.head_signal_typ.append(st)
                #         signal_str_default = re.search('(.*)\n', line).group(1)                                     # захват всей строки в signal_str_default
                #         signal_str         = signal_str_default                                                     # дублирование signal_str_default в signal_str
                #         signal_str         = re.search(st + '(.*)', signal_str_default).group(1)                    # ищет в строке 'input/output' + (бесконечно символов)' и удаляет (input/output)
                #         signal_str         = re.sub(',', '', re.sub('\s', '', signal_str))                          # удаление пробелов (\s - соответствует любому символу пробела ~ [ \t\n\r\f\v]) и запятых

                #         data_type = ["reg", "wire", "integer", "real", "time", "realtime",                          # типы данных Verilog
                #                      "logic", "bit", "byte", "shortint", "int", "longint", "shortreal"]             # типы данных SystemVerilog
                #         self.head_signal_d_t.append('')                                                             # поиск типа данных сигнала ...
                #         for dt in data_type:
                #             if (re.search(dt, line)):
                #                 signal_data_type = dt
                #                 self.head_signal_d_t[len(self.head_signal_d_t)-1] = signal_data_type
                #                 signal_str = re.search(dt + '(.*)', signal_str).group(1)                            #                           ...

                #         num_representation = ["signed", "unsigned"]                                                 # представление чисел (знак / беззнак)
                #         self.head_signal_n_r.append('')                                                             # поиск представления чисел ...
                #         for nr in num_representation:
                #             if (re.search(nr, line)):
                #                 signal_num_representation = nr
                #                 self.head_signal_n_r[len(self.head_signal_n_r)-1] = signal_num_representation
                #                 signal_str = re.search(nr + '(.*)', signal_str).group(1)                            #                           ...

                #         signal_vector_width, flag_v_m  = self.get_signal_v_w(signal_str)                            # извлечение ширины (измерения) сигнала
                #         self.head_signal_v_w.append(signal_vector_width)
                #         if (flag_v_m):
                #             signal_str = signal_str.replace(signal_vector_width, '', 1)

                #         signal_array_size, flag_arr  = self.get_signal_arr(signal_str)                              # извлечение размера массива сигнала
                #         self.head_signal_arr.append(signal_array_size)
                #         if (flag_arr):
                #             signal_str = signal_str.replace(signal_array_size, '', 1)

                #         signal_name = signal_str
                #         self.head_signal_nam.append(signal_name)

                #         signal_clk = ["clk", "CLK", "clock"]                                                        # CLK - используется в параметрах,но пока тут пусть побудет
                #         self.head_signal_clk.append('')
                #         for clk in signal_clk:
                #             if (re.search(clk, signal_name)):
                #                 self.head_signal_clk[len(self.head_signal_clk)-1] = 'clk'
                #                 # self.head_signal_clk.append(clk)

                #         signal_rst = ["rst", "RST", "reset"]
                #         self.head_signal_rst.append('')
                #         for rst in signal_rst:
                #             if (re.search(rst, signal_name)):
                #                 self.head_signal_rst[len(self.head_signal_rst)-1] = 'rst'
                #                 # self.head_signal_rst.append(rst)



        # with io.open("/home/nikkitachka/Desktop/py_parser/header_parser/out/pyverilog_log.txt", "r") as f:
        #     lines = f.readlines()
        #     for i in range(len(lines)):
        #         # определить первое слово вывода парсера
        #             # пропускаем Source, Description, ModuleDef, Paramlist, Portlist
        #         ignore_strs   = ["Source", "Description", "ModuleDef", "Paramlist", "Portlist", "Decl"]
        #             # находим строки, которые начинаются с Input, Output, Reg..
        #         searched_strs = ["Input", "Output", "Inout", "Tri", "Wire", "Reg"]
                
        #         tab_count = lines[i].count("\t")    # число табов в проверяемой строке
                
        #         op   = []                           # операция
        #         op_A = []                           # первый операнд
        #         op_B = []                           # второй операнд
                
        #         if ( searched_strs in lines[i] ):
        #             self.head_signal_typ.append(searched_strs)



        # # построковый вывод из файла
        # with io.open(self.filepars, "r") as f:
        #     lines = f.readlines()
        #     for i in range(len(lines)):
        #         print(lines[i], end = "")

        #     f.close()
        #     if f.closed:
        #         print('\nfile is closed')

    #############################################################################################################################