'''
Created on Apr 24, 2013

@author: Lubo
'''
from ply import lex
import decimal
import re

SHOW_TOKENS = False
BACKWARDS_COMPATIBLE = False

def _raise_error(message, t, klass):
    lineno, lexpos, lexer = t.lineno, t.lexpos, t.lexer
    filename = lexer.filename

    # Switch from 1-based lineno to 0-based lineno
    geek_lineno = lineno - 1
    start_of_line = lexer.line_offsets[geek_lineno]
    end_of_line = lexer.line_offsets[geek_lineno+1]-1
    text = lexer.lexdata[start_of_line:end_of_line]
    offset = lexpos - start_of_line
    # use offset+1 because the exception is 1-based
    raise klass(message, (filename, lineno, offset+1, text))

def raise_syntax_error(message, t):
    _raise_error(message, t, SyntaxError)
    
def raise_indentation_error(message, t):
    _raise_error(message, t, IndentationError)
   
TOKEN = lex.TOKEN    
RESERVED = {
  "import" : "IMPORT",
  "def": "DEF",
  "if": "IF",
  "return": "RETURN",
  "class" : "CLASS"
  }

tokens = (
    "STATEMENT",
    "NEWLINE",
    "LPAR",
    "RPAR",
    "LBRACE",
    "RBRACE",

    "NUMBER",
    "NAME",
    "WS",

    "STRING_START_TRIPLE",
    "STRING_START_SINGLE",
    "STRING_CONTINUE",
    "STRING_END",
    "STRING",

    "INDENT",
    "DEDENT",
    #"ROVNASA",
    "ENDMARKER",
    "COLON",
    "CLASS",
    "DEF",
    "COMMA",
    "COMMENT"
    #"NAMEARGS"
    )

#t_ROVNASA = "\="
t_COMMA = ","
#t_CLASS = "class"

def t_CLASS(t):
    r'class'
    return t

def t_DEF(t):
    r'def'
    return t

def t_COLON(t):
    r':'
    return t

def t_COMMENT(t):
    r"[ ]*\043[^\n]*"  # \043 is '#' ; otherwise PLY thinks it's an re comment
    #pass
    return t

def t_WS(t):
    r" [ \t\f]+ "
    value = t.value 
    value = value.rsplit("\f", 1)[-1]
    pos = 0
    while 1:
        pos = value.find("\t")
        if pos == -1:
            break
        n = 8 - (pos % 8)
        value = value[:pos] + " "*n + value[pos+1:]

    if t.lexer.at_line_start and t.lexer.paren_count == 0:
        return t

def t_escaped_newline(t):
    r"\\\n"
    print("KUK")
    t.type = "STRING_CONTINUE"
    # Raw strings don't escape the newline
    assert not t.lexer.is_raw, "only occurs outside of quoted strings"
    t.lexer.lineno += 1

# Don't return newlines while I'm inside of ()s
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)
    t.type = "NEWLINE"
    #if t.lexer.paren_count == 0:
    return t

def t_LPAR(t):
    r"\("
    t.lexer.paren_count += 1
    return t

def t_RPAR(t):
    r"\)"
    t.lexer.paren_count -= 1
    return t

def t_LBRACE(t):
    r"\{"
    t.lexer.paren_count += 1
    return t

def t_RBRACE(t):
    r"\}"
    t.lexer.paren_count -= 1
    return t

#def t_NUMBER(t):
#    r"""(\d+(\.\d*)?|\.\d+)([eE][-+]? \d+)?"""
#    t.value = decimal.Decimal(t.value)
#    return t

error_message = {
    "STRING_START_TRIPLE": "EOF while scanning triple-quoted string",
    "STRING_START_SINGLE": "EOL while scanning single-quoted string",
}

def t_STATEMENT(t):
    r'[^:\n()]+'
    #r'.+'
    #r'.*^[\ ]'
    t.type = RESERVED.get(t.value, "STATEMENT")    # Check for reserved words
    return t

def _new_token(type,value, lineno):
    tok = lex.LexToken()
    tok.type = type
    tok.value = value
    tok.lineno = lineno
    tok.lexpos = -100
    return tok

# Synthesize a DEDENT tag
def DEDENT(lineno):
    return _new_token("DEDENT","ded", lineno)

# Synthesize an INDENT tag
def INDENT(lineno):
    return _new_token("INDENT","\t", lineno)

def t_error(t):
    raise_syntax_error("invalid syntax", t)

_lexer = lex.lex()

def _parse_quoted_string(start_tok, string_toks):
    # The four combinations are:
    #  "ur"  - raw_uncode_escape
    #  "u"   - uncode_escape
    #  "r"   - no need to do anything
    #  ""    - string_escape
    s = "".join(tok.value for tok in string_toks)
    quote_type = start_tok.value.lower()
    if quote_type == "":
        return s.decode("string_escape")
    elif quote_type == "u":
        return s.decode("unicode_escape")
    elif quote_type == "ur":
        return s.decode("raw_unicode_escape")
    elif quote_type == "r":
        return s
    else:
        raise AssertionError("Unknown string quote type: %r" % (quote_type,))

def create_strings(lexer, token_stream):
    for tok in token_stream:
        if not tok.type.startswith("STRING_START_"):
            yield tok
            continue

        # This is a string start; process until string end
        start_tok = tok
        string_toks = []
        for tok in token_stream:
            #print " Merge string", tok
            if tok.type == "STRING_END":
                break
            else:
                assert tok.type == "STRING_CONTINUE", tok.type
                string_toks.append(tok)
        else:
            # Reached end of input without string termination
            # This reports the start of the line causing the problem.
            # Python reports the end.  I like mine better.
            raise_syntax_error(error_message[start_tok.type], start_tok)

        # Reached the end of the string
        if BACKWARDS_COMPATIBLE and "SINGLE" in start_tok.type:
            # The compiler module uses the end of the single quoted
            # string to determine the strings line number.  I prefer
            # the start of the string.
            start_tok.lineno = tok.lineno
        start_tok.type = "STRING"
        start_tok.value = _parse_quoted_string(start_tok, string_toks)
        yield start_tok

NO_INDENT = 0
MAY_INDENT = 1
MUST_INDENT = 2

# only care about whitespace at the start of a line
def annotate_indentation_state(lexer, token_stream):
    lexer.at_line_start = at_line_start = True
    indent = NO_INDENT
    saw_colon = False
    for token in token_stream:
        if SHOW_TOKENS:
            print ("Got token:", token)
        token.at_line_start = at_line_start

        if token.type == "COLON":
            at_line_start = False
            indent = MAY_INDENT
            token.must_indent = False
            
        elif token.type == "NEWLINE":
            at_line_start = True
            if indent == MAY_INDENT:
                indent = MUST_INDENT
            token.must_indent = False

        elif token.type == "WS":
            assert token.at_line_start == True
            at_line_start = True
            token.must_indent = False

        else:
            # A real token; only indent after COLON NEWLINE
            if indent == MUST_INDENT:
                token.must_indent = True
            else:
                token.must_indent = False
            at_line_start = False
            indent = NO_INDENT

        yield token
        lexer.at_line_start = at_line_start


# Track the indentation level and emit the right INDENT / DEDENT events.
def synthesize_indentation_tokens(token_stream):
    # A stack of indentation levels; will never pop item 0
    levels = [0]
    token = None
    depth = 0
    prev_was_ws = False
    for token in token_stream:
##        if 1:
##            print "Process", token,
##            if token.at_line_start:
##                print "at_line_start",
##            if token.must_indent:
##               print "must_indent",
##            print
                
        # WS only occurs at the start of the line
        # There may be WS followed by NEWLINE so
        # only track the depth here.  Don't indent/dedent
        # until there's something real.
        if token.type == "WS":
            assert depth == 0
            depth = len(token.value)
            prev_was_ws = True
            # WS tokens are never passed to the parser
            continue

        if token.type == "NEWLINE":
            depth = 0
            if prev_was_ws or token.at_line_start:
                # ignore blank lines
                continue
            # pass the other cases on through
            yield token
            continue

        # then it must be a real token (not WS, not NEWLINE)
        # which can affect the indentation level

        prev_was_ws = False
        if token.must_indent:
            # The current depth must be larger than the previous level
            if not (depth > levels[-1]):
                raise_indentation_error("expected an indented block", token)

            levels.append(depth)
            yield INDENT(token.lineno)

        elif token.at_line_start:
            # Must be on the same level or one of the previous levels
            if depth == levels[-1]:
                # At the same level
                pass
            elif depth > levels[-1]:
                # indentation increase but not in new block
                raise_indentation_error("unexpected indent", token)
            else:
                # Back up; but only if it matches a previous level
                try:
                    i = levels.index(depth)
                except ValueError:
                    # I report the error position at the start of the
                    # token.  Python reports it at the end.  I prefer mine.
                    raise_indentation_error(
     "unindent does not match any outer indentation level", token)
                for _ in range(i+1, len(levels)):
                    yield DEDENT(token.lineno)
                    levels.pop()

        yield token

    ### Finished processing ###

    # Must dedent any remaining levels
    if len(levels) > 1:
        assert token is not None
        for _ in range(1, len(levels)):
            yield DEDENT(token.lineno)
    

def add_endmarker(token_stream):
    tok = None
    for tok in token_stream:
        yield tok
    if tok is not None:
        lineno = tok.lineno
    else:
        lineno = 1
    yield _new_token("ENDMARKER", "end",lineno)
_add_endmarker = add_endmarker

def make_token_stream(lexer, add_endmarker = True):
    token_stream = iter(lexer.token, None)
    token_stream = create_strings(lexer, token_stream)
    token_stream = annotate_indentation_state(lexer, token_stream)
    token_stream = synthesize_indentation_tokens(token_stream)
    if add_endmarker:
        token_stream = _add_endmarker(token_stream)
    return token_stream


_newline_pattern = re.compile(r"\n")
def get_line_offsets(text):
    offsets = [0]
    for m in _newline_pattern.finditer(text):
        offsets.append(m.end())
    # This is only really needed if the input does not end with a newline
    offsets.append(len(text))
    return offsets

class PythonLexer(object):
    def __init__(self, lexer = None):
        if lexer is None:
            lexer = _lexer.clone()
        self.lexer = lexer
        self.lexer.paren_count = 0
        self.lexer.is_raw = False
        self.lexer.filename = None
        self.token_stream = None

    def input(self, data, filename="<string>", add_endmarker=True):
        self.lexer.input(data)
        self.lexer.paren_count = 0
        self.lexer.is_raw = False
        self.lexer.filename = filename
        self.lexer.line_offsets = get_line_offsets(data)
        self.token_stream = make_token_stream(self.lexer, add_endmarker=True)

    def token(self):
        #print(self.)
        try:
            x = self.token_stream.__next__()
            #print ("Return", x)
            return x
        except StopIteration:
            return None

    def __iter__(self):
        return self.token_stream

lexer = PythonLexer()