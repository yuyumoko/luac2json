from enum import Enum
from pathlib import Path

from tqdm import tqdm

from utils import ArgRequire, ArgRequireOption

from LuaVm import LuaVm
import ujson


ag = ArgRequire(ArgRequireOption(save=True, save_path="config.ini"))


class ExportType(Enum):
    ALL = 0
    FORMAT = 1
    MIN = 2


LUA_VERSION_LIST = ["52", "53", "54"]

EXCLUDE_KEYS = ["io", "package", "_G"]


def init_res_json_type(lua_data):
    _keys = list(lua_data.keys())
    if len(_keys) > 0 and isinstance(_keys[0], int):
        return []
    else:
        return {}


def add_res_jon(res_json, key, data):
    if isinstance(res_json, list):
        res_json.append(data)
    else:
        res_json[key] = data
    return res_json


class LuaDecode(LuaVm):
    loaded = False

    def __init__(self, lua_version, lua_path: Path):
        super().__init__(lua_version)
        self.lua_path = lua_path

    def load_lua(self):
        if self.loaded:
            return

        lua_files = list(self.lua_path.glob("**/*.*"))
        print(f"found {len(lua_files)} files, start loading..")

        for file in tqdm(lua_files, total=len(lua_files)):
            self.run_lua(file)

        print("all files loaded")

        self.loaded = True

    def gen_lua_data(self, lua_data):
        if isinstance(lua_data, str):
            return lua_data

        res_json = init_res_json_type(lua_data)
        for key in lua_data:
            if key in EXCLUDE_KEYS:
                continue

            try:
                value = lua_data[key]
            except UnicodeDecodeError:
                res_json[key] = "UnicodeDecodeError"
                continue

            if self.data_is_dict(value):
                res_data = self.gen_lua_data(value)
            elif self.data_is_function(value):
                res_data = "lua function"
            else:
                res_data = value

            res_json = add_res_jon(res_json, key, res_data)

        return res_json

    def dump_lua_json(self):
        lua_data = self.globals()
        for key in tqdm(self.data_keys, total=len(self.data_keys)):
            res_data = self.gen_lua_data(lua_data[key]) or {}
            yield key, res_data


@ag.apply("请输入需要转换的lua目录:", "请输入转换后存放json的目录:", ("lua版本(52~54):", "54"))
def decode(
    lua_path: Path,
    output: Path,
    lua_version: str,
    export_type: ExportType,
):
    if lua_version not in LUA_VERSION_LIST:
        raise ValueError(f"lua version {lua_version} is not supported")

    if not lua_path.exists():
        raise ValueError(f"lua path {lua_path} not exists")

    print(f"start decode lua files in: {lua_path}")

    export_all = export_type == ExportType.ALL

    lua_decode = LuaDecode(lua_version, lua_path)
    lua_decode.load_lua()
    
    print(f"output json files in: {output}")

    for key, lua_json in lua_decode.dump_lua_json():
        if export_all or export_type == ExportType.FORMAT:
            with open(Path(output, f"{key}.json"), "w", encoding="utf-8") as f:
                f.write(
                    ujson.dumps(lua_json, indent=3, ensure_ascii=False, sort_keys=True)
                )
        if export_all or export_type == ExportType.MIN:
            with open(Path(output, f"{key}.min.json"), "w", encoding="utf-8") as f:
                f.write(ujson.dumps(lua_json, ensure_ascii=False))

    print("decode done")
