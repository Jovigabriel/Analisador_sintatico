import ply.yacc as yacc
import sys
from lexico import tokens, lexer #Estamos importando do nosso arquivo lexico.py a lista de tokens e tambem o lexer que criamos

#yacc utiliza da tecnica de Shift reduce parsing: 

# Tabela de Precedência e Associatividade, é uma coisa do proprio ply.yacc, então precisa ter esse nome, o que tiver maior precedencia fica lá embaixo
#right significa que vamos começar a ler da direita para esquerda e left quer dizer que é da esqeurda para a direita, isso é para saber o que fazer quando tivermos um "empate", como por exemplo: 5-4-6.
#nonassoc significa que não podemos ter um empate de precedencia, ou seja, não podemos ter algo como: a<b<c. Ou seja não podemos ter mais de um comparador logico numa mesma expressão

precedence = (
    ('right', 'ASSIGN'  ),                 # Atribuição tem a menor prioridade
    ('nonassoc', 'LESS', 'LE', 'EQUAL' ), # Comparações não se misturam (ex: a < b < c é erro)
    ('left', 'PLUS', 'MINUS'),           # Soma e Subtração perdem para Multiplicação
    ('left', 'MULT', 'DIV'),             # Multiplicação e Divisão ganham da soma e subtração
    ('right', 'NOT', 'ISVOID', 'TILDE'), # Operadores unários têm a maior prioridade 
)


#REGRAS SINTATICAS DE COOL:

#Assim como no nosso arquivo automatizado do lexico, vamos usar o ply.yacc para automatizar o nosso sintatico, então, teremos que seguir alguns padrões de nomes, como é o caso dos metodos que terão que começar sempre com a letra p, p_nomeFunçao()

#Na maioria das funções aqui recebemos como parametro a letra p, que é um vetor/lista que o yacc usa para armazenas as "palavras" que formaram a "frase" que bateu com a DOCSTRING da função chamada, então usando de exemplo a docstring de soma: "expr: expr PLUS expr" o p[1] = expr (primeiro expr após os dois pontos, NO CASO O VALOR LITERAL) p[2] = PLUS (no caso, o sinal de +) e o p[3] = expr (o ultimo expr). O p[0] tem uma função diferente, porque ele representa o que vem antes dos dois pontos, ou seja, é o que vai ser retornado para o YACC, basicamente em cada função, nós temos que dizer o que o p[0] vai receber para o yacc montar a arvore usando isso, no exemplo da soma o p[0] vai retornar (SOMA, num1, num2), usamos o P[0] para guardar o que realmente importa para o nosso compilador, o que não for necessario, nós não usamos, como é o caso de ponto e virgula, parenteses e afins


#Um programa em cool é formado por uma lista de classes
def p_program(p):
    ''' program : class_list'''

    p[0] = ("PROGRAMA", p[1]) 

def p_empty(p): #Para tratar situações em que temos espaços em branco e evitar que seja erro sintatico, não retorna nada
    '''empty : '''
    pass

#Definição do que é uma lista de classes, no caso, são uma sequencia de uma ou mais classes
def p_class_list(p):
    '''class_list : class_list class
                    | class'''

    if len(p) == 2:
        p[0] =[ p[1] ]  # lista de p[1], é uma lista por conta da recursivadade que podemos ter nessa regra, no caso, uma lista de classes
    else:
        p[0]= p[1] + [p[2]] #p[1] já é uma lista, mas p[2] temos que fazer ser


#Definindo uma classe segundo a definição do manual de cool, temos duas formas diferentes porque pode ser que tenhamos inherits ou nao

def p_class(p):
    '''class : CLASS TYPEID LBRACE feature_list RBRACE SEMI
            | CLASS TYPEID INHERITS TYPEID LBRACE feature_list RBRACE SEMI'''

    if len(p) == 7:
        p[0] = ("CLASSE", p[2], ("SEM HERANÇA",), ("FEATURES", p[4]))
    else:
        p[0] = ("CLASSE", p[2], ("HERDA DE", p[4]), ("FEATURES", p[6]))



#FUNÇÕES PARA LIDAR COM expr

#Para ficar melhor de se ler, dividimos cada regra de expr em uma função diferente, quando fizemos tudo junto ficou muito grande

#Tipos bases, como int, string, bool

def p_expr_inteiro(p):
    '''expr : INT_CONST'''
    p[0] = ("INTEIRO", p[1])

def p_expr_string(p):
    '''expr : STR_CONST'''
    p[0] = ("STRING", p[1])

def p_expr_bool(p):
    '''expr : BOOL_CONST'''
    p[0] = ("BOOLEANO", p[1])

def p_expr_objeto(p):
    '''expr : OBJECTID'''
    p[0] = ("VARIAVEL", p[1])

def p_expr_new(p):
    '''expr : NEW TYPEID'''
    p[0] = ("NEW", p[2])

def p_expr_parenteses(p):
    '''expr : LPAREN expr RPAREN'''
    p[0] = p[2]  #Só envio a expr

def p_expr_bloco(p):
    '''expr : LBRACE expr_list RBRACE'''
    p[0] = ("BLOCO", p[2])

# Operadores unários

def p_expr_not(p):
    '''expr : NOT expr'''
    p[0] = ("NÃO LÓGICO", p[2])

def p_expr_tilde(p):
    '''expr : TILDE expr'''
    p[0] = ("NEGAÇÃO NUMÉRICA", p[2])

def p_expr_isvoid(p):
    '''expr : ISVOID expr'''
    p[0] = ("ISVOID", p[2])

# Operadores aritméticos

def p_expr_soma(p):
    '''expr : expr PLUS expr'''
    p[0] = ("SOMA", p[1], p[3])

def p_expr_subtracao(p):
    '''expr : expr MINUS expr'''
    p[0] = ("SUBTRAÇÃO", p[1], p[3])

def p_expr_multiplicacao(p):
    '''expr : expr MULT expr'''
    p[0] = ("MULTIPLICAÇÃO", p[1], p[3])

def p_expr_divisao(p):
    '''expr : expr DIV expr'''
    p[0] = ("DIVISÃO", p[1], p[3])

# Operadores de comparação 

def p_expr_menor(p):
    '''expr : expr LESS expr'''
    p[0] = ("MENOR QUE", p[1], p[3])

def p_expr_igual(p):
    '''expr : expr EQUAL expr'''
    p[0] = ("IGUAL", p[1], p[3])

def p_expr_menor_igual(p):
    '''expr : expr LE expr'''
    p[0] = ("MENOR OU IGUAL", p[1], p[3])

# Atribuição

def p_expr_atribuicao(p):
    '''expr : OBJECTID ASSIGN expr'''
    p[0] = ("ATRIBUIÇÃO", p[1], p[3])

# Estruturas de controle 

def p_expr_if(p):
    '''expr : IF expr THEN expr ELSE expr FI'''
    p[0] = ("IF", ("CONDIÇÃO", p[2]), ("VERDADE", p[4]), ("ELSE", p[6]))

def p_expr_while(p):
    '''expr : WHILE expr LOOP expr POOL'''
    p[0] = ("WHILE", ("CONDIÇÃO", p[2]), ("CORPO", p[4]))

def p_expr_case(p): # PODEMOS TER UMA LISTA DE CASE, ENTÇAO CRIAMOS UMA CASE_LIST
    '''expr : CASE expr OF case_list ESAC'''
    p[0] = ("CASE", ("EXPRESSÃO", p[2]), ("CASOS", p[4]))

def p_expr_let(p): # cOMO PODEMOS TER VARIAS VARIAVIES SENDO INICIALIZADAS, CRIAMOS UMA LISTA
    '''expr : LET let_list IN expr'''
    p[0] = ("LET", ("VARIÁVEIS", p[2]), ("CORPO", p[4]))

#  Chamadas de método 

def p_expr_chamada_simples(p): #aCTUAL_LIST É A LISTA DE PARAMETROS QUE PODEM OU NÃO SER PASSADOS
    '''expr : OBJECTID LPAREN actual_list RPAREN'''
    p[0] = ("CHAMADA DE FUNÇÃO", ("NOME", p[1]), ("PARÂMETROS", p[3]))


def p_expr_chamada_metodo(p):
    '''expr : expr DOT OBJECTID LPAREN actual_list RPAREN'''
    p[0] = ("CHAMADA DE MÉTODO", ("OBJETO", p[1]), ("MÉTODO", p[3]), ("PARÂMETROS", p[5]))

def p_expr_chamada_estatica(p):
    '''expr : expr AT TYPEID DOT OBJECTID LPAREN actual_list RPAREN'''
    p[0] = ("CHAMADA ESTÁTICA", ("OBJETO", p[1]), ("CLASSE MÃE", p[3]), ("MÉTODO", p[5]), ("PARÂMETROS", p[7]))



#FUNÇÕES _LIST, QUE SÃO USADAS QUANDO PODEMOS TER 1 OU MAIS ELEMENTOS DE UM TIPO E OUTRAS FUNÇÕES QUE SÃO CHAMADAS APÓS ESSAS _LIST:


def p_feature_list(p): #Essa função serve para possibilitar que tenhamos 0 ou mais features sendo validadas em regras como p_class que aceitam 0 ou mais features
    '''feature_list : feature_list feature
                    | empty'''

    if len(p) == 2:
        p[0] = [] #retorna lista vazia
    else:
        p[0] = p[1] + [p[2]] 


def p_feature(p): #Definição de Feature segundo o manual
    '''feature : OBJECTID LPAREN formal_list RPAREN COLON TYPEID LBRACE expr RBRACE SEMI
               | OBJECTID COLON TYPEID SEMI
               | OBJECTID COLON TYPEID ASSIGN expr SEMI'''

    if len(p) == 5:
        p[0] = ("VARIAVEL", p[1], ("TIPO", p[3]))

    elif len(p) == 7:
        p[0] = ("VARIAVEL", p[1], ("TIPO", p[3]), ("VALOR", p[5]))

    else:
        p[0] = ("FUNÇÃO", p[1], ("PARAMETROS", p[3]), ("TIPO", p[6]), ("CORPO", p[8]))


def p_formal_list(p):  #Definição de formal list, que é uma lista de parametros formais que são as variaveis que colocamos dentro do parenteses quando declaramos uma função
    '''formal_list : formal
                    | formal_list COMMA formal
                    | empty
    '''
    if len(p) ==2:
        if p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_formal(p):
    '''formal : OBJECTID COLON TYPEID'''
    p[0] = ("PARAMETRO", p[1], ("TIPO", p[3]))



def p_expr_list(p): #lista de expressoes

    '''expr_list : expr_list expr SEMI  
                | expr SEMI         
    '''
    if len(p) == 3:
        p[0] = [p[1]]
    else: 
        p[0] = p[1] + [p[2]]

#Usamos o nome actual pois em algumas fontes que lemos eles dizem que quando fazemos a chamada de um metodo, você passa os actual arguments, então é a lista de actual arguments, os argumentos reais

def p_actual_list(p): #Podemos ter ou não parametros, então essa função serve para verificar se a função vai ter ou não parametros, SE TIVER, vamos chamar realmente a função com a lista de parametros
    '''actual_list : lista_argumentos
                   | empty'''

    if len(p) == 2:
        if p[1] == None:
            p[0] = []
        else:
            p[0] = p[1]


def p_lista_argumentos(p): #lista de argumentos
    '''lista_argumentos : lista_argumentos COMMA expr
                        | expr'''

    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


# lISTA COM TODOS OS CASES
def p_case_list(p):
    '''case_list : case_list case_branch
                 | case_branch'''

    if len(p) == 2:
        p[0] = [ p[1] ]
    else:
        p[0] = p[1] + [ p[2] ]


# uM ÚNICO CASE SENDO FORMADO para ir para a lista de cases
def p_case_branch(p):
    '''case_branch : OBJECTID COLON TYPEID DARROW expr SEMI'''
    p[0] = ("RAMO CASE", ("NOME", p[1]), ("TIPO", p[3]), ("EXECUTA", p[5]))


#A lista de variáveis separadas por vírgula
def p_let_list(p):
    '''let_list : let_list COMMA let_decl
                | let_decl'''
            
    if len(p) == 2:
        p[0] = [ p[1] ]
    else:
        p[0] = p[1] + [ p[3] ]


# A declaração individual da variável (Pode ter valor inicial ou não)
def p_let_decl(p):
    '''let_decl : OBJECTID COLON TYPEID
                | OBJECTID COLON TYPEID ASSIGN expr'''

    if len(p) == 4:
        p[0] = ("DECLARAÇÃO LET", ("NOME", p[1]), ("TIPO", p[3]))
    else:
        p[0] = ("DECLARAÇÃO LET", ("NOME", p[1]), ("TIPO", p[3]), ("VALOR", p[5]))


#TRATANDO ERRO SINTATICO

# Função obrigatória do PLY para tratar erros de sintaxe (quando o código COOL está errado)
def p_error(p):
    if p:
        print(f"\n[ERRO SINTÁTICO] Token inesperado '{p.value}' (Linha: {p.lineno})") 
    else:
        print("\n[ERRO SINTÁTICO] Fim de arquivo inesperado") # O arquivo terminou, mas o codigo não foi concluido corretamente, ficou em aberto
    sys.exit(1) # encerra programa


# Constrói o analisador sintático
parser = yacc.yacc()

#FUNÇÃO PARA IMPRIMIR ARVORE
def imprimir_arvore(no, prefixo="", eh_ultimo=True):
    if no is None:
        return

    conector = "└── " if eh_ultimo else "├── "

    if isinstance(no, tuple):
        print(prefixo + conector + str(no[0]))
        novo_prefixo = prefixo + ("    " if eh_ultimo else "│   ")
        filhos = [f for f in no[1:] if f is not None]
        for i, filho in enumerate(filhos):
            imprimir_arvore(filho, novo_prefixo, i == len(filhos) - 1)

    elif isinstance(no, list):
        print(prefixo + conector + "[lista]")
        novo_prefixo = prefixo + ("    " if eh_ultimo else "│   ")
        for i, item in enumerate(no):
            imprimir_arvore(item, novo_prefixo, i == len(no) - 1)

    else:
        print(prefixo + conector + repr(no))




if __name__ == '__main__':
    #  Verifica se o usuário passou o nome do arquivo no terminal
    if len(sys.argv) < 2:
        print("Uso correto: python sintatico.py <arquivo.cl>")
        sys.exit(1)

    # Pega o nome do arquivo 
    nome_arquivo = sys.argv[1]

    if not nome_arquivo.endswith('.cl'):
            print(f'ERRO: Arquivo recebido não é do tipo .cl')
            sys.exit(1)

    # Tenta abrir e ler o arquivo
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
            codigo_cool = arquivo.read()
    except FileNotFoundError:
        print(f"[ERRO] O arquivo '{nome_arquivo}' não foi encontrado.")
        sys.exit(1)
        
    print(f"Iniciando Análise Sintática do arquivo: {nome_arquivo}...\n")
    
    # Passa o texto do arquivo para o parser
    arvore_sintatica = parser.parse(codigo_cool, lexer=lexer.clone()) #Estamos passando o lexer que criamos como parametro tambem
    
 
    if arvore_sintatica:
        print("\n--- ÁRVORE SINTÁTICA (VISUAL) ---")
        imprimir_arvore(arvore_sintatica)