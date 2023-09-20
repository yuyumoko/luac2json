from importlib import import_module

from pathlib import Path


LUA_LIB = {}


class LuaVm:
    data_keys = []
    data_func = {}

    def __init__(self, lua_version: str):
        self.lua_version = lua_version

        if LUA_LIB.get(lua_version) is None:
            LUA_LIB[lua_version] = import_module("lupa.lua%s" % lua_version)

        self.lua = LUA_LIB[lua_version]
        self.runtime = self.lua.LuaRuntime(register_eval=False)

    def get_lua(self):
        return LUA_LIB[self.lua_version]

    def globals(self):
        return self.runtime.globals()

    def lua_type(self, data):
        return self.lua.lua_type(data)

    def data_is_dict(self, data):
        return self.lua_type(data) == "table"

    def data_is_function(self, data):
        return self.lua_type(data) == "function"

    def run_lua(self, file: str | Path):
        if isinstance(file, str):
            file = Path(file)

        func_str = ""

        g1 = set(self.globals())
        try:
            res = self.runtime.execute(file.read_bytes())
        except self.get_lua().LuaError as e:
            func_str = f"function() {file.read_text()} end"
            res = self.runtime.eval(func_str)

        if res and func_str:
            self.data_func[file.stem] = func_str

        g2 = set(self.globals())
        self.data_keys += list(g2 - g1)
