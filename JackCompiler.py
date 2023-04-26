import regex as re
import sys
import os
import glob


class JackTokenizer():
        
    global symbols, keywords
    symbols = r"{}()[].;+-*/&|,<>=~"
    keywords = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"]
    

    def init(file):  # Open jack file for parsing
    
        #Initialization
        outName = file.split(".")[0]  # Get file name without extension, for output file
        outName += "T.xml"
    
        content = ""
        pattern = r"^(.*?)(?=\/\/|\/\*\*|$)"
        switch = False
            
        with open(file) as f:
            for line in f:
                
                if line[:3] == "/**":
                    switch = True
                    pass
                elif line[:2] == "*/":
                    switch = False
                elif switch:
                    pass
                    
                match = re.search(pattern, line)  # Get every instruction, and put in content
                match = match.group().strip()
                if match:
                    content += match
                        
        return content, outName

    
    @staticmethod
    def advance(line):
        
        next_token = ""
        
        # Cut any white space at beginning
        line = line.strip()
                
        # If first character is symbol, simply return this
        if line[0] in symbols:
            return line[0]
        
        # If this is start of string, get rest of string. Need quotes to get tokenType
        elif line[0] == '"':  
            i = 1
            next_token += '"'
            while line[i] != '"':
                next_token += line[i]
                i += 1
            next_token += '"'
            return next_token
        
        # If start is digit, then rest of token is digit
        elif line[0].isdigit():
            i = 0
            while line[i].isdigit():
                next_token += line[i]
                i += 1
            
            return next_token
                

        # OTHERWISE, we have either keyword or identifier
        for j, char in enumerate(line):
            next_token += char
            
            if next_token in keywords and (line[j + 1] == " " or line[j + 1] == ";"):  # String will be keyword 
                return next_token
            elif (line[j + 1] in symbols) or (line[j + 1] == " "):
                return next_token
                
    
    @staticmethod
    def tokenType(token):
        
        token = token.lower()

        # Determine token type and return
        if token.isdigit():
            return "INT_CONST"
        elif token in symbols:
            return "SYMBOL"
        elif token in keywords:
            return "KEYWORD"
        elif token[0] == "\"":
            return "STRING_CONST"
        else:
            return "IDENTIFIER"
        
    @staticmethod
    def intVal(token):
        return f"<integerConstant> {token} </integerConstant>\n" 

    @staticmethod
    def symbol(token):          
        if token == "<":
            token = "&lt;"
        elif token == ">":
            token ="&gt;"
        elif token == '"':
            token = "&quot;"
        elif token == "&":
            token = "&amp;"
            
        return f"<symbol> {token} </symbol>\n" 
        
    @staticmethod
    def keyWord(token):
        return f"<keyword> {token} </keyword>\n"
    
    @staticmethod
    def stringVal(token):
        return f"<stringConstant> {token} </stringConstant>\n"
    
    @staticmethod
    def identifier(token):
        return f"<identifier> {token} </identifier>\n"
    
    @staticmethod
    def write_term(token, tokenType):
        
        if tokenType == "INT_CONST":
            return f"{JackTokenizer.intVal(token)}"
        elif tokenType == "SYMBOL":
            return f"{JackTokenizer.symbol(token)}"
        elif tokenType == "KEYWORD":
            return f"{JackTokenizer.keyWord(token)}"
        elif tokenType == "STRING_CONST":
            return f"{JackTokenizer.stringVal(token)}"
        elif tokenType == "IDENTIFIER":
            return f"{JackTokenizer.identifier(token)}"
                        
    
    
class CompilationEngine():
    
    global op  # Operators to be used by compileExpression
    op = ["+", "-", "=", ">", "<", "*", "/", "|"]
    global statements
    statements = ["if", "while", "do", "let", "return"]
    
    
    def __init__(self):
        return
    
    def compileClass():  # 'class' className'{' classVarDec* subroutineDec* '}'
        global current
        
        result = "<class>\n"
        
        token = JackTokenizer.advance(current)  # class
        print(f"class var: {token}")
        current = current[len(token):].strip()
        result += JackTokenizer.write_term(token, "KEYWORD")
        
        token = JackTokenizer.advance(current)  # className
        print(f"className: {token}")
        current = current[len(token):].strip()
        result += JackTokenizer.write_term(token, "IDENTIFIER")  
        
        token = JackTokenizer.advance(current)
        current = current[len(token):].strip()
        
        if token == "{":  # Ensure next token is '{'
            print('ADDING {')
            result += "<symbol> { </symbol>\n"
        
        token = JackTokenizer.advance(current)  # Start of classVarDec
        print(token)
        
        while token == "static" or token == "field":
            result += CompilationEngine.compileClassVarDec()
            token = JackTokenizer.advance(current)
        print(f"current after classVarDec: {current}")
        
        while token == "constructor" or token == "function" or token == "method":  # Start of subroutineDec
            result += CompilationEngine.compileSubroutineDec()
            token = JackTokenizer.advance(current)
        print(f"current after subroutineDec: {current}")
        
        if token == "}":  # Ensure next token is '}'
            result += "<symbol> } </symbol>\n"
            
        current = current[len(token):].strip()
        
        result += "</class>\n"
            
        return result
    
    def compileClassVarDec():  # ('static'|'field') type varName (',' varName)* ';'
        global current
        
        result = "<classVarDec>\n"
        
        token = JackTokenizer.advance(current)  # static or field
        print(token)
        current = current[len(token):].strip()
        result += JackTokenizer.write_term(token, "KEYWORD")
        
        token = JackTokenizer.advance(current)  # type
        print(f"type:{token}")
        current = current[len(token):].strip()
        tokenType = JackTokenizer.tokenType(token)
        print(tokenType)
        result += JackTokenizer.write_term(token, tokenType)
        
        token = JackTokenizer.advance(current)  # varName
        print(f"varName:{token}")
        current = current[len(token):].strip()
        result += JackTokenizer.write_term(token, "IDENTIFIER")
        
        token = JackTokenizer.advance(current)
        
        while token == ",":  # Check for any other variables
            current = current[len(token):].strip()
            result += JackTokenizer.write_term(token, "SYMBOL")
            token = JackTokenizer.advance(current)  # varName
            current = current[len(token):].strip()
            result += JackTokenizer.write_term(token, "IDENTIFIER")
            token = JackTokenizer.advance(current)
            
        result += JackTokenizer.write_term(token, "SYMBOL")  # ;
        print("ADDING ;")
        current = current[len(token):].strip()
            
        result += "</classVarDec>\n"
        
        return result
    
    def compileSubroutineDec():  # ('constructor'|'function'|'method') ('void'| type) subroutineName '(' parameterList ')' subroutineBody
        global current
        
        result = "<subroutineDec>\n"

        token = JackTokenizer.advance(current)  # constructor or function or method
        current = current[len(token):].strip()
        if token == "constructor" or token == "function" or token == "method":
            print(f"constructor or function or method: {token}")
            result += JackTokenizer.write_term(token, "KEYWORD")
            
        token = JackTokenizer.advance(current)  # void or type
        print(f"void or type: {token}")
        current = current[len(token):].strip()
        tokenType = JackTokenizer.tokenType(token)
        if tokenType == "KEYWORD" or tokenType == "IDENTIFIER":
            result += JackTokenizer.write_term(token, tokenType)
        
        token = JackTokenizer.advance(current)  # subroutineName
        print(f"subroutineName: {token}")
        current = current[len(token):].strip()
        result += JackTokenizer.write_term(token, "IDENTIFIER")
        
        token = JackTokenizer.advance(current)
        current = current[len(token):].strip()
        if token == "(":  # Ensure next token is '('
            print("ADDING (")
            result += "<symbol> ( </symbol>\n"
        
        result += CompilationEngine.compileParameterList()
        
        token = JackTokenizer.advance(current)
        current = current[len(token):].strip()
        if token == ")":  # Ensure next token is ')'
            print("ADDING )")
            result += "<symbol> ) </symbol>\n"
            
        result += CompilationEngine.compileSubroutineBody()
        
        result += "</subroutineDec>\n"
        
        return result
    
    def compileParameterList():  # (type varName, (',' type varName)*)?
        global current
        
        result = "<parameterList>\n"

        token = JackTokenizer.advance(current)  # Either type or )
        
        if token != ")":  # If are no args, then we are done
        
            current = current[len(token):].strip()
            tokenType = JackTokenizer.tokenType(token)
            result += JackTokenizer.write_term(token, tokenType)
            
            token = JackTokenizer.advance(current)  # varName
            current = current[len(token):].strip()
            result += JackTokenizer.write_term(token, "IDENTIFIER")
            
            token = JackTokenizer.advance(current)  # If another arg, it will be ",""
            
            # Check if we have another arg. If so, add it
            while token == ",":
            
                result += JackTokenizer.write_term(token, "SYMBOL")
                current = current[len(token):].strip()
                
                token = JackTokenizer.advance(current)  # type
                tokenType = JackTokenizer.tokenType(token)
                result += JackTokenizer.write_term(token, tokenType)
                
                token = JackTokenizer.advance(current)  # varName
                current = current[len(token):].strip()
                result += JackTokenizer.write_term(token, "IDENTIFIER")
                
                token = JackTokenizer.advance(current)
        
        result += "</parameterList>\n"
        
        return result
        
    def compileSubroutineBody():  # '{' varDec* statements '}'
        global current
        
        result = "<subroutineBody>\n"
        
        token = JackTokenizer.advance(current)  # {
        current = current[len(token):].strip()
        if token == "{":
            print("adding {")
            result += "<symbol> { </symbol>\n"
        
        token = JackTokenizer.advance(current)  # var
        while token == "var":  # For all variables
            result += CompilationEngine.compileVarDec()
            token = JackTokenizer.advance(current)
        print(f"completed varDec, current: {current}")
        
        # Add every statement, checking for errors
        if (token == "let" or token == "if" or token == "while" or token == "do" or token == "return"):
            result += CompilationEngine.compileStatements()
            
        token = JackTokenizer.advance(current)  # }
        current = current[len(token):].strip()
        if token == "}":
            print("adding }")
            result += "<symbol> } </symbol>\n"
        
        result += "</subroutineBody>\n"
        
        return result
    
    def compileVarDec():  # 'var' type varName (',' varName)*';'
        global current
        
        result = "<varDec>\n"
        
        token = JackTokenizer.advance(current)  # var
        print(token)
        current = current[len(token):].strip()
        result += JackTokenizer.write_term(token, "KEYWORD")
        
        token = JackTokenizer.advance(current)  # type
        print(f"type: {token}")
        tokenType = JackTokenizer.tokenType(token)
        current = current[len(token):].strip()
        result += JackTokenizer.write_term(token, tokenType)
        
        token = JackTokenizer.advance(current)  # varName
        print(f"varName: {token}")
        current = current[len(token):].strip()
        result += JackTokenizer.write_term(token, "IDENTIFIER")
        
        token = JackTokenizer.advance(current)
        
        # Check if we have another variable. If so, add it
        while token == ",":
            print("ADDING NEW ARG")
            result += JackTokenizer.write_term(token, "SYMBOL")
            current = current[len(token):].strip()
            
            token = JackTokenizer.advance(current)  # varName
            print(f"next varName: {token}")
            current = current[len(token):].strip()
            result += JackTokenizer.write_term(token, "IDENTIFIER")
            
            token = JackTokenizer.advance(current)
        
        current = current[len(token):].strip()
        print(f"Adding {token}")
        result += JackTokenizer.write_term(token, "SYMBOL")  # ;
        
        result += "</varDec>\n"
        
        return result
    
    def compileStatements():  # *Statements
        global current
        result = "<statements>\n"
        
        token = JackTokenizer.advance(current)
        print(f"compileStatements Token:{token}")
        
        while (token == "let" or token == "if" or token == "while" or token == "do" or token == "return"):
            current = current[len(token):].strip()
            print(f"NEW CURRENT:{current}")
            
            if token == "let":
                result += CompilationEngine.compileLet()
                print("DONE LET")
            elif token == "if":
                result += CompilationEngine.compileIf()
            elif token == "while":
                result += CompilationEngine.compileWhile()
                print("DONE WHILE")
            elif token == "do":
                result += CompilationEngine.compileDo()
            elif token == "return":  
                result += CompilationEngine.compileReturn()
                
            try:  # Check if anything is left
                token = JackTokenizer.advance(current)
                print(f"TOKEN AFTER ADVANCE: {token}")
            except IndexError:
                break
            
                
        result += "</statements>\n"
            
        return result
        
            
    def compileLet():  # 'let' varName('[' expression ']')? '=' expression';'
        global current
        result = "<letStatement>\n"
        print("compilelet")
        result += "<keyword> let </keyword>\n"
        
        token = JackTokenizer.advance(current)  # varName
        print(f"varName: {token}")
        current = current[len(token):].strip()
        result += JackTokenizer.write_term(token, "IDENTIFIER")
        
        token = JackTokenizer.advance(current)
        
        # May be array entry
        if token == "[":
            print("ADDING [")
            current = current[len(token):].strip()
            result += "<symbol> [ </symbol>\n"
            
            result = CompilationEngine.compileExpression()
            
            token =JackTokenizer.advance(current)
            current = current[len(token):].strip()
            if token == "]":
                print("ADDING ]")
                result += "<symbol> ] </symbol>\n"
            
            token = JackTokenizer.advance(current)
        
        # =
        current = current[len(token):].strip()
        if token == "=":
            result += "<symbol> = </symbol>\n"
            print("ADDING =")
        
        result += CompilationEngine.compileExpression()
        
        token = JackTokenizer.advance(current)  # ;
        current = current[len(token):].strip()
        if token == ";":
            print("ADDING ;")
            result += "<symbol> ; </symbol>\n"
            
        result += "</letStatement>\n"
        
        return result
    
    
    def compileIf():  # 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        global current
        print("compile if")
        result = "<ifStatement>\n"
        result += "<keyword> if </keyword>\n"

        token = JackTokenizer.advance(current)  # (
        current = current[len(token):].strip()  
        if token == "(":
            print("ADDING (")
            result += "<symbol> ( </symbol>\n"
    
        result += CompilationEngine.compileExpression() # Insert expression

        token = JackTokenizer.advance(current)  # )
        current = current[len(token):].strip()
        if token == ")":
            print("ADDING )")
            result += "<symbol> ) </symbol>\n" 

        token = JackTokenizer.advance(current)  # {
        current = current[len(token):].strip()
        if token == "{":
            print("ADDING {")
            result += "<symbol> { </symbol>\n"
        
        token = JackTokenizer.advance(current)  # Statements

        # Add every statement, checking for errors
        if (token == "let" or token == "if" or token == "while" or token == "do" or token == "return"):
            result += CompilationEngine.compileStatements()
        
        token = JackTokenizer.advance(current)
        if token == "}":  # Ensure next token is '}'
            print("ADDING }")
            result += "<symbol> } </symbol>\n"
            current = current[len(token):].strip()
        
        token = JackTokenizer.advance(current)  # May be else, must check
        
        if token == "else":
            print("ADDING ELSE")
            current = current[len(token):].strip()
            result += "<keyword> else </keyword>\n"

            token = JackTokenizer.advance(current)
            current = current[len(token):].strip()
            if token == "{":
                print("ADDING {")
                result += "<symbol> { </symbol>\n"
            
            result += CompilationEngine.compileStatements()
            
            token = JackTokenizer.advance(current)
            current = current[len(token):].strip()
            if token == "}":
                print("ADDING }")
                result += "<symbol> } </symbol>\n"
        
        result += "</ifStatement>\n"
    
        return result
        
    def compileWhile():  # 'while' '(' expression ')' '{' statements '}'
        global current
        print('comepile while')
        result = "<whileStatement>\n"
        result += "<keyword> while </keyword>\n"
        
        token = JackTokenizer.advance(current)  # (
        current = current[len(token):].strip()
        if token == "(":  # Ensure next token is '(', then insert
            print("ADDING (")
            result += "<symbol> ( </symbol>\n"
        
        result += CompilationEngine.compileExpression() # Insert expression
        print(f"RESULT AFTER FIRST COMPILE EXPRESSION: {result}")

        token = JackTokenizer.advance(current)
        current = current[len(token):].strip()
        if token == ")":  # Ensure next token is ')'
            print("ADDING )")
            result += "<symbol> ) </symbol>\n" 
        
        token = JackTokenizer.advance(current)
        current = current[len(token):].strip()
        if token == "{":  # Ensure next token is '{'
            result += "<symbol> { </symbol>\n"
            print("ADDING {")
            
        token = JackTokenizer.advance(current)
        print(f"NEXT TOKEN: {token}")
        # Add every statement, checking for errors
        if (token == "let" or token == "if" or token == "while" or token == "do" or token == "return"):
            result += CompilationEngine.compileStatements()
        
        token = JackTokenizer.advance(current)
        if token == "}":  # Ensure next token is '}'
            result += "<symbol> } </symbol>\n" 
            print("ADDING }")
            
        current = current[len(token):].strip()
        result += "</whileStatement>\n"  # Complete while statement
        print(f"FINAL: {result}")
    
        return result
    
    
    def compileDo():  # 'do' subroutineCall';'
        global current
        print("compiel do")
        result = "<doStatement>\n"    
        result += "<keyword> do </keyword>\n"
        
        # SubroutineCall
        token = JackTokenizer.advance(current)  # subroutineName
        print(f"subroutineName: {token}")
        current = current[len(token):].strip()
        nextToken = JackTokenizer.advance(current)  # Either a function ('(') or method ('.')
        print(f"Either function or method: {nextToken}")
        current = current[len(nextToken):].strip()
        
        if nextToken == "(":  # Function: bar(expressionList)
            print("FUNCTION")
            result += JackTokenizer.write_term(token, "IDENTIFIER")
            result += JackTokenizer.write_term(nextToken, "SYMBOL")
            
            result += CompilationEngine.compileExpressionList()
            
            token = JackTokenizer.advance(current)  # )
            current = current[len(token):].strip()
            if token == ")":
                result += "<symbol> ) </symbol>\n"
            
        
        elif nextToken == ".":  # Method: foo.bar(expressionList)
            print("METHOD")
            result += JackTokenizer.write_term(token, "IDENTIFIER")
            result += JackTokenizer.write_term(nextToken, "SYMBOL")
            
            token = JackTokenizer.advance(current)  # bar
            current = current[len(token):].strip()
            result += JackTokenizer.write_term(token, "IDENTIFIER")
            
            token = JackTokenizer.advance(current)  # (
            current = current[len(token):].strip()
            if token == "(":
                print("ADDING (")
                result += "<symbol> ( </symbol>\n"
                
            result += CompilationEngine.compileExpressionList()
            
            token = JackTokenizer.advance(current)  # )
            current = current[len(token):].strip()
            if token == ")":
                print("ADDDING )")
                result += "<symbol> ) </symbol>\n"

        token = JackTokenizer.advance(current)
        current = current[len(token):].strip() 
        
        if token == ";":  # Ensure next token is '}'
            print("ADDING ;")
            result += "<symbol> ; </symbol>\n"       
        
        result += "</doStatement>\n"
        
        print(f"DO statement done: {result}")
            
        return result
    
    def compileReturn():  # 'return' expression?';'
        global current
        print('compile return')
        result = "<returnStatement>\n"
        result += "<keyword> return </keyword>\n"
        
        token = JackTokenizer.advance(current)
        if token == ";":  # If no args
            print("ADDING ;")
            current = current[len(token):].strip()
            result += "<symbol> ; </symbol>\n"
        else:
            result += CompilationEngine.compileExpression()
            token = JackTokenizer.advance(current)  # ;
            current = current[len(token):].strip()
            token = JackTokenizer.write_term(";", "SYMBOL")
            
        result += "</returnStatement>\n"
            
        return result
    
    def compileExpression():  # term (op term)*
        global current
        print('compile expression')
        result = "<expression>\n"
        print(f"CURRENT IN EXPRESSION:{current}")
        
        result += CompilationEngine.compileTerm()
        
        token = JackTokenizer.advance(current) # May be op, otherwise done
        print(f"TOKEN AFTER ADVANCING IN EXPRESSION: {token}") 
        
        while token in op:  # Add all additional terms
            print(f"ADDING OP:{token}")
            current = current[len(token):].strip()
            result += JackTokenizer.write_term(token, "SYMBOL")          
            result += CompilationEngine.compileTerm()
            token = JackTokenizer.advance(current)
        
        result += "</expression>\n"
        print(f"RESULT AFTER COMPILE EXPRESSION: {result}")
        print(f"CURRENT:{current}")
        return result
    
    def compileTerm():  # intConstant | stringConstant | kwConstant | varName | varname[Exp] | subroutineCall | (expression) | unaryOp term
        global current
        result = "<term>\n"
        print("compile term")
        token = JackTokenizer.advance(current)
        print(f"TOKEN IN TERM:{token}")
        
        tokenType = JackTokenizer.tokenType(token)
        current = current[len(token):].strip()
        
        if tokenType == "INT_CONST" or tokenType == "STRING_CONST" or tokenType == "KEYWORD":
            print("CONST")
            result += JackTokenizer.write_term(token, tokenType)
            
        elif token in op:
            print("OP")
            result += JackTokenizer.write_term(token, "SYMBOL")
            
            result += CompilationEngine.compileTerm()
                
        elif token == "(":
            result += "<symbol> ( </symbol>\n"
            
            result += CompilationEngine.compileExpression()
            
            tokenType = JackTokenizer.tokenType(token)
            current = current[len(token):].strip()
            
            if token == ")":
                print("ADDING )")
                result += "<symbol> ) </symbol>\n"
            
        elif tokenType == "IDENTIFIER":  # If not constant, check next token
            print("IDENTIFIER")

            nextToken = JackTokenizer.advance(current)
            if nextToken == "[":  # Array entry: foo[expression]
                print("ADDING [")
                current = current[len(nextToken):].strip()
                result += JackTokenizer.write_term(token, "IDENTIFIER")
                result += JackTokenizer.write_term(nextToken, "SYMBOL")
                
                result += CompilationEngine.compileExpression()
                
                token = JackTokenizer.advance(current)
                current = current[len(token):].strip()
                if token == "]":
                    print("ADDING ]")
                    result += "<symbol> ] </symbol>\n"

                            
            elif nextToken == ".":  # Method: foo.bar(expressionList)
                current = current[len(nextToken):].strip()
                result += JackTokenizer.write_term(token, "IDENTIFIER")
                result += JackTokenizer.write_term(nextToken, "SYMBOL")
                
                token = JackTokenizer.advance(current)  # bar
                current = current[len(token):].strip()
                result += JackTokenizer.write_term(token, "IDENTIFIER")
                
                token = JackTokenizer.advance(current)  # (
                current = current[len(token):].strip()
                if token == "(":
                    result += "<symbol> ( </symbol>\n"
                    
                result += CompilationEngine.compileExpressionList()
                
                token = JackTokenizer.advance(current)  # )
                current = current[len(token):].strip()
                if token == ")":
                    print("ADDING )")
                    result += "<symbol> ) </symbol>\n"
    
                
            elif nextToken == "(":  # Function: bar(expressionList)
                current = current[len(nextToken):].strip()
                result += JackTokenizer.write_term(token, "IDENTIFIER")
                result += JackTokenizer.write_term(nextToken, "SYMBOL")
                
                result += CompilationEngine.compileExpressionList()
                
                token = JackTokenizer.advance()
                current = current[len(token):].strip()
                if token == ")":
                    print("ADDING )")
                    result += "<symbol> ) </symbol>\n"
            
                
            else:  # Variable: foo
                print("VARIABLE")
                result += JackTokenizer.write_term(token, "IDENTIFIER")
        
        result += "</term>\n"
        print(f"RESULT AFTER TERM: {result}")
        
        return result
    
    def compileExpressionList():  # (expression (',' expression)*)?
        global current
        result = "<expressionList>\n"
        print('compile exp list')
        token = JackTokenizer.advance(current)
        
        if token != ")":  # If we have any args
            result += CompilationEngine.compileExpression()
            
            token = JackTokenizer.advance(current)
            
            while token == ",":  # If we have more args
                current = current[len(token):].strip()
                result += "<symbol> , </symbol>\n"
                
                token = JackTokenizer.advance(current)
                result += CompilationEngine.compileExpression()
                
                token = JackTokenizer.advance(current)
        
        result += "</expressionList>\n"
        
        return result
    
def main():
    
    length = len(sys.argv)
    
    if length != 2:
        sys.exit("Error: Provide a File/Directory")
    else:
        [name] = sys.argv[1:]  # Unpack full file/directory name to variable
        
    global current
    current = ""
        
    if os.path.isfile(name):  # If this is a file
        
        content, outFile = JackTokenizer.init(name)
        result = ""
        
        current = content

        while len(current) != 0:  # While there are still tokens in this instruction:
            token = JackTokenizer.advance(current)  # Get next token
            print(f"main TOKEN:{token}")
            
            if token in statements:
                print("IN STATEMENTS")
                result += CompilationEngine.compileStatements()
                print("DONE")
            elif token == "class":
                result += CompilationEngine.compileClass()
                print("DONE")
            print(f"current result value:{result}")
                     
        with open(outFile, "w") as f:
            f.write(result)
            
    else:  # This is a directory
        paths = glob.glob(os.path.join(name, '*'))  # Get all files in this directory
        for file_path in paths:
            content, outFile = JackTokenizer.Initialize(file_path)
            JackTokenizer.write(content, outFile)
    
    
main()