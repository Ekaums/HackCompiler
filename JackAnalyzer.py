import regex as re
import sys
import os
import glob


class JackTokenizer():
        
    global symbols, keywords
    symbols = r"{}()[].;+-*/&|,<>=~"
    keywords = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"]
    
    @staticmethod
    def __init__(self, file):  # Open jack file for parsing
    
        #Initialization
        outName = file.split(".")[0]  # Get file name without extension, for output file
        outName += "T.xml"
    
        content = []
        pattern = r"^(.*?)(?=\/\/|\/\*\*| \*|$)"
            
        with open(file) as f:
            for line in f:
                match = re.search(pattern, line)  # Get every instruction, and put in content
                match = match.group().strip()
                if match:
                    content.append(match)
                        
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
        return f"<integerConstant> {token} </integerConstant>" 

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
            
        return f"<symbol> {token} </symbol>" 
        
    @staticmethod
    def keyWord(token):
        return f"<keyword> {token} </keyword>"
    
    @staticmethod
    def stringVal(token):
        return f"<stringConstant> {token} </stringConstant>"
    
    @staticmethod
    def identifier(token):
        return f"<identifier> {token} </identifier>"
    
    @staticmethod
    def write(content):
            return
                
    
        #if tokenType == "INT_CONST":
        #    f.write(f"{JackTokenizer.intVal(token)}\n")
       # elif tokenType == "SYMBOL":
       #     f.write(f"{JackTokenizer.symbol(token)}\n")
      #  elif tokenType == "KEYWORD":
       #     f.write(f"{JackTokenizer.keyWord(token)}\n")
      #  elif tokenType == "STRING_CONST":
       #     f.write(f"{JackTokenizer.stringVal(token)}\n")
       # elif tokenType == "IDENTIFIER":
        #    f.write(f"{JackTokenizer.identifier(token)}\n")


class CompilationEngine():
    
    def __init__(self):
        return
    
    def compileClass():
        return
    
    def compileClassVarDec():
        return
    
    def compileSubroutineDec():
        return
    
    def compileParameterList():
        return
        
    def compileSubroutineBody():
        return
    
    def compileVarDec():
        return
    
    def compileStatements():
        return
    
    def compileLet():
        return
    
    def compileIf():
        return
        
    def compileWhile():
        return
    def compileDo():
        return
    def compileReturn():
        return
    
    def compileExpression():
        return
    
    def compileTerm():
        return
    
    def compileExpressionList():
        return
    
    
def main():
    
    length = len(sys.argv)
    
    if length != 2:
        sys.exit("Error: Provide a File/Directory")
    else:
        [name] = sys.argv[1:]  # Unpack full file/directory name to variable
        
    if os.path.isfile(name):  # If this is a file
        content, outFile = JackTokenizer(name)
        JackTokenizer.write(content, outFile)
        
        
        with open("outfile", "w") as f:
            
            for line in content:
                while len(line) != 0:
                    
                    token = JackTokenizer.advance(line)  # Get next token
                    tokenType = JackTokenizer.tokenType(token)
                    # Splice the line to remove this token
                    line = line[len(token):]  
                    line = line.strip()
                    token = token.strip('"')
                    
                    
        
        
    else:  # This is a directory
        paths = glob.glob(os.path.join(name, '*'))  # Get all files in this directory
        for file_path in paths:
            content, outFile = JackTokenizer.Initialize(file_path)
            JackTokenizer.write(content, outFile)
    
    
    
main()

