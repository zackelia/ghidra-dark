"""Represents _code_browser.tcd"""
import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom as MD
from preferences import Wrapped

TCD_LIST = [
    "_code_browser.tcd",
    "_debugger.tcd",
    "_version _tracking.tcd",
    "Version Tracking (DESTINATION TOOL).tool",
    "Version Tracking (SOURCE TOOL).tool",
]

class TCDBrowser:
    def __init__(self, path: str) -> None:
        self.path = path
        tree = ET.parse(path)
        self.root = tree.getroot()

    def _indent(self, elem, level=0):
        """Spacing fixup after adding new things"""
        i = "\n" + level*"    "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "    "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def update(self, preferences):
        # List comprehensions instead of a ton of nested statements
        tool = [_ for _ in self.root.iter() if _.tag == "TOOL"][0]
        tool_options = [_ for _ in tool.iter() if _.tag == "OPTIONS"][0]
        categories = [_ for _ in tool_options.iter() if _.tag == "CATEGORY" and "NAME" in _.attrib]

        # Add missing category tags
        names = [_.get("NAME") for _ in categories]
        for category in preferences.keys():
            if category not in names:
                c = ET.Element("CATEGORY")
                c.set("NAME", category)
                tool_options.insert(sys.maxsize, c)

        # Remake the categories list in case we added new ones
        categories = [_ for _ in tool_options.iter() if _.tag == "CATEGORY" and "NAME" in _.attrib]

        for category in categories:
            for preference, option in preferences.get(category.get("NAME"), {}).items():
                element = [_ for _ in category.iter() if _.get("NAME") == preference]

                # Check if the preference exists or not
                if len(element) == 0:
                    e = ET.Element(option.tag)
                    e.set("NAME", preference)

                    if isinstance(option, Wrapped):
                        e.set("CLASS", option.classname)
                        for state in option.states:
                            s = ET.SubElement(e, state.tag)
                            s.set("NAME", state.name)
                            s.set("TYPE", state.type)
                            s.set("VALUE", state.value)
                    else:
                        e.set("TYPE", option.type)
                        e.set("VALUE", option.value)

                    category.insert(sys.maxsize, e)

                else:
                    element = element[0]
                    if isinstance(option, Wrapped):
                        for state in option.states:
                            e = [_ for _ in element.iter() if _.get("NAME") == state.name][0]
                            e.set("VALUE", state.value)
                    else:
                        element.set("VALUE", option.value)

        self._indent(self.root)
    
        xmlstr = MD.parseString(ET.tostring(self.root)).toprettyxml(indent="", newl="", encoding="UTF-8")
        with open(self.path, "wb") as f:
            f.write(xmlstr)
