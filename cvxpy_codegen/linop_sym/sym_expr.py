"""
Copyright 2017 Nicholas Moehle

This file is part of CVXPY-CODEGEN.

CVXPY-CODEGEN is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CVXPY-CODEGEN is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CVXPY-CODEGEN.  If not, see <http://www.gnu.org/licenses/>.
"""



class SymExpr():
    "abstract class"

    def __mul__(self, expr):
        if isinstance(self, SymConst) and self.value == 1.0:
            return expr
        elif isinstance(expr, SymConst) and expr.value == 1.0:
            return self
        else:
            return SymMult(self, expr)
        return SymMult(self, expr)

    def __rmul__(self, expr):
        return SymMult(expr, self)

    def __add__(self, expr):
        #if isinstance(self, SymAdd):
        #    return SymAdd(self.args
        return SymAdd(self, expr)

    def __truediv__(self, expr):
        return SymDiv(self, expr)

    def __neg__(self):
        return SymConst(-1.0) * self



class SymConst(SymExpr):
    def __init__(self, value):
        self.value = float(value)

    def print(self):
        return str(self.value)
        

class SymParam(SymExpr):
    def __init__(self, param, idx, nz_idx):
        self.param = param
        self.idx = idx
        self.nz_idx = nz_idx

    def print(self):
        return(self.param.name()+'['+str(self.idx[0])+','+str(self.idx[1])+']')

    @property
    def value(self):
        if self.param.size == (1,1):
            return self.param.value
        else:
            return self.param.value[self.idx[0], self.idx[1]]


class SymAdd(SymExpr):
    def __init__(self, arg1, arg2):
        self.args = []
        if isinstance(arg1, SymAdd):
            self.args += arg1.args
        else:
            self.args += [arg1]
        if isinstance(arg2, SymAdd):
            self.args += arg2.args
        else:
            self.args += [arg2]

    @property
    def value(self):
        return sum([a.value for a in self.args])

    def print(self):
        s = '( '
        for a in self.args[:-1]:
            s += a.print() + ' + '
        s += self.args[-1].print() + ' )'
        return s

class SymMult(SymExpr):
    def __init__(self, arg1, arg2):
        self.args = [arg1, arg2]

    @property
    def value(self):
        return self.args[0].value * self.args[1].value

    def print(self):
        return '( ' + self.args[0].print() + ' * ' + self.args[1].print() + ' )'


class SymDiv(SymExpr):
    def __init__(self, arg1, arg2):
        self.args = [arg1, arg2]

    @property
    def value(self):
        #print('\n')
        #print(self.args[0].value)
        #print(self.args[1].value)
        return self.args[0].value / self.args[1].value

    def print(self):
        return '( ' + self.args[0].print() + ' / ' + self.args[1].print() + ' )'

