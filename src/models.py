from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal


# --------------------------------------------------------------------------
# JUPYTER NOTEBOOK PANDANTIC MODELS
# --------------------------------------------------------------------------

class LanguageInfo(BaseModel):
    name: str = "python"

class NotebookMetadata(BaseModel):
    language_info: LanguageInfo

class MarkdownCell(BaseModel):
    cell_type: Literal["markdown"] = "markdown"
    source: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    id: Optional[str] = None

class CodeCell(BaseModel):
    cell_type: Literal["code"] = "code"
    source: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_count: Optional[int] = None
    id: Optional[str] = None
    outputs: List[Dict[str, Any]] = Field(default_factory=list)

class JupyterNotebook(BaseModel):
    """The main model representing the entire .ipynb structure."""
    cells: List[Union[MarkdownCell, CodeCell]]
    metadata: NotebookMetadata = Field(default_factory=NotebookMetadata)
    nbformat: int = 4
    nbformat_minor: int = 5
    
    class Config:
        # This helps Pydantic generate a cleaner schema for the LLM
        json_schema_extra = {
            "example": {
                "cells": [
                    {
                        "cell_type": "markdown",
                        "source": ["## This is an explanation\n", "Here is some text."]
                    },
                    {
                        "cell_type": "code",
                        "source": ["import pandas as pd\n", "print('Hello World')"]
                    }
                ],
                "metadata": {"language_info": {"name": "python"}},
                "nbformat": 4,
                "nbformat_minor": 5
            }
        }
