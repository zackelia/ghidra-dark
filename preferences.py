from typing import Tuple

class State():
    def __init__(self, value, name=""):
        self.tag = "STATE"
        self.name = name
        self.value = str(value)
        if type(value) == str:
            self.type = "string"
        elif type(value) == bool:
            self.type = "boolean"
        elif type(value) == int:
            self.type = "int"
        else:
            self.type = "unknown"

class Wrapped():
    def __init__(self, *states: Tuple[State]):
        self.tag = "WRAPPED_OPTION"
        self.states = states
        self.classname = "ghidra.framework.options.Wrapped{}".format(self.__class__.__name__)

class Color(Wrapped):
    def __init__(self, color: str):
        super().__init__(
            State(color, "color")    
        )

class Font(Wrapped):
    def __init__(self, size: int, style: int, family: str):
        super().__init__(
            State(size, "size"),
            State(style, "style"),
            State(family, "family")
        )

class KeyStroke(Wrapped):
    def __init__(self, keyCode: int, modifiers: int):
        super().__init__(
            State(keyCode, "KeyCode"),
            State(modifiers, "Modifiers")
        )

preferences = {
    "Listing Fields": {
        "Cursor Text Highlight.Highlight Color": Color(-13157567),
        "Cursor Text Highlight.Scoped Write Highlight Color": Color(-13157567),
        "Cursor Text Highlight.Scoped Read Highlight Color": Color(-13157567),
        "Selection Colors.Selection Color": Color(-11118501),
        "Selection Colors.Difference Color": Color(-11118501),
        "Selection Colors.Highlight Color": Color(-11118501),
        "Cursor.Cursor Color - Focused": Color(-3815226),
        "Cursor.Cursor Color - Unfocused": Color(-13157567),
        "Cursor.Highlight Cursor Line Color": Color(-13157567),
    },
    "Decompiler": {
        "Display.Color for Keywords": Color(-2190497),
        "Display.Background Color": Color(-14144978),
        "Display.Color for Parameters": Color(-8034417),
        "Display.Color for Constants": Color(-5946814),
        "Display.Color for Current Variable Highlight": Color(-13157567),
        "Display.Color Default": Color(-3815226),
        "Display.Color for Types": Color(-7564224),
        "Display.Color for Variables": Color(-3815226),
        "Display.Color for Comments": Color(-10518115),
        "Display.Color for Function names": Color(-10580601),
        "Display.Font": Font(14, 0, "Monospaced")
    },
    "Search": {
        "Highlight Color for Current Match": Color(-11974594),
        "Highlight Color": Color(-11974594),
    },
    "Listing Display": {
        "Background Color": Color(-14144978),
        "Mnemonic Color": Color(-3815226),
        "Bad Reference Address Color": Color(-5946814),
        "XRef Write Color": Color(-2190497),
        "Address Color": Color(-10066330),
        "Function Parameters Color": Color(-3815226),
        "Function Return Type Color": Color(-3815226),
        "Comment, Referenced Repeatable Color": Color(-10518115),
        "Constant Color": Color(-5946814),
        "XRef Other Color": Color(-3815226),
        "EOL Comment Color": Color(-10518115),
        "Labels, Primary Color": Color(-10518115),
        "Function Tag Color": Color(-8034417),
        "Bytes Color": Color(-8281410),
        "Post-Comment Color": Color(-10518115),
        "Function Call-Fixup Color": Color(-5073733),
        "Plate Comment Color": Color(-10518115),
        "Labels, Unreferenced Color": Color(-3815226),
        "Entry Point Color": Color(-3815226),
        "Pre-Comment Color": Color(-10518115),
        "Mnemonic, Override Color": Color(-3815226),
        "External Reference, Resolved Color": Color(-10580601),
        "Parameter, Dynamic Storage Color": Color(-10580601),
        "Parameter, Custom Storage Color": Color(-8034417),
        "Underline Color": Color(-5073733),
        "Field Name Color": Color(-3815226),
        "XRef Read Color": Color(-10518115),
        "Separator Color": Color(-3815226),
        "Version Track Color": Color(-5073733),
        "Comment, Automatic Color": Color(-10518115),
        "XRef Color": Color(-7564224),
        "Variable Color": Color(-8034417),
        "Flow Arrow, Active Color": Color(-3815226),
        "Labels, Local Color": Color(-7564224),
        "Function Name Color": Color(-10580601),
        "Comment, Repeatable Color": Color(-10518115),
        "BASE FONT": Font(14, 0, "Monospaced"),
    },
    "Comments": {
        "Enter accepts comment": State(True)
    },
}
