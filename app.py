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
    'LESSTHAN',
    'GREATERTHAN',
    'PLUS',
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
t_LESSTHAN = r'<'
t_GREATERTHAN = r'>'
t_PLUS = r'\+'

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
    for_loop : variable_declaration for_loop_inner_declaration
             | p_variable_variation for_loop_inner_variation 
             | for_loop_inner
    '''
    p[0] = 'Ciclo for válido'
    # Agrega los tokens del bucle for a la lista
    p.parser.for_loop_tokens.extend(p[1:])

def p_variable_variation(p):
    '''
    p_variable_variation : INT ID SEMICOLON
    '''
    p[0] = f'Declaración de variable {p[2]}'
    p.parser.var_name = p[2]

def p_variable_declaration(p):
    '''
    variable_declaration : INT ID ASSIGN NUMBER SEMICOLON
    '''
    p[0] = f'Declaración de variable {p[2]}'
    p.parser.var_name = p[2]

def p_for_loop_inner_variation(p):
    '''
    for_loop_inner_variation : FOR LPAREN ID ASSIGN NUMBER SEMICOLON ID LESSTHAN NUMBER SEMICOLON ID INCREMENT RPAREN LBRACE system_out RBRACE
                              | FOR LPAREN ID ASSIGN NUMBER SEMICOLON ID GREATERTHAN NUMBER SEMICOLON ID INCREMENT RPAREN LBRACE system_out RBRACE
                              | FOR LPAREN ID ASSIGN NUMBER SEMICOLON ID LESSTHANOREQUAL NUMBER SEMICOLON ID INCREMENT RPAREN LBRACE system_out RBRACE
    '''
    var_name = p.parser.var_name if hasattr(p.parser, 'var_name') else None
    if var_name and (p[3] != var_name or p[7] != var_name or p[11] != var_name):
        error = "Error semántico: La variable del ciclo for debe ser consistente en todas las partes"
        errors.append(error)
        return
    p[0] = 'Ciclo for válido'


def p_for_loop_inner_declaration(p):
    '''
    for_loop_inner_declaration : FOR LPAREN ID SEMICOLON ID LESSTHAN NUMBER SEMICOLON ID INCREMENT RPAREN LBRACE system_out RBRACE
                                | FOR LPAREN ID SEMICOLON ID GREATERTHAN NUMBER SEMICOLON ID INCREMENT RPAREN LBRACE system_out RBRACE
                                | FOR LPAREN ID SEMICOLON ID LESSTHANOREQUAL NUMBER SEMICOLON ID INCREMENT RPAREN LBRACE system_out RBRACE
    '''
    var_name = p.parser.var_name if hasattr(p.parser, 'var_name') else None
    if var_name and (p[3] != var_name or p[5] != var_name or p[9] != var_name):
        error = "Error semántico: La variable del ciclo for debe ser consistente en todas las partes"
        errors.append(error)
        return
    p[0] = 'Ciclo for válido'
    
def p_for_loop_inner(p):
    '''
    for_loop_inner : FOR LPAREN INT ID ASSIGN NUMBER SEMICOLON ID LESSTHAN NUMBER SEMICOLON ID INCREMENT RPAREN LBRACE system_out RBRACE
                    | FOR LPAREN INT ID ASSIGN NUMBER SEMICOLON ID GREATERTHAN NUMBER SEMICOLON ID INCREMENT RPAREN LBRACE system_out RBRACE
                    | FOR LPAREN INT ID ASSIGN NUMBER SEMICOLON ID LESSTHANOREQUAL NUMBER SEMICOLON ID INCREMENT RPAREN LBRACE system_out RBRACE
    '''
    if p[4] != p[8] or p[8] != p[12]:
        error = "Error semántico: La variable del ciclo for debe ser consistente en todas las partes"
        errors.append(error)
        return
    p[0] = 'Ciclo for válido'


def p_system_out_content(p):
    '''
    system_out_content : STRING
                       | ID
                       | system_out_content PLUS STRING
                       | system_out_content PLUS ID
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f"{p[1]} + {p[3]}"


def p_system_out(p):
    '''
    system_out : ID DOT ID DOT ID LPAREN system_out_content RPAREN SEMICOLON
    '''
    if p[1] != 'System' or p[3] != 'out' or p[5] != 'println':
        error = "Error semántico: Uso incorrecto de System.out.println"
        errors.append(error)
        return
    p[0] = f'System.out.println válido con contenido: {p[7]}'


# Manejo de errores
def p_error(p):
    if p:
        error = f"Error en la sintaxis del bucle 'for', verifica el cuerpo del bucle "
        errors.append(error)
    else:
        error = "Error de sintaxis al final del bloque, se esperaba un }"
        errors.append(error)

parser = yacc.yacc()

errors = []
parser.for_loop_tokens = []


def analyze_code(data):
    global errors
    errors = []
    lexer.input(data)
    tokens = []
    for tok in lexer:
        tokens.append((tok.value, tok.type))  
    parser.parse(data)
    return errors, tokens

def count_tokens(data):
    lexer.input(data)
    token_count = {'PR': 0, 'ID': 0, 'NUM': 0, 'SYM': 0, 'ERR': 0}

    for tok in lexer:
        token_type = tok.type
        if token_type == 'FOR' or token_type == 'INT':
            token_count['PR'] += 1
        elif token_type == 'ID':
            token_count['ID'] += 1
        elif token_type == 'NUMBER':
            token_count['NUM'] += 1
        elif token_type == 'STRING':
            pass
        else:
            token_count['SYM'] += 1

    return token_count



@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    token_count = {}
    for_loop_tokens = []
    if request.method == 'POST':
        code = request.form['code']
        errors, for_loop_tokens = analyze_code(code)
        token_count = count_tokens(code)
        if not errors:
            errors.append("El código es correcto.")
    return render_template('index.html', errors=errors, token_count=token_count, for_loop_tokens=for_loop_tokens)


if __name__ == '__main__':
    app.run(debug=True)