#latex.py
from pdftolatex.utils import *
             
class Text():
    """Class representing regular Latex text.
    Input - text: string"""
    def __init__(self, text):
        assert(isinstance(text, str))
        self.text = escape_special_chars(text)

class Command():
    """Class representing a Latex command.
    Input - command_name: string, arguments: list that can contain strings or Command objs, options: list of two-length tuples. idx1 is string representing option_type, idx2 is string or Command obj representing option val """
    def __init__(self, command_name, arguments = [], options = []):
        assert(isinstance(command_name, str))
        assert(all([isinstance(arg, str) or isinstance(arg, Command) for arg in arguments]))
        assert(all([isinstance(o[0], str) and (isinstance(o[1], str) or isinstance(o[1], Command)) for o in options]))
        
        self.command_name = command_name
        self.arguments = arguments
        self.options = options
        self.text = self.make_text()

    def make_text(self):
        """Output: string. Creates command string, formatting command name, args, and options"""
        text = "\\" + self.command_name

        arguments = ""
        if self.arguments:
            for arg in self.arguments:
                arg_text = arg.text if isinstance(arg, Command) else arg
                arguments += '{{{0}}}'.format(arg_text) 
        
        options, ostore = "", []
        if self.options:
            for o in self.options:
                o_type = o[0]
                o_val = o[1].text if isinstance(o[1], Command) else o[1]
                o_text = o_type + '=' + o_val if o_type else o_val
                ostore.append(o_text)
            options = '[{}]'.format(','.join(ostore))
               
        text += arguments + options if self.command_name == 'begin' else options + arguments
        return text

class Environment():
    """Class represing a Latex environment (document, figure, equation, etc.) 
    Input - body: list of other objects from latex.py, env_name: string, options: list of two-length tuples. idx1 is string representing option_type, idx2 is string or Command obj representing option val """
    def __init__(self, body, env_name, options = []):
        assert(isinstance(env_name, str))
        assert(all([isinstance(o[0], str) and (isinstance(o[1], str) or isinstance(o[1], Command)) for o in options]))
        assert(isinstance(body, list))

        self.env_name = env_name
        self.body = body
        self.options = options
        self.content = self.make_content()

    def make_content(self):
        """Output: List of Latex objects. Represents content in order of appearance in environment"""
        start, end = Command('begin', arguments=[self.env_name], options=self.options), Command('end', arguments=[self.env_name])
        content = [start] + self.body + [end]
        return content

def make_default_preamble():
    """Create default preamble to be used in TexFile"""
    default_preamble = []
    default_preamble.append(Command('documentclass', arguments=['article'], options=[('', 'a4paper'), ('', '12pt')]))
    default_preamble.append(Command('usepackage', arguments=['amsmath']))
    default_preamble.append(Command('usepackage', arguments=['amssymb']))
    default_preamble.append(Command('usepackage', arguments=['graphicx']))
    default_preamble.append(Command('usepackage', arguments=['geometry'], options=[('margin', '1in')]))
    default_preamble.append(Command('setlength', arguments=[Command('parindent'), '0pt']))
    return default_preamble

class TexFile():
    """Class representing a Latex file. Contains preamble and body which are lists of Latex objects that comprise of the Latex file's content"""
            
    def __init__(self, pdf_obj, use_default_preamble=True):
        self.preamble = make_default_preamble() if use_default_preamble else []
        self.body = pdf_obj.generate_latex()
    
    def generate_tex_file(self, filename):
        """Writes the preamble and body to file."""
        write_all(filename, self.unpack_content(self.preamble + self.body)) 
    
    def unpack_content(self, lst):
        """Output: list of strings. List contains lines of the Latex file in order of appearance"""
        content = []
        for obj in lst:
            if isinstance(obj, Environment):
                env_content = self.unpack_content(obj.content)
                content.extend(env_content)
            else:
                content.append(obj.text)
        return [s.replace("\x0c", Command('vspace', arguments=['10pt']).text) for s in content]

    def add_to_preamble(obj):
        """Add Latex obj to preamble."""
        self.preamble.append(obj)
