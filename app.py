from flask import Flask, render_template, request
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

reserved = {
    'for': 'FOR',
    'int': 'INT',
}

tokens = [
    'ID',
    'NUMBER',
    'STRING',
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'SEMICOLON',
    'ASSIGN',
    'INCREMENT',
    'LESSTHANOREQUAL',
    'DOT',
] + list(reserved.values())

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SEMICOLON = r';'
t_ASSIGN = r'='
t_INCREMENT = r'\+\+'
t_LESSTHANOREQUAL = r'<='
t_DOT = r'\.'

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]  
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID') 
    return t

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

# Manejo de errores
def t_error(t):
    if t.value[0] not in ' \t\n\r':
        error = f"Carácter ilegal '{t.value[0]}' en la línea {t.lineno}"
        # errors.append(error)
    t.lexer.skip(1)

lexer = lex.lex()

# Reglas de gramática
def p_for_loop(p):
    '''
    for_loop : FOR LPAREN INT ID ASSIGN NUMBER SEMICOLON ID LESSTHANOREQUAL NUMBER SEMICOLON ID INCREMENT RPAREN LBRACE system_out RBRACE
    '''
    if int(p[6]) >= int(p[10]):
        error = "Error semántico: La condición de parada del bucle debe ser mayor que el valor inicial"
        errors.append(error)
        return
    p[0] = 'Ciclo for válido'

def p_system_out(p):
    '''
    system_out : ID DOT ID DOT ID LPAREN STRING RPAREN SEMICOLON
    '''
    if p[1] != 'System' or p[3] != 'out' or p[5] != 'println':
        error = "Error semántico: Uso incorrecto de System.out.println"
        errors.append(error)
        return
    p[0] = 'System.out.println válido'

# Manejo de errores
def p_error(p):
    if p:
        error = f"Error en la sintaxis del bucle 'for', verifica el cuerpo del bucle "
        errors.append(error)
    else:
        error = "Error de sintaxis al final del bloque, se esperaba un }"
        errors.append(error)

parser = yacc.yacc()

# Lista para almacenar errores
errors = []

def analyze_code(data):
    global errors
    errors = []
    lexer.input(data)
    parser.parse(data)
    return errors


def count_tokens(data):
    lexer.input(data)
    token_count = {'PR': 0, 'ID': 0, 'NUM': 0, 'SYM': 0, 'ERR': 0}

    for tok in lexer:
        token_type = tok.type
        if token_type in ['FOR', 'INT']:
            token_count['PR'] += 1
        elif token_type == 'ID':
            token_count['ID'] += 1
        elif token_type == 'NUMBER':
            token_count['NUM'] += 1
        elif token_type == 'STRING':
            pass
        else:
            token_count['SYM'] += 1

        tokens.append((tok.value, token_type))

    return token_count

@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    token_count = {}
    if request.method == 'POST':
        code = request.form['code']
        errors = analyze_code(code)
        token_count = count_tokens(code)
        if not errors:
            errors.append("El código es correcto.")
    return render_template('index.html', errors=errors, token_count=token_count)

if __name__ == '__main__':
    app.run(debug=True)
