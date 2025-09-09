-- function OrderedList(elem)

-- 	local lists = {}
--     table.insert(lists, pandoc.Plain{pandoc.RawInline('html', "<!-- START OF OL -->")})
-- 	table.insert(lists, elem)
-- 	table.insert(lists, pandoc.Plain{pandoc.RawInline('html', "<!-- END OF OL -->")})
-- 	return lists

-- end

-- function BulletList(elem)

-- 	local lists = {}
--     table.insert(lists, pandoc.Plain{pandoc.RawInline('html', "<!-- START OF BL -->")})
-- 	table.insert(lists, elem)
-- 	table.insert(lists, pandoc.Plain{pandoc.RawInline('html', "<!-- END OF BL -->")})
-- 	return lists

-- end