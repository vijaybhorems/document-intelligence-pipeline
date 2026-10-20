"""Document intelligence pipeline: messy contracts in, validated JSON records out."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("document-intelligence-pipeline")
except PackageNotFoundError:  # running from a source tree without an install
    __version__ = "0.0.0+unknown"
