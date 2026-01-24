import pytest
from app.services.torznab.models import TorznabCaps, TorznabCategory, TorznabSearchMode, TorznabResponse, TorznabItem, TorznabAttr
from app.services.torznab.xml_builder import build_caps_xml, build_search_rss_xml
from lxml import etree

@pytest.fixture
def sample_caps():
    return TorznabCaps(
        server_title="Test Indexer",
        categories=[
            TorznabCategory(id=5070, name="Anime"),
            TorznabCategory(id=5000, name="TV")
        ],
        search_modes=[
            TorznabSearchMode(name="search", supportedParams=["q"]),
            TorznabSearchMode(name="tvsearch", supportedParams=["q", "season", "ep"])
        ]
    )

def test_build_caps_xml(sample_caps):
    xml_str = build_caps_xml(sample_caps)
    root = etree.fromstring(xml_str.encode("utf-8"))
    
    assert root.tag == "caps"
    server = root.find("server")
    assert server.get("title") == "Test Indexer"
    
    categories = root.find("categories")
    assert len(categories.findall("category")) == 2
    assert categories.find("category[@id='5070']").get("name") == "Anime"

def test_build_search_rss_xml(sample_caps):
    item = TorznabItem(
        title="Test Anime S01E01",
        guid="unique-guid",
        link="http://example.com/download",
        pubDate="Sat, 24 Jan 2026 10:00:00 +0800",
        size=1024576,
        enclosure_url="http://example.com/download",
        enclosure_length=1024576,
        attributes=[
            TorznabAttr(name="season", value="1"),
            TorznabAttr(name="episode", value="1"),
            TorznabAttr(name="resolution", value="1080p")
        ]
    )
    response = TorznabResponse(offset=0, total=1, items=[item])
    
    xml_str = build_search_rss_xml(sample_caps, response)
    root = etree.fromstring(xml_str.encode("utf-8"))
    
    assert root.tag == "rss"
    channel = root.find("channel")
    item_node = channel.find("item")
    assert item_node.find("title").text == "Test Anime S01E01"
    
    # 检查 torznab 属性
    attrs = item_node.findall("{http://torznab.com/schemas/2015/feed}attr")
    assert len(attrs) == 3
    season_attr = item_node.find("{http://torznab.com/schemas/2015/feed}attr[@name='season']")
    assert season_attr.get("value") == "1"
    
    # 检查 enclosure
    enclosure = item_node.find("enclosure")
    assert enclosure.get("url") == "http://example.com/download"
    assert enclosure.get("length") == "1024576"
