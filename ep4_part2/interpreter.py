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
		expr, reversable = self.expr()
		if not expr: return None, reversable

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
#  SYMBOL TABLE                     #
#####################################

class SymbolTable:
	def __init__(self):
		self.symbols = {}

	def add(self, name):
		self.symbols[name] = None

	def set(self, name, value):
		if name in self.symbols:
			self.symbols[name] = value

	def get(self, name):
		if name in self.symbols:
			return self.symbols[name]

#####################################
#  INTERPRETER                      #
#####################################

class Interpreter(object):
	def __init__(self):
		self.symbol_table = SymbolTable()

	def visit(self, node, *args, **kwargs):
		method_name = "visit" + type(node).__name__
		method = getattr(self, method_name, self.visit_generic)
		return method(node, *args, **kwargs)

	def visit_generic(self, node, *args, **kwargs):
		raise Exception('No visit{} method'.format(type(node).__name__))

	def visitProgramTree(self, tree):
		for node in tree.statements:
			self.visit(node)

	def visitFuncCallNode(self, node):
		if node.name.value.lower() == "print":
			print self.visit(node.argument)

	def visitStringNode(self, node):
		return node.tok.value

	def visitVariableDeclarationNode(self, node):
		self.symbol_table.add(node.name.value)
		self.symbol_table.set(node.name.value, self.visit(node.value))

	def visitVariableAccessNode(self, node):
		return self.symbol_table.get(node.name.value)

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