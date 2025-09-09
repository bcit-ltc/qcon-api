def convert_txt(original_file_path, actual_filename):
    import os
    import subprocess
    import uuid
    from pathlib import Path
    import glob
    import shutil
    txt_file_uuid =  uuid.uuid4()
    txt_lines = ""

    try:
        Path("/code/temp").mkdir(parents=True, exist_ok=True)
        os.chdir('/code/temp')

        subprocess.run(["soffice", 
                        "--headless", 
                        "--convert-to", 
                        "txt", 
                        "--outdir", 
                        str(txt_file_uuid), 
                        original_file_path], 
                        capture_output=True)
     
        txt_file_path = glob.glob(f"/code/temp/{str(txt_file_uuid)}/*.txt")[0]
        text_file = Path(str(txt_file_path))
        if text_file.is_file():
            f = open(txt_file_path , mode='r', encoding='utf-8-sig')
            lines = f.read()
            txt_lines = '\n' + lines
            f.close()  
        shutil.rmtree("/code/temp/"+str(txt_file_uuid), ignore_errors=True)
        return txt_lines
    except Exception as e:
        raise ConvertTxtError(e)
    
    
class ConvertTxtError(Exception):
    def __init__(self, reason, message="ConvertTxtError"):
        self.reason = reason
        self.message = message
    def __str__(self):
        return f'{self.message} -> {self.reason}'