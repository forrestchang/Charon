###############
# Lexer       #
###############


def lexer(text):
    return text.replace('(', ' ( ').replace(')', ' ) ').split()

##############
# Parser     #
##############
Symbol = str
List = list
Number = (int, float)


def parser(program):
    return read_from_tokens(lexer(program))


def read_from_tokens(tokens):
    if len(tokens) == 0:
        raise SyntaxError('unexcepted EOF while reading')

    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0)
        return L
    elif token == ')':
        raise SyntaxError('unexcepted )')
    else:
        return atom(token)


def atom(token):
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)

###############
# Environment #
###############


class Procedure(object):
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env

    def __call__(self, *args):
        return eval(self.body, Env(self.parms, args, self.env))


class Env(dict):
    def __init__(self, parms=(), args=(), outer=None, **kwargs):
        super(Env, self).__init__(**kwargs)
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, var):
        return self if (var in self) else self.outer.find(var)


def standard_env():
    import math
    import operator
    from functools import reduce
    env = Env()
    env.update(vars(math))
    env.update({'+': lambda *args: reduce(lambda x, y: x + y, args),
                '-': lambda *args: reduce(lambda x, y: x - y, args),
                '*': lambda *args: reduce(lambda x, y: x * y, args),
                '/': lambda *args: reduce(lambda x, y: x / y, args),
                '>': lambda x, y: x > y,
                '>=': lambda x, y: x >= y,
                '<': lambda x, y: x < y,
                '<=': lambda x, y: x <= y,
                '=': lambda x, y: x == y,
                'abs': abs,
                'append': lambda *args: reduce(lambda x, y: x + y, args),
                'begin': lambda *x: x[-1],
                'car': lambda x: x[0],
                'cdr': lambda x: x[1:],
                'cons': lambda x, y: [x] + y,
                'eq?': lambda x, y: isinstance(x, y),
                'equal?': lambda x, y: x == y,
                'length': len,
                'list': lambda *x: list(x),
                'list?': lambda x: isinstance(x, list),
                'map': map,
                'min': min,
                'max': max,
                'not': operator.not_,
                'null?': lambda x: x == [],
                'number?': lambda x: isinstance(x, Number),
                'procedure': callable,
                'round': round,
                'symbol': lambda x: isinstance(x, Symbol)
                })
    return env

global_env = standard_env()

###############
# Evaluation  #
###############


def eval(x, env=global_env):
    if isinstance(x, Symbol):
        return env.find(x)[x]
    elif not isinstance(x, List):
        return x
    elif x[0] == 'quote':
        (_, exp) = x
        return exp
    elif x[0] == 'if':
        (_, test, conseq, alt) = x
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif x[0] == 'define':
        (_, var, exp) = x
        env[var] = eval(exp, env)
    elif x[0] == 'set!':
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    elif x[0] == 'lambda':
        (_, parms, body) = x
        return Procedure(parms, body, env)
    else:
        proc = eval(x[0], env)
        args = [eval(exp, env) for exp in x[1:]]
        return proc(*args)

##############
# REPL       #
##############


def repl():
    while True:
        try:
            text = input('>>> ')
        except EOFError:
            break
        if not text:
            continue
        ast = parser(text)
        result = eval(ast)
        if result is not None:
            print(result)

#############
# Test      #
#############


def main():
    repl()

if __name__ == '__main__':
    main()
