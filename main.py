import os

from utils import MenuTools

from decode import decode, ExportType

__version__ = "0.0.1"

def format_min():
    decode(export_type=ExportType.ALL)


def only_format():
    decode(export_type=ExportType.FORMAT)


def only_min():
    decode(export_type=ExportType.MIN)


def run():
    MenuTools(
        title="--- lua转json工具 v%s ---" % __version__,
        options={
            format_min: "导出格式化和min.json",
            only_format: "仅导出格式化的json",
            only_min: "仅导出min.json",
        },
    ).show()

    os.system("pause")
    run()


if __name__ == "__main__":
    run()
