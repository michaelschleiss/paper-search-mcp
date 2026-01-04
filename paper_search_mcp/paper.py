# paper_search_mcp/paper.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional

@dataclass
class Paper:
    """Standardized paper format with core fields for academic sources"""
    # 核心字段（必填，但允许空值或默认值）
    paper_id: str              # Unique identifier (e.g., arXiv ID, PMID, DOI)
    title: str                 # Paper title
    authors: List[str]         # List of author names
    abstract: str              # Abstract text
    doi: str                   # Digital Object Identifier
    published_date: datetime   # Publication date
    pdf_url: str               # Direct PDF link
    url: str                   # URL to paper page
    source: str                # Source platform (e.g., 'arxiv', 'pubmed')

    # 可选字段
    updated_date: Optional[datetime] = None    # Last updated date
    categories: List[str] = None               # Subject categories
    keywords: List[str] = None                 # Keywords
    citations: int = 0                         # Citation count
    references: Optional[List[str]] = None     # List of reference IDs/DOIs
    extra: Optional[Dict] = None               # Source-specific extra metadata

    def __post_init__(self):
        """Post-initialization to handle default values"""
        if self.authors is None:
            self.authors = []
        if self.categories is None:
            self.categories = []
        if self.keywords is None:
            self.keywords = []
        if self.references is None:
            self.references = []
        if self.extra is None:
            self.extra = {}

    def to_dict(self, abstract_limit: int = 200) -> Dict:
        """Convert paper to dictionary format for serialization.

        Args:
            abstract_limit: Max chars for abstract. 0 = omit, -1 = full (default: 200)
        """
        # Process abstract based on limit
        if abstract_limit == 0:
            abstract = None
        elif abstract_limit > 0 and self.abstract and len(self.abstract) > abstract_limit:
            abstract = self.abstract[:abstract_limit] + '...'
        else:
            abstract = self.abstract

        result = {
            'id': self.paper_id,
            'title': self.title,
            'authors': '; '.join(self.authors) if self.authors else None,
            'abs': abstract,
            'date': self.published_date.strftime('%Y-%m-%d') if self.published_date else None,
            'pdf': self.pdf_url or self.url or None,
            'doi': self.doi or None,
            'cats': '; '.join(self.categories) if self.categories else None,
            'cites': self.citations if self.citations else None,
        }

        # Remove None/empty values
        return {k: v for k, v in result.items() if v is not None and v != ''}