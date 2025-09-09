import pypandoc

def convert(path_to_file):

    try:
        mdblockquotePath = "./api/pandoc/pandoc-filters/mdblockquote.lua"
        pandocstring = pypandoc.convert_file(
            path_to_file,
            format='docx',
            to=
            'markdown_github+fancy_lists+emoji+hard_line_breaks+all_symbols_escapable+escaped_line_breaks+grid_tables+startnum',
            extra_args=[
                '--extract-media=' + self.folder_path, '--no-highlight',
                '--self-contained', '--atx-headers', '--preserve-tabs',
                '--wrap=preserve', '--indent=false', '--lua-filter=' + mdblockquotePath
            ])

        return pandocstring
    except:
        pass