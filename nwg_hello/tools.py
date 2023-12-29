import json
import os
import subprocess
import sys


def temp_dir():
    if os.getenv("TMPDIR"):
        return os.getenv("TMPDIR")
    elif os.getenv("TEMP"):
        return os.getenv("TEMP")
    elif os.getenv("TMP"):
        return os.getenv("TMP")
    return "/tmp"


def eprint(*args, log=False):
    print(*args, file=sys.stderr)
    # we don't log testing sessions
    if log and os.getenv("USER") == "greeter":
        log_file = os.path.join(temp_dir(), 'nwg-hello.log')
        with open(log_file, 'a') as f:
            print(*args, file=f)


def list_users():
    uid_min = None
    with open('/etc/login.defs') as loglist:
        for line in loglist.readlines():
            if line.startswith('UID_MIN'):
                uid_min = int(line.split(' ')[1])
    users = []
    for i in os.listdir('/home'):
        try:
            # ask pam about users
            user = subprocess.check_output(['getent', 'passwd', i]).decode('ascii').strip()
        except subprocess.SubprocessError:
            # skip nonexistent users
            continue
        user = user.split(':')
        if int(user[2]) >= uid_min:
            users.append(user[0])
    return users


def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        eprint(f"* error loading json: {e}")
        return {}


def save_json(src_dict, path, en_ascii=True, log=False):
    try:
        with open(path, 'w') as f:
            json.dump(src_dict, f, indent=2, ensure_ascii=en_ascii)
            eprint(f"Saved json to: '{src_dict}'", log=log)
    except Exception as e:
        eprint(f"Error saving json: '{f}'", log=log)


def load_text_file(path):
    try:
        with open(path, 'r') as file:
            data = file.read()
            return data
    except Exception as e:
        eprint(e)
        return None


def list_sessions(session_dirs):
    _sessions = []
    _x_sessions = []
    for session_dir in session_dirs:
        if os.path.isdir(session_dir):
            for file_name in sorted(os.listdir(session_dir)):
                p = os.path.join(session_dir, file_name)
                if p.endswith('.desktop'):
                    session = parse_desktop_entry(p)
                    if session:
                        _sessions.append(session)
                        if session_dir == "/usr/share/xsessions":
                            _x_sessions.append(session["exec"])
    return _sessions, _x_sessions


def launch(self, cmd, log=False):
    eprint("Executing cmd: '{}'".format(cmd), log=log)
    # Alright, I know. But subprocess sucks with systemd.
    eprint(os.popen(cmd).read(), log=log)


def parse_desktop_entry(path):
    paths = os.getenv('PATH').split(":")
    session = {}
    lines = load_text_file(path).splitlines()
    if lines:
        for line in lines:
            if line.startswith('Name'):
                session['name'] = line.split("=")[1]
                continue
            if line.startswith('Exec'):
                session['exec'] = line.split("=")[1]
                continue
            if line.startswith('TryExec'):
                session['try-exec'] = line.split("=")[1]
                continue
        if 'try-exec' in session:
            if os.path.isfile(session['try-exec']):
                return session
            else:
                for p in paths:
                    if os.path.isfile(os.path.join(p, session['try-exec'])):
                        return session
        else:
            return session
    else:
        return None


def greetd(client, json_req, log=False):
    eprint(f"greetd: request = {json_req}", log=log)
    req = json.dumps(json_req)
    client.send(len(req).to_bytes(4, "little") + req.encode("utf-8"))
    resp_raw = client.recv(128)
    resp_len = int.from_bytes(resp_raw[0:4], "little")
    resp_trimmed = resp_raw[4:resp_len + 4].decode()
    try:
        r = json.loads(resp_trimmed)
        eprint(f"greetd: response = {r}", log=log)
        return r
    except ValueError:
        eprint(f"greetd: ValueError")
        return {}
