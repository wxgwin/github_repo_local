#!/usr/bin/python
'''an example for generate html page.
the module used is:PyH
Its home page is: http://code.google.com/p/pyh/
we can download it at:http://code.google.com/p/pyh/downloads/detail?name=PyH-0.1.1.tar.gz&can=2&q=
More things about html at:http://www.w3school.com.cn/tags/tag_div.asp
'''

import  datetime

from pyh import *
page = PyH("Automation Report")


def createStatisticTable():
    table2 = page << table(border='1',id='total_table2')
    headtr = table2 << tr(id='headline')
    headtr.attributes['bgcolor'] = '#408080'
    td_link = td('State',bgcolor="#F00000")
    
    headtr << td_link << td('TestCase ID') << td('Module') << td('Title')
    return table2


def addTbtoSttsTable(table2):
    tr3 = table2  << tr(id='line1')
    td_link = td('', align="center")
    link1 = td_link << a('BSP-2')
    link1.attributes['href'] = 'test.txt'
    tr3 << td('Passed') <<td_link


def addDetailTable():
    table1 = page << table(border='1',id='mytable1')
    headtr = table1 << tr(id='headline')
    headtr << td('Module name') << td('Total') << td('Passed')<< td('Failed')
    
    return table1


def addTdToTable(table_name):
    tr1 = table_name << tr(id='line1')
    tr1.attributes['bgcolor'] = '#FF00000'
    tr1 << td('VIDio') << td('10') << td('1') << td('9')
    
    tr2 = table_name << tr(id='line2')
    tr2 << td('r2,c1') <<td('r2,c2')

### mains
page <<h1('BSP Automation Report',align='center')

page << div(align='center',id='') << p(datetime.datetime.now(),id='myp1')

mydiv2 = page << div(id='myDiv2')
mydiv2 <<h2('Test Case Version: ') #<< p

addTdToTable(addDetailTable())

mydiv3 = page << div(id='myDiv3')
mydiv3.attributes['align'] = 'center'
mydiv3.attributes['style'] = 'background:#000;color:#00FF00'

mydiv3 << p('Detail information of automation test case')


addTbtoSttsTable(createStatisticTable())

page.printOut(file=r'D:\tool\eclipse\wrtm-workspace\html\test.html')