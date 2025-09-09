function Para(elem)

    if #elem.content == 0 
    then 
        return pandoc.Para{pandoc.RawInline('html', "<!-- NewLine -->")}
    else 
        return
    end

end