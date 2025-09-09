def extract_images(content):
    import re
    import logging
    logger = logging.getLogger(__name__)
    
    images_list = []
    try:
        x = re.findall(r"\<img\s+.*?\>", content)
        if len(x) == 0:
            return content, images_list
        for image in x:
            images_list.append(image)

        for index, image in enumerate(images_list):
            val = re.escape(image)
            x = re.sub(val, "<<<<"+ str(index) +">>>>" , content)
            content = x
        return content, images_list
    except Exception as e:
        raise ImageExtractError(e)
    

class ImageExtractError(Exception):
    def __init__(self, reason, message=""):
        self.reason = reason
        self.message = message

    def __str__(self):
        return f'{self.message} -> {self.reason}'