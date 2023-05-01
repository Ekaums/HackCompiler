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
        outName += ".xml"
        content = ""
        pattern = r"^(?:(?!\s\*\s))(.*?)(?=\/\/|\/\*\*|\*\/|$)"
            
        with open(file) as f:
            for line in f:
                    
                match = re.search(pattern, line)  # Get every instruction, and put in content
                if match:
                    match = match.group().strip()
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
        return "<stringConstant> {} </stringConstant>\n".format(token.strip('"'))
    
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
    op = ["+", "-", "=", ">", "<", "*", "/", "|", "~", "&"]
    global statements
    statements = ["if", "while", "do", "let", "return"]
    
    
    def __init__(self):
        return
    
    def compileClass():  # 'class' className'{' classVarDec* subroutineDec* '}'
        global current
        
        result = "<class>\n"
        
        token = JackTokenizer.advance(current)  # class
        current = current[len(token):].strip()
        result += JackTokenizer.write_term(token, "KEYWORD")
        
        token = JackTokenizer.advance(current)  # className
        current = current[len(token):].strip()
        result += JackTokenizer.write_term(token, "IDENTIFIER")  
        
        token = JackTokenizer.advance(current)
        current = current[len(token):].strip()
        
        if token == "{":  # Ensure next token is '{'
            result += "<symbol> { </symbol>\n"
        
        token = JackTokenizer.advance(current)  # Start of classVarDec
        
        while token == "static" or token == "field":
            result += CompilationEngine.compileClassVarDec()
            token = JackTokenizer.advance(current)
        
        while token == "constructor" or token == "function" or token == "method":  # Start of subroutineDec
            result += CompilationEngine.compileSubroutineDec()
            token = JackTokenizer.advance(current)
        
        if token == "}":  # Ensure next token is '}'
            result += "<symbol> } </symbol>\n"
            
        current = current[len(token):].strip()
        
        result += "</class>\n"
            
        return result
    
    def compileClassVarDec():  # ('static'|'field') type varName (',' varName)* ';'
        global current
        
        result = "<classVarDec>\n"
        
        token = JackTokenizer.advance(current)  # static or field
        current = current[len(token):].strip()
        result += JackTokenizer.write_term(token, "KEYWORD")
        
        token = JackTokenizer.advance(current)  # type
        current = current[len(token):].strip()
        tokenType = JackTokenizer.tokenType(token)
        result += JackTokenizer.write_term(token, tokenType)
        
        token = JackTokenizer.advance(current)  # varName
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
        current = current[len(token):].strip()
            
        result += "</classVarDec>\n"
        
        return result
    
    def compileSubroutineDec():  # ('constructor'|'function'|'method') ('void'| type) subroutineName '(' parameterList ')' subroutineBody
        global current
        
        result = "<subroutineDec>\n"

        token = JackTokenizer.advance(current)  # constructor or function or method
        current = current[len(token):].strip()
        if token == "constructor" or token == "function" or token == "method":
            result += JackTokenizer.write_term(token, "KEYWORD")
            
        token = JackTokenizer.advance(current)  # void or type
        current = current[len(token):].strip()
        tokenType = JackTokenizer.tokenType(token)
        if tokenType == "KEYWORD" or tokenType == "IDENTIFIER":
            result += JackTokenizer.write_term(token, tokenType)
        
        token = JackTokenizer.advance(current)  # subroutineName
        current = current[len(token):].strip()
        result += JackTokenizer.write_term(token, "IDENTIFIER")
        
        token = JackTokenizer.advance(current)
        current = current[len(token):].strip()
        if token == "(":  # Ensure next token is '('
            result += "<symbol> ( </symbol>\n"
        
        result += CompilationEngine.compileParameterList()
        
        token = JackTokenizer.advance(current)
        current = current[len(token):].strip()
        if token == ")":  # Ensure next token is ')'
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
                current = current[len(token):].strip()
                
                token = JackTokenizer.advance(current)  # varName
                result += JackTokenizer.write_term(token, "IDENTIFIER")
                current = current[len(token):].strip()
                
                token = JackTokenizer.advance(current)
        
        result += "</parameterList>\n"
        
        return result
        
    def compileSubroutineBody():  # '{' varDec* statements '}'
        global current
        
        result = "<subroutineBody>\n"
        
        token = JackTokenizer.advance(current)  # {
        current = current[len(token):].strip()
        if token == "{":
            result += "<symbol> { </symbol>\n"
        
        token = JackTokenizer.advance(current)  # var
        while token == "var":  # For all variables
            result += CompilationEngine.compileVarDec()
            token = JackTokenizer.advance(current)
        
        # Add every statement, checking for errors
        if (token == "let" or token == "if" or token == "while" or token == "do" or token == "return"):
            result += CompilationEngine.compileStatements()
            
        token = JackTokenizer.advance(current)  # }
        current = current[len(token):].strip()
        if token == "}":
            result += "<symbol> } </symbol>\n"
        
        result += "</subroutineBody>\n"
        
        return result
    
    def compileVarDec():  # 'var' type varName (',' varName)*';'
        global current
        
        result = "<varDec>\n"
        
        token = JackTokenizer.advance(current)  # var
        current = current[len(token):].strip()
        result += JackTokenizer.write_term(token, "KEYWORD")
        
        token = JackTokenizer.advance(current)  # type
        tokenType = JackTokenizer.tokenType(token)
        current = current[len(token):].strip()
        result += JackTokenizer.write_term(token, tokenType)
        
        token = JackTokenizer.advance(current)  # varName
        current = current[len(token):].strip()
        result += JackTokenizer.write_term(token, "IDENTIFIER")
        
        token = JackTokenizer.advance(current)
        
        # Check if we have another variable. If so, add it
        while token == ",":
            result += JackTokenizer.write_term(token, "SYMBOL")
            current = current[len(token):].strip()
            
            token = JackTokenizer.advance(current)  # varName
            current = current[len(token):].strip()
            result += JackTokenizer.write_term(token, "IDENTIFIER")
            
            token = JackTokenizer.advance(current)
        
        current = current[len(token):].strip()
        result += JackTokenizer.write_term(token, "SYMBOL")  # ;
        
        result += "</varDec>\n"
        
        return result
    
    def compileStatements():  # *Statements
        global current
        result = "<statements>\n"
        
        token = JackTokenizer.advance(current)
        
        while (token == "let" or token == "if" or token == "while" or token == "do" or token == "return"):
            current = current[len(token):].strip()
            
            if token == "let":
                result += CompilationEngine.compileLet()
            elif token == "if":
                result += CompilationEngine.compileIf()
            elif token == "while":
                result += CompilationEngine.compileWhile()
            elif token == "do":
                result += CompilationEngine.compileDo()
            elif token == "return":  
                result += CompilationEngine.compileReturn()
                
            try:  # Check if anything is left
                token = JackTokenizer.advance(current)
            except IndexError:
                break
            
                
        result += "</statements>\n"
            
        return result
        
            
    def compileLet():  # 'let' varName('[' expression ']')? '=' expression';'
        global current
        result = "<letStatement>\n"
        result += "<keyword> let </keyword>\n"
        
        token = JackTokenizer.advance(current)  # varName
        current = current[len(token):].strip()
        result += JackTokenizer.write_term(token, "IDENTIFIER")
        
        token = JackTokenizer.advance(current)
        
        # May be array entry
        if token == "[":
            current = current[len(token):].strip()
            result += "<symbol> [ </symbol>\n"
            
            result += CompilationEngine.compileExpression()
            
            token = JackTokenizer.advance(current)
            current = current[len(token):].strip()
            if token == "]":
                result += "<symbol> ] </symbol>\n"
            
            token = JackTokenizer.advance(current)
        
        # =
        current = current[len(token):].strip()
        if token == "=":
            result += "<symbol> = </symbol>\n"
        
        result += CompilationEngine.compileExpression()
        
        token = JackTokenizer.advance(current)  # ;
        current = current[len(token):].strip()
        if token == ";":
            result += "<symbol> ; </symbol>\n"
            
        result += "</letStatement>\n"
        
        return result
    
    
    def compileIf():  # 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        global current
        result = "<ifStatement>\n"
        result += "<keyword> if </keyword>\n"

        token = JackTokenizer.advance(current)  # (
        current = current[len(token):].strip()  
        if token == "(":
            result += "<symbol> ( </symbol>\n"
    
        result += CompilationEngine.compileExpression() # Insert expression

        token = JackTokenizer.advance(current)  # )
        current = current[len(token):].strip()
        if token == ")":
            result += "<symbol> ) </symbol>\n" 

        token = JackTokenizer.advance(current)  # {
        current = current[len(token):].strip()
        if token == "{":
            result += "<symbol> { </symbol>\n"
        
        token = JackTokenizer.advance(current)  # Statements

        # Add every statement, checking for errors
        if (token == "let" or token == "if" or token == "while" or token == "do" or token == "return"):
            result += CompilationEngine.compileStatements()
        
        token = JackTokenizer.advance(current)
        if token == "}":  # Ensure next token is '}'
            result += "<symbol> } </symbol>\n"
            current = current[len(token):].strip()
        
        token = JackTokenizer.advance(current)  # May be else, must check
        
        if token == "else":
            current = current[len(token):].strip()
            result += "<keyword> else </keyword>\n"

            token = JackTokenizer.advance(current)
            current = current[len(token):].strip()
            if token == "{":
                result += "<symbol> { </symbol>\n"
            
            result += CompilationEngine.compileStatements()
            
            token = JackTokenizer.advance(current)
            current = current[len(token):].strip()
            if token == "}":
                result += "<symbol> } </symbol>\n"
        
        result += "</ifStatement>\n"
    
        return result
        
    def compileWhile():  # 'while' '(' expression ')' '{' statements '}'
        global current
        result = "<whileStatement>\n"
        result += "<keyword> while </keyword>\n"
        
        token = JackTokenizer.advance(current)  # (
        current = current[len(token):].strip()
        if token == "(":  # Ensure next token is '(', then insert
            result += "<symbol> ( </symbol>\n"
        
        result += CompilationEngine.compileExpression() # Insert expression

        token = JackTokenizer.advance(current)
        current = current[len(token):].strip()
        if token == ")":  # Ensure next token is ')'
            result += "<symbol> ) </symbol>\n" 
        
        token = JackTokenizer.advance(current)
        current = current[len(token):].strip()
        if token == "{":  # Ensure next token is '{'
            result += "<symbol> { </symbol>\n"
            
        token = JackTokenizer.advance(current)
        # Add every statement, checking for errors
        if (token == "let" or token == "if" or token == "while" or token == "do" or token == "return"):
            result += CompilationEngine.compileStatements()
        
        token = JackTokenizer.advance(current)
        if token == "}":  # Ensure next token is '}'
            result += "<symbol> } </symbol>\n" 
            
        current = current[len(token):].strip()
        result += "</whileStatement>\n"  # Complete while statement
    
        return result
    
    
    def compileDo():  # 'do' subroutineCall';'
        global current
        result = "<doStatement>\n"    
        result += "<keyword> do </keyword>\n"
        
        # SubroutineCall
        token = JackTokenizer.advance(current)  # subroutineName
        current = current[len(token):].strip()
        nextToken = JackTokenizer.advance(current)  # Either a function ('(') or method ('.')
        current = current[len(nextToken):].strip()
        
        if nextToken == "(":  # Function: bar(expressionList)
            result += JackTokenizer.write_term(token, "IDENTIFIER")
            result += JackTokenizer.write_term(nextToken, "SYMBOL")
            
            result += CompilationEngine.compileExpressionList()
            
            token = JackTokenizer.advance(current)  # )
            current = current[len(token):].strip()
            if token == ")":
                result += "<symbol> ) </symbol>\n"
            
        
        elif nextToken == ".":  # Method: foo.bar(expressionList)
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
                result += "<symbol> ) </symbol>\n"

        token = JackTokenizer.advance(current)
        current = current[len(token):].strip() 
        
        if token == ";":  # Ensure next token is '}'
            result += "<symbol> ; </symbol>\n"       
        
        result += "</doStatement>\n"
            
        return result
    
    
    def compileReturn():  # 'return' expression?';'
        global current
        result = "<returnStatement>\n"
        result += "<keyword> return </keyword>\n"
        
        token = JackTokenizer.advance(current)
        if token == ";":  # If no args
            current = current[len(token):].strip()
            result += "<symbol> ; </symbol>\n"
        else:
            result += CompilationEngine.compileExpression()
            token = JackTokenizer.advance(current)  # ;
            current = current[len(token):].strip()
            result += JackTokenizer.write_term(";", "SYMBOL")
            
        result += "</returnStatement>\n"
            
        return result
    
    def compileExpression():  # term (op term)*
        global current
        result = "<expression>\n"
        
        result += CompilationEngine.compileTerm()
        
        token = JackTokenizer.advance(current) # May be op, otherwise done
        
        while token in op:  # Add all additional terms
            current = current[len(token):].strip()
            result += JackTokenizer.write_term(token, "SYMBOL")          
            result += CompilationEngine.compileTerm()
            token = JackTokenizer.advance(current)
        
        result += "</expression>\n"
        
        return result
    
    def compileTerm():  # intConstant | stringConstant | kwConstant | varName | varname[Exp] | subroutineCall | (expression) | unaryOp term
        global current
        result = "<term>\n"
        token = JackTokenizer.advance(current)
        
        tokenType = JackTokenizer.tokenType(token)
        current = current[len(token):].strip()
        
        if tokenType == "INT_CONST" or tokenType == "STRING_CONST" or tokenType == "KEYWORD":
            result += JackTokenizer.write_term(token, tokenType)
            
        elif token in op:
            result += JackTokenizer.write_term(token, "SYMBOL")
            
            result += CompilationEngine.compileTerm()
                
        elif token == "(":  # (expression)
            result += "<symbol> ( </symbol>\n"
            
            result += CompilationEngine.compileExpression()
            
            token = JackTokenizer.advance(current)
            current = current[len(token):].strip()
            
            if token == ")":
                result += "<symbol> ) </symbol>\n"
            
        elif tokenType == "IDENTIFIER":  # If not constant, check next token

            nextToken = JackTokenizer.advance(current)
            if nextToken == "[":  # Array entry: foo[expression]
                current = current[len(nextToken):].strip()
                result += JackTokenizer.write_term(token, "IDENTIFIER")
                result += JackTokenizer.write_term(nextToken, "SYMBOL")
                
                result += CompilationEngine.compileExpression()
                
                token = JackTokenizer.advance(current)
                current = current[len(token):].strip()
                if token == "]":
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
                    result += "<symbol> ) </symbol>\n"
    
                
            elif nextToken == "(":  # Function: bar(expressionList)
                current = current[len(nextToken):].strip()
                result += JackTokenizer.write_term(token, "IDENTIFIER")
                result += JackTokenizer.write_term(nextToken, "SYMBOL")
                
                result += CompilationEngine.compileExpressionList()
                
                token = JackTokenizer.advance()
                current = current[len(token):].strip()
                if token == ")":
                    result += "<symbol> ) </symbol>\n"
            
                
            else:  # Variable: foo
                result += JackTokenizer.write_term(token, "IDENTIFIER")
        
        result += "</term>\n"
        
        return result
    
    def compileExpressionList():  # (expression (',' expression)*)?
        global current
        result = "<expressionList>\n"
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
            
            if token in statements:
                result += CompilationEngine.compileStatements()
            elif token == "class":
                result += CompilationEngine.compileClass()
                     
        with open(outFile, "w") as f:
            f.write(result)
            
    else:  # This is a directory
        paths = glob.glob(os.path.join(name, '*'))  # Get all files in this directory
        for file_path in paths:
            
            content, outFile = JackTokenizer.init(file_path)
            result = ""
            
            current = content
            
            while len(current) != 0:  # While there are still tokens in this instruction:
                token = JackTokenizer.advance(current)  # Get next token
                
                if token in statements:
                    result += CompilationEngine.compileStatements()
                elif token == "class":
                    result += CompilationEngine.compileClass()
                    
            with open(outFile, "w") as f:
                f.write(result)
            
            
        
main()