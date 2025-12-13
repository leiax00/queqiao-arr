-- Seed title parser dictionary data (idempotent)
-- Execute after tables are created.

-- Dict types
INSERT INTO dict_types (code, name, remark, is_active)
SELECT 'title_parser.resolution', '标题解析-分辨率', 'Builtin mapping for resolutions', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_types WHERE code = 'title_parser.resolution');

INSERT INTO dict_types (code, name, remark, is_active)
SELECT 'title_parser.source', '标题解析-来源', 'Builtin mapping for sources', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_types WHERE code = 'title_parser.source');

INSERT INTO dict_types (code, name, remark, is_active)
SELECT 'title_parser.hdr', '标题解析-HDR', 'Builtin mapping for HDR tags', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_types WHERE code = 'title_parser.hdr');

INSERT INTO dict_types (code, name, remark, is_active)
SELECT 'title_parser.codec', '标题解析-编码', 'Builtin mapping for codecs', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_types WHERE code = 'title_parser.codec');

INSERT INTO dict_types (code, name, remark, is_active)
SELECT 'title_parser.audio', '标题解析-音轨', 'Builtin mapping for audio', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_types WHERE code = 'title_parser.audio');

INSERT INTO dict_types (code, name, remark, is_active)
SELECT 'title_parser.subtitle', '标题解析-字幕', 'Builtin mapping for subtitle languages', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_types WHERE code = 'title_parser.subtitle');

INSERT INTO dict_types (code, name, remark, is_active)
SELECT 'title_parser.tag', '标题解析-标签', 'Builtin mapping for tags', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_types WHERE code = 'title_parser.tag');

INSERT INTO dict_types (code, name, remark, is_active)
SELECT 'title_parser.rule', '标题解析-规则', 'Builtin regex rules for parser', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_types WHERE code = 'title_parser.rule');

INSERT INTO dict_types (code, name, remark, is_active)
SELECT 'quality', '质量标签', 'Quality presets', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_types WHERE code = 'quality');

-- title_parser.resolution
INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.resolution', '2160P', '2160p', '2160p', 1, 'builtin', '{"aliases":["4K"],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.resolution' AND code = '2160P');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.resolution', '1080P', '1080p', '1080p', 2, 'builtin', '{"aliases":[],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.resolution' AND code = '1080P');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.resolution', '720P', '720p', '720p', 3, 'builtin', '{"aliases":[],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.resolution' AND code = '720P');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.resolution', '480P', '480p', '480p', 4, 'builtin', '{"aliases":[],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.resolution' AND code = '480P');

-- title_parser.source
INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.source', 'WEB-DL', 'WEB-DL', 'WEB-DL', 1, 'builtin', '{"aliases":["WEBDL","WEB"],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.source' AND code = 'WEB-DL');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.source', 'WEBRIP', 'WEBRip', 'WEBRip', 2, 'builtin', '{"aliases":["WEB-RIP"],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.source' AND code = 'WEBRIP');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.source', 'BLURAY', 'BluRay', 'BluRay', 3, 'builtin', '{"aliases":["BDRIP","BDRip"],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.source' AND code = 'BLURAY');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.source', 'HDTV', 'HDTV', 'HDTV', 4, 'builtin', '{"aliases":[],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.source' AND code = 'HDTV');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.source', 'DVDRIP', 'DVDRip', 'DVDRip', 5, 'builtin', '{"aliases":[],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.source' AND code = 'DVDRIP');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.source', 'B-GLOBAL', 'B-Global', 'WEB-DL', 6, 'builtin', '{"aliases":["B-Global","B-GLOBAL"],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.source' AND code = 'B-GLOBAL');

-- title_parser.hdr
INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.hdr', 'HDR10+', 'HDR10+', 'HDR10+', 1, 'builtin', '{"aliases":[],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.hdr' AND code = 'HDR10+');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.hdr', 'HDR10', 'HDR10', 'HDR10', 2, 'builtin', '{"aliases":[],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.hdr' AND code = 'HDR10');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.hdr', 'HDR', 'HDR', 'HDR', 3, 'builtin', '{"aliases":[],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.hdr' AND code = 'HDR');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.hdr', 'DOLBYVISION', 'DolbyVision', 'DolbyVision', 4, 'builtin', '{"aliases":["DOVI","DV","Dolby.Vision"],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.hdr' AND code = 'DOLBYVISION');

-- title_parser.codec
INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.codec', 'HEVC', 'HEVC', 'HEVC', 1, 'builtin', '{"aliases":["H265","X265","H.265"],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.codec' AND code = 'HEVC');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.codec', 'H264', 'H264', 'H264', 2, 'builtin', '{"aliases":["X264","H.264"],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.codec' AND code = 'H264');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.codec', 'AV1', 'AV1', 'AV1', 3, 'builtin', '{"aliases":[],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.codec' AND code = 'AV1');

-- title_parser.audio
INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.audio', 'AAC', 'AAC', 'AAC', 1, 'builtin', '{"aliases":[],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.audio' AND code = 'AAC');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.audio', 'AC3', 'AC3', 'AC3', 2, 'builtin', '{"aliases":[],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.audio' AND code = 'AC3');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.audio', 'EAC3', 'EAC3', 'EAC3', 3, 'builtin', '{"aliases":["DDP"],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.audio' AND code = 'EAC3');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.audio', 'FLAC', 'FLAC', 'FLAC', 4, 'builtin', '{"aliases":[],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.audio' AND code = 'FLAC');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.audio', 'DTS-HD', 'DTS-HD', 'DTS-HD', 5, 'builtin', '{"aliases":[],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.audio' AND code = 'DTS-HD');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.audio', 'DTS', 'DTS', 'DTS', 6, 'builtin', '{"aliases":[],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.audio' AND code = 'DTS');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.audio', 'TRUEHD', 'TrueHD', 'TrueHD', 7, 'builtin', '{"aliases":[],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.audio' AND code = 'TRUEHD');

-- title_parser.subtitle
INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.subtitle', 'CHS', '简体', 'chs', 1, 'builtin', '{"aliases":["简体","GB","CHS"],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.subtitle' AND code = 'CHS');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.subtitle', 'CHT', '繁体', 'cht', 2, 'builtin', '{"aliases":["繁体","繁體","BIG5","CHT"],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.subtitle' AND code = 'CHT');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.subtitle', 'CHS&CHT', '简繁', 'chs&cht', 3, 'builtin', '{"aliases":["简繁","简繁内封","简繁內封","CHS&CHT"],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.subtitle' AND code = 'CHS&CHT');

-- title_parser.tag
INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.tag', 'GLOBAL', 'B-Global', 'B-Global', 1, 'builtin', '{"aliases":["B-GLOBAL","B-Global"],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.tag' AND code = 'GLOBAL');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.tag', 'DUAL_AUDIO', '国粤双语', '国粤双语', 2, 'builtin', '{"aliases":["双语","雙語"],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.tag' AND code = 'DUAL_AUDIO');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.tag', 'COLLECTION', '合集', '合集', 3, 'builtin', '{"aliases":["合集","Collection","Complete"],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.tag' AND code = 'COLLECTION');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.tag', 'NC', 'NC', 'NC', 4, 'builtin', '{"aliases":["NCOP","NCED","NC-OP","NC-ED"],"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.tag' AND code = 'NC');

-- title_parser.rule
INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.rule', 'is_finale', '完结标记', 'true', 1, 'builtin rule', '{"pattern":"\\bEND\\b|完结|全集|完結","priority":10,"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.rule' AND code = 'is_finale');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'title_parser.rule', 'special_type', 'OVA/SP 标记', 'OVA', 2, 'builtin rule', '{"pattern":"\\b(OVA|SP)\\b","priority":20,"kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'title_parser.rule' AND code = 'special_type');

-- quality
INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'quality', '8K', '8K超高清', '8K', 1, 'builtin', '{"priority":10,"resolution":"7680x4320","kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'quality' AND code = '8K');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'quality', '4K', '4K超高清', '4K', 2, 'builtin', '{"priority":9,"resolution":"3840x2160","kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'quality' AND code = '4K');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'quality', '1080p', '1080p全高清', '1080p', 3, 'builtin', '{"priority":8,"resolution":"1920x1080","kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'quality' AND code = '1080p');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'quality', '720p', '720p高清', '720p', 4, 'builtin', '{"priority":7,"resolution":"1280x720","kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'quality' AND code = '720p');

INSERT INTO dict_items (dict_type_code, code, name, value, sort_order, remark, extra_data, is_active)
SELECT 'quality', '480p', '480p标清', '480p', 5, 'builtin', '{"priority":6,"resolution":"720x480","kind":"builtin"}', 1
WHERE NOT EXISTS (SELECT 1 FROM dict_items WHERE dict_type_code = 'quality' AND code = '480p');
