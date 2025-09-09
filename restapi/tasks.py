from celery import shared_task
from celery.utils.log import get_task_logger

loggercelery = get_task_logger(__name__)
import re 

from .logging.logging_adapter import FilenameLoggingAdapter
from .logging.ErrorTypes import (WRInlineStructureError, WREndStructureError, MSInlineStructureError, MSEndStructureError, ORDInlineStructureError, ORDEndStructureError, MCInlineStructureError, MCEndStructureError, TFInlineStructureError, TFEndStructureError, FIBInlineStructureError, FIBEndStructureError, MATInlineStructureError, MATEndStructureError, InlineNoTypeError, EndAnswerNoTypeError, NoTypeDeterminedError, MarkDownConversionError)
from .logging.WarningTypes import (RespondusTypeEWarning, RespondusTypeMRWarning, RespondusTypeFMBWarning, RespondusTypeMTWarning)

@shared_task()
def run_pandoc_task(temp_file_path, filename):
    logger = FilenameLoggingAdapter(loggercelery, {
        'filename': filename
        })
    
    try:
        import pypandoc
        mdblockquotePath = "./pandoc/pandoc-filters/mdblockquote.lua"
        emptyparaPath = "./pandoc/pandoc-filters/emptypara.lua"
        imageFilterPath = "./pandoc/pandoc-filters/image.lua"
        tables = "./pandoc/pandoc-filters/tables.lua"
        # listsPath = "./api/pandoc/pandoc-filters/lists.lua"

        pandoc_word_to_html = pypandoc.convert_file(
            temp_file_path,
            format='docx+empty_paragraphs',
            to='html+empty_paragraphs+tex_math_single_backslash',
            extra_args=['--no-highlight',
            '--embed-resources',
            '--markdown-headings=atx',
            '--preserve-tabs',
            '--wrap=preserve',
            '--indent=false',
            '--mathml',
            '--ascii',
            # '--lua-filter=' + imageFilterPath
            ])
        pandoc_word_to_html = re.sub(r"(?!\s)<math>", " <math>", pandoc_word_to_html)
        pandoc_word_to_html = re.sub(r"</math>(?!\s)", "</math> ", pandoc_word_to_html)
        pandoc_html_to_md = pypandoc.convert_text(
            pandoc_word_to_html,
            'markdown_github+fancy_lists+emoji+hard_line_breaks+all_symbols_escapable+escaped_line_breaks+pipe_tables+startnum+tex_math_dollars',
            format='html+empty_paragraphs',
            extra_args=['--no-highlight', 
                        '--embed-resources',
                        '--markdown-headings=atx', 
                        '--preserve-tabs', 
                        '--wrap=preserve', 
                        '--indent=false', 
                        '--mathml', 
                        '--ascii',
                        '--lua-filter=' + mdblockquotePath, 
                        '--lua-filter=' + emptyparaPath,
                        # '--lua-filter=' + tables
                        ])
        pandoc_html_to_md = pandoc_html_to_md.rstrip()
        return "\n" + pandoc_html_to_md + "\n"
    except Exception as e:
        logger.debug(e)
        raise MarkDownConversionError(e)
    
