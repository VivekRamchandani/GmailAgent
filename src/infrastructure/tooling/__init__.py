import inspect
import re

def func_tool(func):
    type_map = {
        "str": "string",
        "float": "number",
        "int": "integer",
        "bool": "boolean",
        "list": "array"
    }

    schema = {"type": "function"}
    schema["name"] = func.__name__
    parameters = {"type": "object"}
    properties = {}
    parameters["properties"] = properties
    required = []

    func_args = inspect.signature(func).parameters.items()
    for name, item in func_args:
        arg_prop = {}
        arg_type = item.annotation.__name__

        mapped_type = type_map.get(arg_type, None)
        if not mapped_type:     # Raise error for unsupported type
            raise TypeError(f"Type '{arg_type}' not acceptable.")
        arg_prop["type"] = mapped_type

        # Add default values to properties if set
        if item.default == inspect._empty:
            required.append(name)
        else:
            arg_prop["default"] = item.default

        properties[name] = arg_prop

    # Parsing Docstring for more information
    docstring = func.__doc__
    func_desc = ""

    mode = 0
    arg_pattern = re.compile(r'(\S+)\s*\(([^0-9]+)\)\s*:\s*(.+)')

    last_arg = None

    # Parsing docstring line by line
    for line in docstring.splitlines():
        line = line.strip()
        if not line:
            continue

        if line == "Args:":
            mode = 1
            continue
        if line == "Returns:" or line == "Raises":
            break

        if not mode:
            func_desc += line + "\n"
        else:
            m = arg_pattern.match(line)
            if m:
                name, _, desc = m.groups()
                last_arg = name
                properties[name]["description"] = desc
            else:
                if not last_arg:
                    raise SyntaxError("Malformed docstring")
                properties[last_arg]["description"] += "\n" + line

    schema["description"] = func_desc
    schema["parameters"] = parameters
    schema["required"] = required

    def wrapper(*args, **kwargs):
        # TODO: Add call information to the result for LLM
        result = func(*args, **kwargs)
        # TODO: Add error information if function call fails
        return result

    wrapper.schema = schema

    return wrapper


# TODO: Create decorator for converting class methods in tools