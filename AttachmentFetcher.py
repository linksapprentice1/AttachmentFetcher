from email.utils import parsedate
import poplib
import email
import mimetypes
import bisect
import os
import subprocess

def getAttachments(service, username, password, start_date, end_date, file_type):
    conn = _connect(service)
    _login(conn, service, username, password)
    attachments = _retrieveAttachments(conn, start_date, end_date, file_type)
    _saveAttachments(attachments)
    _openDir("Attachments")

def _connect(service):
    try:
        return poplib.POP3_SSL('pop.' + service + '.com', 995)
    except:
        return poplib.POP3_SSL('pop.mail.' + service + '.com', 995)

def _login(conn, service, username, password):
    conn.user(username)
    conn.pass_(password)

def _retrieveAttachments(conn, start_date, end_date, file_type):
    for message in _messagesByDate(conn, start_date, end_date):
        for attachment in _attachmentsByFileType(message, file_type):
            yield attachment

def _fileTypeMatches(data, file_type):
    filename, content_type = data.get_filename(), data.get_content_type() 
    extensions = mimetypes.guess_all_extensions(content_type, strict = False)
    return (content_type and file_type in content_type.lower()) or \
       (filename and file_type in filename.lower()) or \
       any(file_type in extension.lower() for extension in extensions)  

def _attachmentsByFileType(message, file_type):
    for data in message.walk():
        if _fileTypeMatches(data, file_type):
            yield data

def _getMessage(conn, index):
    return email.message_from_string("\n".join(conn.retr(index)[1]))

def  _messagesByDate(conn, start_date, end_date):
    newest_index = len(conn.list()[1])

    class Message_Date(object):
        def __getitem__(self, index):
            return email.utils.parsedate(_getMessage(conn, index)["date"])

    end_index = bisect.bisect_right(Message_Date(), end_date, 1, newest_index)
    start_index = bisect.bisect_left(Message_Date(), start_date, 1, end_index)

    return (_getMessage(conn, index) for index in xrange(start_index, end_index))

def _mkdir(the_dir):
    if not os.path.exists(the_dir):
        os.makedirs(the_dir)

def _attachmentData(attachment):
    return attachment.get_content_type(), attachment.get_filename(), attachment.get_payload(decode = 1)

def _saveAttachments(attachments):
    for attachment in attachments:
        file_type, file_name, payload = _attachmentData(attachment)
        _mkdir("Attachments")
        _mkdir("Attachments/" + file_type)
        file_path = "Attachments/" + file_type + "/" + file_name
        print "Now saving " + os.getcwd() + file_path 
        with open(file_path, "w") as f:
            f.write(payload)
    print "Done"

def _openDir(dir_name):
    _mkdir("Attachments")
    subprocess.Popen(["explorer" if os.name == "nt" else "nautilus", dir_name])
    
    


