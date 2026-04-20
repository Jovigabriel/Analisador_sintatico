import ply.yacc as yacc
from lexico import tokens, lexer #Estamos importando do nosso arquivo lexico.py a lista de tokens 

# Tabela de Precedência e Associatividade, é uma coisa do proprio ply.yacc, então precisa ter esse nome, o que tiver maior precedencia fica lá embaixo
precedence = (
    ('right', 'ASSIGN'),                 # Atribuição tem a menor prioridade
    ('nonassoc', 'LESS', 'LE', 'EQUAL'), # Comparações não se misturam (ex: a < b < c é erro)
    ('left', 'PLUS', 'MINUS'),           # Soma e Subtração perdem para Multiplicação
    ('left', 'MULT', 'DIV'),             # Multiplicação e Divisão ganham da soma e subtração
    ('right', 'NOT', 'ISVOID', 'TILDE'),          # Operadores unários têm a maior prioridade 
)

#right significa que vamos começar a ler da direita para esquerda e left quer dizer que é da esqeurda para a direita, isso é para saber o que fazer quando tivermos um "empate", como por exemplo: 5-4-6.
#nonassoc significa que não podemos ter um empate de precedencia, ou seja, não podemos ter algo como: a<b<c. Ou seja não podemos ter mais de um comparador logico numa mesma expressão

#REGRAS SINTATICAS DE COOL

def p_program(p):
    ''' program : lista_classes'''

    p[0] = ("PROGRAMA", p[1])


def p_lista_classes(p):
    '''lista_classes : lista_classes class
                    | class'''

    if len(p) == 2:
        p[0] =[ p[1] ]  #lista de p[1], é uma lista por conta da recursivadade que podemos ter nessa regra // lista de classes
    else:
        p[0]= p[1] + [p[2]]


def p_empty(p): #Para tratar situações em que podemos ter 0 ou mais coisas
    '''empty : '''
    pass

def p_class(p):
    '''class : CLASS TYPEID LBRACE feature_list RBRACE SEMI
            | CLASS TYPEID INHERITS TYPEID LBRACE feature_list RBRACE SEMI'''

    if len(p) == 7:
        p[0] = ("CLASSE", p[2], "SEM HERANÇA", p[4])
    else:
        p[0] = ("CLASSE", p[2], f"HERDA DE {p[4]}", p[6])


def p_feature_list(p):
    '''feature_list : feature_list feature
                    | empty'''

    if len(p) == 2:
        p[0] = [] #retorna lista vazia
    else:
        p[0] = p[1] + [p[2]] 


def p_feature(p):
    '''feature : OBJECTID LPAREN formal_list RPAREN COLON TYPEID LBRACE expr RBRACE SEMI
                | OBJECTID COLON TYPEID SEMI
                | OBJECTID COLON TYPEID ASSIGN expr SEMI'''

    if len(p) == 5:
        p[0] = (f"VARIAVEL: {p[1]}", f"TIPO: {p[3]}" )
    elif len(p) ==7:
        p[0] = (f"VARIAVEL: {p[1]}", f"TIPO: {p[3]}", f"VALOR ARMAZENADO {p[5]}" )
    else:
        p[0] = (f"FUNÇÃO: {p[1]}", f"LISTA DE PARAMETRO {p[3]}" , f"TIPO: {p[6]}", f"VALOR ARMAZENADO {p[8]}" )


def p_formal_list(p): 
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
    p[0] = ("PARAMETRO", p[1], p[3])


def p_expr(p):
    '''expr : INT_CONST 
            | STR_CONST
            | OBJECTID
            | BOOL_CONST
            | NEW TYPEID
            | TILDE expr
            | LPAREN expr RPAREN
            | NOT expr
            | ISVOID expr
            | expr PLUS expr
            | expr MINUS expr
            | expr MULT expr
            | expr DIV expr
            | expr LESS expr
            | expr EQUAL expr
            | expr LE expr
            | OBJECTID ASSIGN expr
            | IF expr THEN expr ELSE expr FI
            | WHILE expr LOOP expr POOL
            | LBRACE expr_list RBRACE
            | OBJECTID LPAREN actual_list RPAREN
            | expr AT TYPEID DOT OBJECTID LPAREN actual_list RPAREN
            | expr DOT OBJECTID LPAREN actual_list RPAREN
            | CASE expr OF case_list ESAC
            | LET let_list IN expr
    '''
    if len(p) == 2:
        p[0] = ("VALOR", p[1])

    elif len(p) == 3:
        if p[1] == '~':
            p[0] = ("NEGAÇÃO NUMÉRICA", p[2])
        elif p[1] == 'not':
            p[0] = ("NÃO LÓGICO", p[2])
        elif p[1] == 'isvoid':
            p[0] = ("ISVOID", p[2])
        elif p[1] == 'new':
            p[0] = ("NEW", p[2])

    elif len(p) == 4:
        if p[2] =='+':
            p[0] = ("SOMA", p[1], p[3])

        elif p[2] =='-':
            p[0] = ("SUBTRAÇÃO", p[1], p[3])

        elif p[2] =='*':
            p[0] = ("MULTIPLICAÇÃO", p[1], p[3])

        elif p[2] =='/':
            p[0] = ("DIVISÃO", p[1], p[3])

        elif p[2] =='<':
            p[0] = ("MENOR QUE", p[1], p[3])

        elif p[2] =='=':
            p[0] = ("IGUAL", p[1], p[3])

        elif p[2] =='<=':
            p[0] = ("MENOR OU IGUAL", p[1], p[3])

        elif p[2] =='<-':
            p[0] = ("VARIAVEL RECEBE", p[1], p[3])

        elif p[1] == '(':
            p[0] = p[2]
        
        elif p[1] == '{':
            p[0] = ("BLOCO", p[2])

    elif len(p) == 5:
        if p[1] == 'let':
            p[0] = ("CRIAÇÃO DE VARIAVEL", f"LISTA DE VARIAVEIS: {p[2]}", f"CORPO DO LET: {p[4]}" )
        else:
            p[0] = ("CHAMADA DE FUNÇÃO", f"NOME: {p[1]}", f"PARAMETROS: {p[3]}" )


    elif len(p) == 6:
        if p[1] == 'while':
            p[0] = ("WHILE", f"Condição: {p[2]}", f"Bloco: {p[4]}")
        elif p[1] == 'case':
            p[0] =  ("CASE", f"Expressão testada: {p[2]}", f"Lista de Cases {p[4]}")
        
    elif len(p) == 7:
        if p[2] =='.':
            p[0] = ("CHAMADA DE FUNÇÃO", f"NOME OBJETO: {p[1]}", f"NOME FUNÇÃO {p[3]}", f"PARAMETROS: {p[5]}")


    elif len(p) == 8:
        if p[1] == "if":
            p[0] = ("IF", f"Condição: {p[2]}", f"Bloco verdade: {p[4]}", f"Bloco Else: {p[6]}")

    elif len(p) == 9:
        p[0] = ("CHAMADA DE FUNÇÃO", f"NOME OBJETO: {p[1]}", f"NOME CLASSE MÃE: {p[3]}", f"NOME FUNÇÃO {p[5]}", f"PARAMETROS: {p[7]}" )

def p_expr_list(p):

    '''expr_list : expr_list expr SEMI  
                | expr SEMI         
    '''
    if len(p) == 3:
        p[0] = [p[1]]
    else: 
        p[0] = p[1] + [p[2]]


def p_lista_argumentos(p):
    '''lista_argumentos : lista_argumentos COMMA expr
                        | expr'''

    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_actual_list(p):
    '''actual_list : lista_argumentos
                   | empty'''

    if len(p) == 2:
        if p[1] == None:
            p[0] = []
        else:
            p[0] = p[1]

# linha individual do Case 
def p_case_branch(p):
    '''case_branch : OBJECTID COLON TYPEID DARROW expr SEMI'''
    
    p[0] = ("RAMO_CASE", f"Nome: {p[1]}", f"Tipo: {p[3]}", f"Executa: {p[5]}")

# Juntando todos os cases
def p_case_list(p):
    '''case_list : case_list case_branch
                 | case_branch'''

    if len(p) == 2:
        p[0] = [ p[1] ]
    else:
        p[0] = p[1] + [ p[2] ]

# A declaração individual da variável (Pode ter valor inicial ou não)
def p_let_decl(p):
    '''let_decl : OBJECTID COLON TYPEID
                | OBJECTID COLON TYPEID ASSIGN expr'''
                
    if len(p) == 4:
        p[0] = ("DECLARACAO_LET", f"Nome: {p[1]}", f"Tipo: {p[3]}")
    else:
        p[0] = ("DECLARACAO_LET_COMPLETA", f"Nome: {p[1]}", f"Tipo: {p[3]}", f"Valor: {p[5]}")

#A lista de variáveis separadas por vírgula
def p_let_list(p):
    '''let_list : let_list COMMA let_decl
                | let_decl'''
            
    if len(p) == 2:
        p[0] = [ p[1] ]
    else:
        p[0] = p[1] + [ p[3] ]

# --- MOTOR DO COMPILADOR E TESTE ---

# Função obrigatória do PLY para tratar erros de sintaxe (quando o código COOL está errado)
def p_error(p):
    if p:
        print(f"\n[ERRO SINTÁTICO] Código fora do padrão próximo a '{p.value}' (Linha: {p.lineno})")
    else:
        print("\n[ERRO SINTÁTICO] Fim de arquivo inesperado")

# Constrói o analisador sintático
parser = yacc.yacc()


def imprimir_arvore(no, nivel=0):
        # Cria o recuo com base no nível de profundidade
        espaco = "    " * nivel
        
        # Se for uma Tupla (Ex: um nó com Regra e Filhos)
        if isinstance(no, tuple):
            print(f"{espaco} # {no[0]}") # Imprime o nome da regra (ex: CLASSE, IF, SOMA)
            for filho in no[1:]:
                imprimir_arvore(filho, nivel + 1) # Entra nos filhos
                
        # Se for uma Lista (Ex: lista de parâmetros ou expr_list)
        elif isinstance(no, list):
            for item in no:
                imprimir_arvore(item, nivel)
                
        # Se for um valor final (Uma string ou número)
        else:
            print(f"{espaco} └─ {no}")


import sys

# ... (Deixe a sua função imprimir_arvore(no, nivel=0) aqui, logo acima do if) ...

if __name__ == '__main__':
    # 1. Verifica se o usuário passou o nome do arquivo no terminal
    if len(sys.argv) < 2:
        print("Uso correto: python sintatico.py <arquivo.cl>")
        sys.exit(1)

    # 2. Pega o nome do arquivo (é o segundo item da lista do terminal)
    nome_arquivo = sys.argv[1]

    # 3. Tenta abrir e ler o arquivo
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
            codigo_cool = arquivo.read()
    except FileNotFoundError:
        print(f"[ERRO] O arquivo '{nome_arquivo}' não foi encontrado.")
        sys.exit(1)
        
    print(f"Iniciando Análise Sintática do arquivo: {nome_arquivo}...\n")
    
    # 4. Passa o texto do arquivo para o parser!
    arvore_sintatica = parser.parse(codigo_cool, lexer=lexer.clone())
    
    # 5. Se a árvore foi gerada com sucesso (sem erros de sintaxe), imprime bonito
    if arvore_sintatica:
        print("\n--- ÁRVORE SINTÁTICA (VISUAL) ---")
        imprimir_arvore(arvore_sintatica)