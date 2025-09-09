function Table(elem)

	local lists = {}
    table.insert(lists, pandoc.Plain{pandoc.RawInline('html', "<!-- START OF TABLE -->")})
	table.insert(lists, elem)
	table.insert(lists, pandoc.Plain{pandoc.RawInline('html', "<!-- END OF TABLE -->")})
	return lists

end