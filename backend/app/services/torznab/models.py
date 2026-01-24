from typing import List, Optional
from pydantic import BaseModel, Field

class TorznabCategory(BaseModel):
    id: int
    name: str
    subcats: List["TorznabCategory"] = Field(default_factory=list)

class TorznabSearchMode(BaseModel):
    name: str
    available: str = "yes"
    supported_params: List[str] = Field(default_factory=list, alias="supportedParams")

    class Config:
        populate_by_name = True

class TorznabCaps(BaseModel):
    server_title: str = "Queqiao-arr"
    server_version: str = "1.0"
    max_items: int = 100
    categories: List[TorznabCategory] = Field(default_factory=list)
    search_modes: List[TorznabSearchMode] = Field(default_factory=list)

class TorznabAttr(BaseModel):
    name: str
    value: str

class TorznabItem(BaseModel):
    title: str
    guid: str
    link: str
    pub_date: str = Field(alias="pubDate")
    size: int
    enclosure_url: str
    enclosure_length: int
    enclosure_type: str = "application/x-bittorrent"
    
    # torznab 扩展属性
    attributes: List[TorznabAttr] = Field(default_factory=list)

    class Config:
        populate_by_name = True

class TorznabResponse(BaseModel):
    offset: int = 0
    total: int = 0
    items: List[TorznabItem] = Field(default_factory=list)
