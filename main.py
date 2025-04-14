from sympy import sympify

expr = sympify("1/2 + 1/3")

result = expr.evalf()
fraction_result = expr.simplify()

print(fraction_result)
