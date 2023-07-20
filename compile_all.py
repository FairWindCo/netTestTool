import subprocess


def compile_file(file_path):
    subprocess.run(['pyinstaller', '--noconfirm', '--onefile', '--console', '--clean', '--distpath', 'output',
                    file_path])


if __name__ == "__main__":
    list_compile = [
        'ping/os_ping.py',
        'ping/os_ping_multi.py',
        'check_url/url_test.py',
        'check_url/multi_url_test.py',
        'check_url/special_multi_url_test.py',
        'check_url/www01_multi_url_test.py'
    ]
    for compile in list_compile:
        compile_file(compile)
