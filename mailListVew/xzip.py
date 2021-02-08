import zipfile,tarfile,rarfile,gzip,py7zr,lzma,shutil
from py7zr import pack_7zarchive, unpack_7zarchive
import os
# register file format at first.
shutil.register_archive_format('7zip', pack_7zarchive, description='7zip archive')
shutil.register_unpack_format('7zip', ['.7z'], unpack_7zarchive)

# extraction
# compression
def rm_file_or_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


def un_zip(file_name,xurl):
    print(file_name)
    z = zipfile.ZipFile(file_name, 'r')
    z.extractall(path=xurl)
    z.close()

def un_tar(file_name,xurl):
    t=tarfile.open(file_name,'r')
    t.extractall(xurl)
    t.close()
# gz如果提示"tarfile.ReadError: not a gzip file"将"r:gz" 改为"r"
def un_gz(file_name,xurl):
    try:
        tar = tarfile.open(file_name, "r:gz")
        file_names = tar.getnames()
        for file_name in file_names:
            tar.extract(file_name, xurl)
        tar.close()
    except Exception as e:
        raise e
def un_rar(file_name,xurl):
    rf = rarfile.RarFile(file_name)# 待解压文件
    rf.extractall(xurl)
    rf.close()
def b_7z(file_name,burl):
    with py7zr.SevenZipFile(file_name, 'w') as z:
        z.writeall(burl,'base')
def b_7z_dir(dir_name,burl):
    shutil.make_archive(burl, '7zip',dir_name )
def un_7z(file_name,burl):
    with py7zr.SevenZipFile(file_name, mode='r') as z:
        z.extractall(burl)

def un_xz(file_name,xurl):
    os.popen('xz -d '+file_name)
    print(file_name.replace(".xz",''))
    os.popen("tar -xvf "+file_name)

# un_zip("/home/sdzw/PycharmProjects/mail163_django/static/email_data/Email_download/罗云超/2020-12-22_13:49:23/chromedriver_linux64-1.zip","/home/sdzw/PycharmProjects/mail163_django/static/email_data/Email_download/罗云超/2020-12-22_13:49:23/chromedriver_linux64-1")


