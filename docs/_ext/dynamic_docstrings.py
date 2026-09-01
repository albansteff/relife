"""Griffe extension surfacing docstrings that relife composes at import time.

``relife.lifetime_models``'s ``document_args`` decorator (see
``src/relife/lifetime_models/_base.py``) rewrites ``method.__doc__`` at
decoration time by merging the base class's numpydoc ``Parameters``/``Returns``
sections. Griffe's static analysis never executes that decorator, so it only
sees the pre-decoration (empty) docstring. This extension re-imports each
``relife`` object after static collection and copies its live ``__doc__``,
restoring the docstrings mkdocstrings renders.
"""

import inspect

import griffe

logger = griffe.get_logger(__name__)


class DynamicDocstrings(griffe.Extension):
    def on_object(
        self, obj: griffe.Object, loader: griffe.GriffeLoader, **kwargs
    ) -> None:
        if obj.analysis == "dynamic" or not obj.path.startswith("relife."):
            return
        try:
            runtime_obj = griffe.dynamic_import(obj.path)
            doc = runtime_obj.__doc__
        except ImportError:
            logger.debug(f"Could not get dynamic docstring for {obj.path}")
            return
        if not doc:
            return
        doc = inspect.cleandoc(doc)
        if obj.docstring:
            obj.docstring.value = doc
        else:
            obj.docstring = griffe.Docstring(
                doc,
                parent=obj,
                parser=loader.docstring_parser,
                parser_options=loader.docstring_options,
            )
