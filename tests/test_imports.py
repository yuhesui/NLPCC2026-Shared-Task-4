import importlib


def test_package_imports():
    for module in [
        "nlpcc4",
        "nlpcc4.common.paths",
        "nlpcc4.execution.trade_converter",
        "nlpcc4.strategies.base",
        "nlpcc4.llm.parsers",
    ]:
        importlib.import_module(module)
