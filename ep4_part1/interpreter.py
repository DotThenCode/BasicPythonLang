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
EQ          =   'EQ'

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
			
			elif self.current_char == '=':
				tokens.append(Token(EQ, '='))
				self.advance()

		return tokens

	def string(self):
		string = ""
		self.advance()

		while self.current_char and self.current_char != '"':
			string += self.current_char
			self.advance()
		
		self.advance()
		return string

	def identifier(self):
		result = ""
		while self.current_char and self.current_char in LETTERS + DIGITS:
			result += self.current_char
			self.advance()

		return result

#####################################
#  NODES                            #
#####################################

class ProgramTree(object):
	def __init__(self, statements):
		self.statements = statements

class PrintNode(object):
	def __init__(self, node):
		self.node = node

class StringNode(object):
	def __init__(self, tok):
		self.tok = tok

class VariableDeclarationNode(object):
	def __init__(self, name, value):
		self.name = name
		self.value = value

class VariableAccessNode(object):
	def __init__(self, name):
		self.name = name

class FuncCallNode(object):
	def __init__(self, name, argument):
		self.name = name
		self.argument = argument

#####################################
#  PARSER                           #
#####################################

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.tok_index = 0

	def eat(self, tok_type, tok_value=None):
		tok = self.tokens[self.tok_index]
		if tok_value and tok.value != tok_value: return None
		if tok.type == tok_type:
			self.tok_index += 1
			return tok

	def reverse(self, count):
		self.tok_index -= count

	def parse(self):
		return self.program()

	#################################

	def program(self):
		return ProgramTree(self.statements())

	def statements(self):
		statements = []
		while self.tok_index < len(self.tokens):
			statements.append(self.statement())
		return statements

	def statement(self):
		node, reversable = self.variable_declaration()
		if node != None: return node
		self.reverse(reversable)
		return self.func_call()

	def variable_declaration(self):
		reversable = 0

		let = self.eat(IDENTIFIER, "LET")
		if not let: return None, reversable
		reversable += 1
		
		var_name = self.eat(IDENTIFIER)
		if not var_name: return None, reversable
		reversable += 1

		if not self.eat(EQ): return None, reversable
		reversable += 1

		expr, reversable_in = self.expr()
		reversable += reversable_in
		if not expr: return None, reversable

		return VariableDeclarationNode(var_name, expr), reversable

	def func_call(self):
		func_name = self.eat(IDENTIFIER)
		expr = self.expr()

		return FuncCallNode(func_name, expr)

	def expr(self):
		string = self.eat(STRING)

		if string == None:
			var_name = self.eat(IDENTIFIER)
			if not var_name: return None, 0
			return VariableAccessNode(var_name), 0
		else:
			return StringNode(string), 0

#####################################
#  INTERPRETER                      #
#####################################

class Interpreter(object):
	def visitProgramTree(self, tree):
		for node in tree.statements:
			if isinstance(node, PrintNode):
				self.visitPrintNode(node)

	def visitPrintNode(self, node):
		print node.node.tok.value

#####################################
#  MAIN                             #
#####################################

f = open("script.txt", "r")
data = f.read()
f.close()

lexer = Lexer(data)
tokens = lexer.make_tokens()
parser = Parser(tokens)
tree = parser.parse()
interpreter = Interpreter()
interpreter.visitProgramTree(tree)