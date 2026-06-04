"""Transformer-first News Overlay scaffold."""

from nlpcc.news_overlay.base import AvailabilityStatus, MethodSpec, ModelAvailabilityReport
from nlpcc.news_overlay.config import NewsOverlayConfig
from nlpcc.news_overlay.pipeline import ScaffoldNewsOverlayPipeline
from nlpcc.news_overlay.registry import get_method_spec, instantiate_method, list_method_specs

__all__ = [
    "AvailabilityStatus",
    "MethodSpec",
    "ModelAvailabilityReport",
    "NewsOverlayConfig",
    "ScaffoldNewsOverlayPipeline",
    "get_method_spec",
    "instantiate_method",
    "list_method_specs",
]
