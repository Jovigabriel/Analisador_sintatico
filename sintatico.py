import ply.yacc as yacc
from lexico import tokens #Estou importando do nosso arquivo lexico.py a lista de tokens 

#REGRAS SINTATICAS DE COOL

def p_program(p):
    ''' program : lista_classes'''

    p[0] = ("PROGRAMA", p[1])


def p_lista_classes(p):
    '''lista_classes: lista_classes class
                    | class'''

    if len(p) == 2:
        p[0] =[ p[1] ]  #lista de p[1], é uma lista por conta da recursivadade que podemos ter nessa regra // lista de classes
    else:
        p[0]= p[1] + [p[2]]


def p_empty(p): #Para tratar situações em que podemos ter 0 ou mais coisas
    '''empty : '''
    pass

def p_class(p):
    '''class: CLASS TYPEID LBRACE feature_list RBRACE SEMI
            | CLASS TYPEID INHERITS TYPEID LBRACE feature_list RBRACE SEMI'''

    if len(p) == 7:
        p[0] = ("CLASSE", p[2], "SEM HERANÇA", p[4])
    else:
        p[0] = ("CLASSE", p[2], f"HERDA DE {p[4]}", p[6])


def p_feature_list(p):
    '''feature_list: feature_list feature
                    | empty'''

    if len(p) == 2:
        p[0] = [] #retorna lista vazia
    else:
        p[0] = p[1] + [p[2]] 


def p_feature(p):
    '''feature: OBJECTID LPAREN formal_list RPAREN COLON TYPEID LBRACE expr RBRACE SEMI
                | OBJECTID COLON TYPEID SEMI
                | OBJECTID COLON TYPEID ASSIGN expr SEMI'''

    if len(p) == 5:
        p[0] = (f"VARIAVEL: {p[1]}", f"TIPO: {p[3]}" )
    elif len(p) ==7:
        p[0] = (f"VARIAVEL: {p[1]}", f"TIPO: {p[3]}", f"VALOR ARMAZENADO {p[5]}" )
    else:
        p[0] = (f"FUNÇÃO: {p[1]}", f"LISTA DE PARAMETRO {p[3]}" , f"TIPO: {p[6]}", f"VALOR ARMAZENADO {p[8]}" )


def p_formal_list(p): 
    '''formal_list: formal
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
    '''expr: INT_CONST 
            | STR_CONST
            | OBJECTID
            | BOOL_CONST
            | NEW TYPEID
            | LPAREN expr RPAREN
            | NOT expr
            | ISVOID expr
            | expr PLUS expr
    '''
    if len(p) == 2:
        p[0] = ("VALOR", p[1])
    elif len(p) == 3:
        p[0] = ("OPERADOR", p[1], p[2])
    elif len(p)==4:
        if p[2] =='+':
            p[0] = ("SOMA", p[1], p[3])
        elif p[1] == '(':
            p[0] = p[2]
        