import os
import logging 

class QuestionlibraryFilenameFilter(logging.Filter):
    def __init__(self, questionlibrary=None):
        self.questionlibrary = questionlibrary        
    def filter(self, record):        
        if self.questionlibrary==None:
            # record.file = '--'
            pass
        else:
            if self.questionlibrary.temp_file.name != None:
                # record.file = 'docx_filename:' + os.path.basename(self.questionlibrary.temp_file.name)
                # filename = 'docx_filename:' + os.path.basename(self.questionlibrary.temp_file.name)
                filename = 'docx_filename:' + self.questionlibrary.temp_file.name
                record.msg = filename + " >>> " + str(record.getMessage())
            elif self.questionlibrary.filtered_main_title != None:
                # record.file = 'filtered_main_title:' + os.path.basename(self.questionlibrary.filtered_main_title)   
                titlename = 'filtered_main_title:' + os.path.basename(self.questionlibrary.filtered_main_title)      
                record.msg = titlename + " >>> " + str(record.getMessage())  
            else:
                # record.file = '--'
                pass
        return True
        
