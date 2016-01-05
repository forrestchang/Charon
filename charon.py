class Env(dict):
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, var):
        return self if var in self else self.outer.find(var)

def add_globals(env):
    "Add some Scheme standard procedure to an environment."
    import math, operator as op
    env.update(vars(math))
    env.update({'+': op.add,
                '-': op.sub,
                '*': op.mul,
                '/': op.truediv,
                'not': op.not_,
                '>': op.gt,
                '<': op.lt,
                '>=': op.ge,
                '<=': op.le,
                '=': op.eq,
                'equal?': op.eq,
                'eq?': op.is_,
                'length': len,
                'cons': lambda x, y: [x] + y,
                'car': lambda x: x[0],
                'cdr': lambda x: x[1:],
                'append': op.add,
                'list': lambda *x: list(x),
                'list?': lambda x: isinstance(x, list),
                'null?': lambda x: x == [],
                'symbol?': lambda x: isinstance(x, str),
                })
    return env

def eval(x, env=add_globals(Env())):
    "Evaluate an expression in an environment."
    if isinstance(x, str):
        return env.find(x)[x]
    elif not isinstance(x, list):
        return x
    elif x[0] == 'quote':
        (_, exp) = x
        return exp
    elif x[0] == 'if':
        (_, test, conseq, alt) = x
        return eval((conseq if eval(test, env) else alt), env)
    elif x[0] == 'set!':
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    elif x[0] == 'define':
        (_, var, exp) = x
        env[var] = eval(exp, env)
    elif x[0] == 'lambda':
        (_, vars, exp) = x
        return lambda *args: eval(exp, Env(vars, args, env))
    elif x[0] == 'begin':
        for exp in x[1:]:
            val = eval(exp, env)
        return val
    else:
        exps = [eval(exp, env) for exp in x]
        proc = exps.pop(0)
        return proc(*exps)





def read(s):
    "Read a Scheme expression from a string."
    return read_from(tokenize(s))

parse = read

def tokenize(s):
    "Convert a string into a list of tokens."
    return s.replace('(', ' ( ').replace(')', ' ) ').split()

def read_from(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while readind')
    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_from(tokens))
        tokens.pop(0)

        return L
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token):
    "Numbers become numbers, any other token become string(Symbol)."
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return str(token)

def to_string(exp):
    "Convert a Python object back into a Lisp-readable string."
    return '('+' '.join(map(to_string, exp))+')' if isinstance(exp, list) else str(exp)

def repl():
    "A prompt-read-eval-print loop."
    while True:
        text = input('>>> ')
        val = eval(parse(text))
        if val is not None:
            print(to_string(val))

def main():
    repl()

if __name__ == '__main__':
    main()