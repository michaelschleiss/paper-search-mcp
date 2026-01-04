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

    def to_dict(self, compact: bool = True, abstract_limit: int = 200) -> Dict:
        """Convert paper to dictionary format for serialization.

        Args:
            compact: If True, omit empty/null fields to reduce token usage (default: True)
            abstract_limit: Max characters for abstract. 0 = omit, -1 = full (default: 200)
        """
        # Process abstract based on limit
        if abstract_limit == 0:
            abstract = None
        elif abstract_limit > 0 and self.abstract and len(self.abstract) > abstract_limit:
            abstract = self.abstract[:abstract_limit] + '...'
        else:
            abstract = self.abstract

        result = {
            'paper_id': self.paper_id,
            'title': self.title,
            'authors': '; '.join(self.authors) if self.authors else None,
            'abstract': abstract,
            'doi': self.doi or None,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'pdf_url': self.pdf_url or None,
            'url': self.url or None,
            'source': self.source,
            'updated_date': self.updated_date.isoformat() if self.updated_date else None,
            'categories': '; '.join(self.categories) if self.categories else None,
            'keywords': '; '.join(self.keywords) if self.keywords else None,
            'citations': self.citations if self.citations else None,
            'references': '; '.join(self.references) if self.references else None,
            'extra': str(self.extra) if self.extra else None
        }

        if compact:
            # Remove None/empty values to save tokens
            result = {k: v for k, v in result.items() if v is not None and v != ''}

        return result