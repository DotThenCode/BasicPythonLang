#####################################
#  IMPORTS                          #
#####################################

import string

#####################################
#  CONSTANTS                        #
#####################################

LETTERS = string.ascii_letters
DIGITS 	= '0123456789'

#####################################
#  TOKENS                           #
#####################################

IDENTIFIER  =   'IDENTIFIER'
STRING      =   'STRING'

class Token(object):
    def __init__(self, typ, val=""):
        self.type = typ
        self.value = val

#####################################
#  LEXER                            #
#####################################

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def make_tokens(self):
        tokens = []
        
        while self.current_char is not None:
        	if self.current_char.isspace():
        		self.advance()
        		continue

        	elif self.current_char == '"':
        		tokens.append(Token(STRING, self.string()))

        	elif self.current_char in LETTERS:
        		tokens.append(Token(IDENTIFIER, self.identifier()))

        return tokens

    def string(self):
        string = ""
        self.advance()

        while self.current_char != '"':
            string += self.current_char
            self.advance()
        
        self.advance()
        return string

    def identifier(self):
        result = ""

        while self.current_char in LETTERS + DIGITS:
            result += self.current_char
            self.advance()

        return result

#####################################
#  PARSER                           #
#####################################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_index = 0

    def eat(self, tok_type):
        tok = self.tokens[self.tok_index]
        if tok.type == tok_type:
            self.tok_index += 1
            return tok

    def parse(self):
        self.program()

    #################################

    def program(self):
        self.statements()

    def statements(self):
        while self.tok_index < len(self.tokens):
            func_tok = self.eat(IDENTIFIER)
            if func_tok.value.upper() == "PRINT":
                string = self.eat(STRING)
                print string.value

#####################################
#  MAIN                             #
#####################################

f = open("script.txt", "r")
data = f.read()
f.close()

lexer = Lexer(data)
tokens = lexer.make_tokens()
parser = Parser(tokens)
parser.parse()