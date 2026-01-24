from lxml import etree
from .models import TorznabCaps, TorznabResponse

def build_caps_xml(caps: TorznabCaps) -> str:
    """
    将 TorznabCaps 对象转换为标准的 Torznab Capabilities XML 字符串。
    """
    root = etree.Element("caps")
    
    # 1. Server info
    etree.SubElement(root, "server", title=caps.server_title, version=caps.server_version)
    
    # 2. Limits
    etree.SubElement(root, "limits", max=str(caps.max_items), default=str(caps.max_items))
    
    # 3. Registration
    etree.SubElement(root, "registration", status="no", local="no")
    
    # 4. Searching
    searching = etree.SubElement(root, "searching")
    for mode in caps.search_modes:
        etree.SubElement(
            searching, 
            mode.name, 
            available=mode.available, 
            supportedParams=",".join(mode.supported_params)
        )
        
    # 5. Categories
    categories_node = etree.SubElement(root, "categories")
    for cat in caps.categories:
        cat_node = etree.SubElement(categories_node, "category", id=str(cat.id), name=cat.name)
        for sub in cat.subcats:
            etree.SubElement(cat_node, "subcat", id=str(sub.id), name=sub.name)
            
    # 返回格式化后的 XML 字节串，转为字符串
    return etree.tostring(root, pretty_print=True, encoding="utf-8", xml_declaration=True).decode("utf-8")


def build_search_rss_xml(caps: TorznabCaps, response: TorznabResponse) -> str:
    """
    将 TorznabResponse 转换为标准的 Torznab RSS XML 字符串。
    """
    # 定义命名空间
    NSMAP = {
        "torznab": "http://torznab.com/schemas/2015/feed",
        "newznab": "http://newznab.com/schemas/2003/edits",
    }
    
    rss = etree.Element("rss", version="2.0", nsmap=NSMAP)
    channel = etree.SubElement(rss, "channel")
    
    # 1. 基础信息
    etree.SubElement(channel, "title").text = caps.server_title
    etree.SubElement(channel, "description").text = f"{caps.server_title} Torznab API"
    etree.SubElement(channel, "link").text = "" # 可以填 API 入口
    etree.SubElement(channel, "language").text = "zh-cn"
    
    # 2. Newznab 响应元数据
    newznab_resp = etree.SubElement(channel, "{http://newznab.com/schemas/2003/edits}response")
    newznab_resp.set("offset", str(response.offset))
    newznab_resp.set("total", str(response.total))
    
    # 3. 遍历生成 Item
    for item in response.items:
        node = etree.SubElement(channel, "item")
        etree.SubElement(node, "title").text = item.title
        etree.SubElement(node, "guid", isPermaLink="false").text = item.guid
        etree.SubElement(node, "link").text = item.link
        etree.SubElement(node, "pubDate").text = item.pub_date
        etree.SubElement(node, "size").text = str(item.size)
        
        # Enclosure 标签 (关键)
        etree.SubElement(node, "enclosure", {
            "url": item.enclosure_url,
            "length": str(item.enclosure_length),
            "type": item.enclosure_type
        })
        
        # Torznab Attributes
        for attr in item.attributes:
            attr_node = etree.SubElement(node, "{http://torznab.com/schemas/2015/feed}attr")
            attr_node.set("name", attr.name)
            attr_node.set("value", str(attr.value))
            
    return etree.tostring(rss, pretty_print=True, encoding="utf-8", xml_declaration=True).decode("utf-8")
