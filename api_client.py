from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from apiclient.discovery import build
import os, sys, getopt, datetime, log, io, settings
from datetime import date, timedelta
from mimetypes import MimeTypes as mime
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

logger = log.getTimedLogger()
m = 0       # files found
n = 0       # files created
p = 0       # files downloaded

email_address = 'ENTER YOUR EMAIL HERE'
    
def syntax_display_msg():
    logger.info('syntax for read: python uploader.py -r [-d <dd/mm/yyyy>]')
    logger.info('syntax for save: python uploader.py -s -d <dd/mm/yyyy>')
    logger.info('syntax for upload: python uploader.py [-d <dd/mm/yyyy>]')
    logger.info('syntax for delete: python uploader.py --delete <file_id>')
    sys.exit(2)
    
def validate_date(datestring):
    try:
        logger.info('validating date \''+datestring+'\'')
        return datetime.datetime.strptime(datestring, '%d/%m/%Y').strftime("%Y\\%b\\%d")
    except ValueError:
        syntax_display_msg()
        
# returns 'mimetype:extension'
def get_mimetype(filename):
    try:
        # return mime().guess_type(filename)[0] + ':' + filename.split('.')[-1]
        return mime().guess_type(filename)[0]
    except Exception as e:
        logger.error('Exception: '+str(e))
        return None
        

def query_files(entered_date=None, extended_query=None, file_id=None):
    try:
        logger.info('making API request')
        query = "mimeType contains 'image'"
        
        if file_id:
            return {'files': [ drive_service.files().get(fileId=file_id).execute() ]}
        
        if entered_date:
            path = 'IDs\\'+entered_date
            logger.info('fetching files from \''+path+'\'...')
            # parents = create_folder_path(path.split('\\'))
            # query = "'"+parents[-1]+"' in parents"
            query = query + " AND fullText contains '"+path.replace('\\', '\\\\')+"'"
        else:
            logger.info('fetching files...')
        
        if extended_query:
            query = query + extended_query
        
        logger.info('query: "'+query+'"')
        return drive_service.files().list(q=query,
                                        spaces='drive',
                                        fields='files(id, name, description, mimeType)').execute()
    except Exception as e:
        logger.error('Exception: '+str(e))
        return {'files': []}

def read_files(entered_date):
    response = query_files(entered_date)
                                    
    logger.info(str(len(response['files']))+' FILES FOUND')
    logger.info('RESPONSE --> '+str(response))
    
def download_file(file, file_storage_dir):
    global p
    
    logger.info('DOWNLOADING FILE \''+file.get('name')+'\' (ID: '+file.get('id')+')')
    try:
        fh = io.FileIO(os.path.join(file_storage_dir, file.get('name')), 'wb')
        request = drive_service.files().get_media(fileId=file.get('id'))
        
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            # print("%d%% Downloaded." % int(status.progress()*100), end=" ")
            
        logger.info('FILE DOWNLOADED!!!')
        p = p+1
    except Exception as e:
        logger.error('Exception: '+str(e))
        logger.info('DOWNLOAD FAILED')
    
def save_files(entered_date):
    global p
    logger.info('checking files for the given date...')
    response = query_files(entered_date)
    logger.info(str(len(response['files']))+' FILES FOUND')
    
    if len(response['files']) > 0:
        logger.info('initiating download...')
        
        HOME_DIR = os.path.expanduser("~")
        DATE_DIR = datetime.datetime.strptime(entered_date, '%Y\\%b\\%d').strftime("%d-%b-%Y")
        file_storage_dir = os.path.join(HOME_DIR, 'Downloads\\Guest Ids\\'+DATE_DIR)
        
        if not os.path.exists(file_storage_dir):
            os.makedirs(file_storage_dir)
        
        for file in response['files']:
            download_file(file, file_storage_dir)
            
        logger.info(str(p)+'/'+str(len(response['files']))+' files downloaded')

def delete_file(file_id):
    try:
        logger.info('checking for the existence of file \''+file_id+'\'...')
        response = query_files(file_id=file_id)
        
        if len(response['files'])==0:
            logger.info('Please provide a valid FileID')
            return
            
        logger.info('File Exist')
        logger.info('deleting file \''+response['files'][0]['name']+'\' (File ID: '+file_id+')')
        drive_service.files().delete(fileId=file_id).execute()
        logger.info('FILE DELETED!!!')
    except Exception as e:
        logger.error('Exception: '+str(e))
        logger.info('FILE NOT DELETED!!!')
    
def search_folder(folder_name, parent_folder_id):
    logger.info('searching folder \''+folder_name+'\'... ')
    
    query = "mimeType='application/vnd.google-apps.folder' AND trashed=false AND name='"+folder_name+"' AND '"+parent_folder_id+"' in parents"
    response = drive_service.files().list(q=query,
                                        spaces='drive',
                                        fields='files(id, name)').execute()
                                        
    folder_list = response.get('files', None)
    
    if folder_list:
        logger.info('folder exist')
        return folder_list[0]
    else:
        logger.info('folder does not exist')
        return None
        
def create_folder(folder_name, parents_list=None):
    try:
        logger.info('creating folder \''+folder_name+'\'... ')
        
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': 'root' if not parents_list else parents_list
        }
        folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
        logger.info('Folder ID: '+folder.get('id'))
        share_file(folder.get('id'))
        return folder
    except Exception as e:
        logger.error('Exception: \'Folder not created\' - '+str(e))
        sys.exit(2)
        
def create_folder_path(folder_list):
    folder_path = ''
    for folder in folder_list:
        folder_path = folder_path + '/' + folder
        
    logger.info('creating folder path: \''+folder_path+'\'...')
    parents_list = []
    folder_obj = None
    
    for folder in folder_list:
        folder_obj = search_folder(folder, 'root' if not folder_obj else folder_obj.get('id'))
        if not folder_obj:
            folder_obj = create_folder(folder, parents_list)
        parents_list = []
        parents_list.append(folder_obj.get('id'))
        
    logger.info('PATH CREATION SUCCESSFUL')
    return parents_list
    
def create_file(upload_file_name, upload_file_path, parent_folder_path, upload_file_description=None):
    global n
    
    logger.info('CREATING FILE \''+upload_file_name+'\'...')
    parents = create_folder_path(parent_folder_path.split('\\'))
    
    if parents:
        # file_exist = True if len(query_files(parent_folder_path[4:], " AND '"+str(parents[-1])+"' in parents AND name = '"+upload_file_name+"'")['files']) > 0 else False
        file_exist = True if len(query_files(parent_folder_path[4:], " AND name = '"+upload_file_name+"'")['files']) > 0 else False
        
        if file_exist:
            logger.warning('FILE ALREADY EXIST!!!')
            return
        else:
            logger.info('UPLOADING FILE...')
            
        try:
            mime_type = get_mimetype(upload_file_name)
            
            if not mime_type:
                logger.error('could not determine mimetype of the file')
                
                user_help = input('do you wish to continue?(y/n): ')
                if user_help=='n' or user_help=='N':
                    sys.exit(2)
                else:
                    logger.info('proceeding...')
            
            file_obj = MediaFileUpload(upload_file_path, mimetype=mime_type, resumable=True)
            
            file_metadata = {
                            'name': upload_file_name,
                            'parents': parents,
                            'mimeType': mime_type,
                            'description': parent_folder_path+' - '+upload_file_description if upload_file_description else parent_folder_path
            }
            
            file = drive_service.files().create(media_body=file_obj, body=file_metadata, fields='id').execute()
            logger.info('file created successfully (ID: '+file.get('id')+')')
            n = n+1
            share_file(file.get('id'))
        except Exception as e:
            logger.error('Exception: '+str(e))
            logger.info('file creation failed!!!')
    
def callback(request_id, response, exception):
    if exception:
        # Handle error
        logger.error('Excepton: '+str(exception))
        logger.info('file not shared!!!')
    else:
        logger.info('Permission Id: '+response.get('id'))
    
def share_file(file_id):
    logger.info('sharing file...')
    batch = drive_service.new_batch_http_request(callback=callback)
    
    user_permission = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': email_address
    }
    batch.add(drive_service.permissions().create(
            fileId=file_id,
            body=user_permission,
            fields='id',
    ))
    
    # domain_permission = {
        # 'type': 'domain',
        # 'role': 'reader',
        # 'domain': 'example.com'
    # }
    # batch.add(drive_service.permissions().create(
            # fileId=file_id,
            # body=domain_permission,
            # fields='id',
    # ))
    
    batch.execute()
    
def upload_files(entered_date):
    # today = datetime.datetime.now().strftime("%d/%b/%Y").split("-")                           # ['date', 'month', 'year']
    global m
    global n
    iteration = 1
    
    # yesterday = (date.today()-timedelta(days=1)).strftime("%Y\\%b\\%d")                # ['date', 'month', 'year']
    today = (date.today()).strftime("%Y\\%b\\%d")                                      # ['date', 'month', 'year']
    
    if not entered_date:
        entered_date = today
    
    for root, subdirs, files in os.walk("IDs\\", topdown=True):
        for name in files:
            m = m+1
            file = os.path.join(root, name)
            logger.info(''+str(m)+'. file: '+file)
            
            if iteration==1:
                create_file(file.split('\\')[-1], file, root+entered_date)
            else:
                path_list = file.split('\\')
                path_list.pop()
                create_file(file.split('\\')[-1], file, '\\'.join(path_list))
        # for name in subdirs:
            # folder = os.path.join(root, name)
            # logger.info('folder: '+folder)
            
        iteration = iteration+1
        
    if m==0:
        logger.info('NO FILES FOUND TO UPLOAD!!!')
            
    logger.info('TOTAL FILES FOUND: '+str(m))
    logger.info('TOTAL FILES CREATED: '+str(n))
    
if __name__ == '__main__':
    logger.info('---------------------------------------------------------------------------------------------------')

    logger.info('setting scope...')
    scopes = ['https://www.googleapis.com/auth/drive']

    logger.info('initialising credentials object')
    credentials = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(settings.BASE_DIR, 'Extras/client_secret.json'), scopes)

    logger.info('applying necessary credential headers for authorizing request')
    http_auth = credentials.authorize(Http())

    logger.info('initialising service object...')
    drive_service = build('drive', 'v3', http=http_auth)
    
    entered_date = None
    fileId_for_deletion = None
    operation = None
    
    try:
      opts, args = getopt.getopt(sys.argv[1:], "hd:rus", ["date=", "read", "upload", "save", "download", "delete="])
    except getopt.GetoptError:
        syntax_display_msg()
    except Exception:
        pass
    for opt, arg in opts:
        if opt == '-h':
            syntax_display_msg()
        elif opt in ("-d", "--date"):
            entered_date = validate_date(arg)
            logger.info('using date \''+entered_date+'\'')
        elif opt in ("-r", "--read"):
            operation = "read"
        elif opt in ("-u", "--upload"):
            operation = "upload"
        elif opt in ("-s", "--save", "--download"):
            operation = "save"
        elif opt in ("--delete"):
            operation = "delete"
            fileId_for_deletion = arg
            
    if not operation:
        syntax_display_msg()
         
    if operation=="read":
        if not entered_date:
            syntax_display_msg()
            
        logger.info('OPERATION: READ (starting...)')
        read_files(entered_date)
    elif operation=="upload":
        logger.info('OPERATION: UPLOAD (starting...)')
        upload_files(entered_date)
    elif operation=="save":
        if not entered_date:
            syntax_display_msg()
            
        logger.info('OPERATION: SAVE (starting...)')
        save_files(entered_date)
    elif operation=="delete":
        logger.info('OPERATION: DELETE (starting...)')
        delete_file(fileId_for_deletion)