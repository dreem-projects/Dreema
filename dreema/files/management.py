import os, shutil
from responses import SysCodes, SysMessages
from helpers import Json

"""File utilities for Dreema.

    This module provides helpers for managing file uploads through request body 
    and controllers
"""


class FileManagement:
    """Manage temporary uploaded files and move them into persistent storage."""

    def save(self, fullPath: str, destination: str, newfilename: str = None):
        """Move a temporary file to a destination directory.

        Args:
            fullPath (str): source path of the temporary file.
            destination (str): target directory path.
            newfilename (str, optional): override file name at the destination.

        Returns:
            Json: operation result with file metadata on success.
        """
        # checking file existence
        if not os.path.exists(fullPath):
            return Json(
                {
                    "data": None,
                    "status": SysCodes.FILE_NOT_EXISTS,
                    "message": SysMessages.FILE_NOT_EXISTS,
                }
            )
         
        #create directory if it does not exist   
        os.makedirs(destination,exist_ok=True)
        filename = newfilename if newfilename else os.path.basename(fullPath)
        path = os.path.join(destination,filename)
        
        #move the file
        shutil.move(fullPath,path)
        
        if not os.path.exists(path):
            return Json(
                {
                    "data": None,
                    "status": SysCodes.FILE_UPLOAD_FAILED,
                    "message": SysMessages.FILE_UPLOAD_FAILED,
                }
            )
        
        return Json(
                {
                    "data": {
                        'size':os.path.getsize(path),
                        'fullpath':path
                    },
                    "status": SysCodes.FILE_UPLOAD_SUCCESS,
                    "message": SysMessages.FILE_UPLOAD_SUCCESS,
                }
            )    

       
    async def delete(self, fullpath:str):
        """Delete a file from disk.

        Args:
            fullpath (str): path to the file to remove.

        Returns:
            Json: operation result indicating success or failure.
        """
        if not os.path.exists(fullpath):
            return Json(
                {
                    "data": None,
                    "status": SysCodes.FILE_NOT_EXISTS,
                    "message": SysMessages.FILE_NOT_EXISTS,
                }
            )
        try:
            os.remove(fullpath)
            return Json(
                {
                    "data": None,
                    "status": SysCodes.OP_SUCCESS,
                    "message": SysMessages.OP_SUCCESS,
                }
            )
        except Exception as e:
             return Json(
                {
                    "data": None,
                    "status": SysCodes.OP_FAILED,
                    "message": f'{SysMessages.OP_FAILED} - {e}',
                    
                }
            )
            
        