def restore_images(content, images_list):
    import re
    import logging
    logger = logging.getLogger(__name__)
    
    # This is to conditionally replace every match with the image at the index of the images_list
    try:
        if content is None:
            return None
        def replTxt(match):        
            x = re.search(r"\d+", match.group())
            if int(x.group()) < len(images_list):
                return images_list[int(x.group())]
        a = re.compile(r"(\<\<\<\<\d+\>\>\>\>)")
        result = a.sub(replTxt, content)
        return result
    except Exception as e:
        raise ImageRestoreError(e)

class ImageRestoreError(Exception):
    def __init__(self, reason, message=""):
        self.reason = reason
        self.message = message

    def __str__(self):
        return f'{self.message} -> {self.reason}'