# @file: parseHtml.py
# @purpose: a HTML tag generator
# @author: wangxg

__doc__ = """The pyh.py module is the core of the PyH package
"""
__author__ = "wangxg"
__version__ = '$Revision: 63 $'
__date__ = '$Date: 2013-05-21 03:09:03 +0200 (Fri, 21 May 2010) $'

from sys import _getframe, stdout, modules, version
nOpen={}

nl = '\n'
doctype = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
charset = '<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />\n'

tags = ['html', 'body', 'head', 'link', 'meta', 'div', 'p', 'form', 'legend', 
        'input', 'select', 'span', 'b', 'i', 'option', 'img', 'script',
        'table', 'tr', 'td', 'th', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'fieldset', 'a', 'title', 'body', 'head', 'title', 'script', 'br', 'table',
        'ul', 'li', 'ol']

selfClose = ['input', 'img', 'link', 'br']

class Tag(list):
    tagname = ''
    
    def __init__(self, *arg, **kw):
        self.attributes = kw
        if self.tagname : 
            name = self.tagname
            self.isSeq = False
        else: 
            name = 'sequence'
            self.isSeq = True
        self.id = kw.get('id', name)
        #self.extend(arg)
        for a in arg: self.addObj(a)

    def __iadd__(self, obj):
        if isinstance(obj, Tag) and obj.isSeq:
            for o in obj: self.addObj(o)
        else: self.addObj(obj)
        return self
    
    def addObj(self, obj):
        if not isinstance(obj, Tag): obj = str(obj)
        id=self.setID(obj)
        setattr(self, id, obj)
        self.append(obj)

    def setID(self, obj):
        if isinstance(obj, Tag):
            id = obj.id
            n = len([t for t in self if isinstance(t, Tag) and t.id.startswith(id)])
        else:
            id = 'content'
            n = len([t for t in self if not isinstance(t, Tag)])
        if n: id = '%s_%03i' % (id, n)
        if isinstance(obj, Tag): obj.id = id
        return id

    def __add__(self, obj):
        if self.tagname: return Tag(self, obj)
        self.addObj(obj)
        return self

    def __lshift__(self, obj):
        self += obj
        if isinstance(obj, Tag): return obj

    def render(self):
        result = ''
        if self.tagname:
            result = '<%s%s%s>' % (self.tagname, self.renderAtt(), self.selfClose()*' /')
        if not self.selfClose():
            for c in self:
                if isinstance(c, Tag):
                    result += c.render()
                else: result += c
            if self.tagname:
                result += '</%s>' % self.tagname
        result += '\n'
        return result

    def renderAtt(self):
        result = ''
        for n, v in self.attributes.iteritems():
            if n != 'txt' and n != 'open':
                if n == 'cl': n = 'class'
                result += ' %s="%s"' % (n, v)
        return result

    def selfClose(self):
        return self.tagname in selfClose 
    
def TagFactory(name):
    class f(Tag):
        tagname = name
    f.__name__ = name
    return f

thisModule = modules[__name__]

for t in tags: setattr(thisModule, t, TagFactory(t)) 

def ValidW3C():
    out = a(img(src='http://www.w3.org/Icons/valid-xhtml10', alt='Valid XHTML 1.0 Strict'), href='http://validator.w3.org/check?uri=referer')
    return out

class PyH(Tag):
    tagname = 'html'
    
    def __init__(self, name='MyPyHPage'):
        self += head()
        self += body()
        self.attributes = dict(xmlns='http://www.w3.org/1999/xhtml', lang='en')
        self.head += title(name)

    def __iadd__(self, obj):
        if isinstance(obj, head) or isinstance(obj, body): self.addObj(obj)
        elif isinstance(obj, meta) or isinstance(obj, link): self.head += obj
        else:
            self.body += obj
            id=self.setID(obj)
            setattr(self, id, obj)
        return self

    def addJS(self, *arg):
        for f in arg: self.head += script(type='text/javascript', src=f)

    def addCSS(self, *arg):
        for f in arg: self.head += link(rel='stylesheet', type='text/css', href=f)
    
    def printOut(self,file=''):
        if file: f = open(file, 'w')
        else: f = stdout
        f.write(doctype)
        f.write(self.render())
        f.flush()
        if file: f.close()
        
#page = PyH("Automation Report")

def createStatisticTable(page):
    table1 = page << table(border='1',id='mytable1',align= "center")
    headtr = table1 << tr(id='headline')
    headtr.attributes['bgcolor'] = "#8080FF"
    headtr << td('Module') << td('Total') << td('Passed')<< td('Failed') 
    
    return table1

def addTdToTable(table_name, 
                 module_name,
                 module_total, 
                 module_passed, 
                 module_failed):
    tr1 = table_name << tr(id='line1')
    #tr1.attributes['bgcolor'] = "#8080FF"
    tr1 << td(module_name) << td(module_total) << td(module_passed) << td(module_failed)


def createCaseDetailTable(page):
    table2 = page << table(border='0.2',id='total_table2', align= "center")
    headtr = table2 << tr(id='headline',height='30')
    headtr.attributes['bgcolor'] = "#8080FF"
    
    headtr << td('State') << td('TestCase ID') << td('Priority') \
    << td('Module') << td('Title') << td('Note')
    return table2


def addTbtoSttsTable(table2, 
                     case_state, 
                     case_id,
                     case_pri,
                     moduel_name, 
                     case_title, 
                     case_log,
                     case_info):
    tr3 = table2  << tr(id='line1')
    td_link = td('', align="center")
    link1 = td_link << a(case_id)
    link1.attributes['href'] = case_log
    if case_state == 'Failed':
        tr3.attributes['bgcolor'] = '#FF0000'
    else:
        tr3.attributes['bgcolor'] = '#FFE6FF'
    tr3 << td(case_state) <<td_link  << td(case_pri, align="center") \
    << td(moduel_name) << td(case_title) << td(case_info)

def createEmptyTable(page, top=True, bottom=True):
    emp_table = page << table(width="100%", id='emptytable')
    if top == True:
        emp_table << tr(id='empty', height="2")
    headtr = emp_table << tr(id='empty')
    headtr.attributes['bgcolor'] = '#C50EFF'
    td_link = td(height="1", align="center")
    headtr << td_link
    if bottom == True:
        emp_table << tr(id='empty', height="2")