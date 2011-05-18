from retrace import *

def application(environ, start_response):
    request = Request(environ)

    try:
        _ = gettext.translation(GETTEXT_DOMAIN, languages=["%s" % request.accept_language],
                                codeset="%s" % request.accept_charset).gettext
    except:
        _ = lambda x: x

    match = URL_PARSER.match(request.script_name)
    if not match:
        return response(start_response, "404 Not Found",
                        _("Invalid URL"))

    taskdir = "%s/%s" % (CONFIG["SaveDir"], match.group(1))

    if not os.path.isdir(taskdir):
        return response(start_response, "404 Not Found",
                        _("There is no such task"))

    pwdpath = "%s/password" % taskdir
    try:
        pwdfile = open(pwdpath, "r")
        pwd = pwdfile.read()
        pwdfile.close()
    except:
        return response(start_response, "500 Internal Server Error",
                        _("Unable to verify password"))

    if not "X-Task-Password" in request.headers or \
       request.headers["X-Task-Password"] != pwd:
        return response(start_response, "403 Forbidden",
                        _("Invalid password"))

    status = "PENDING"
    if os.path.isfile("%s/retrace_log" % taskdir):
        if os.path.isfile("%s/retrace_backtrace" % taskdir):
            status = "FINISHED_SUCCESS"
        else:
            status = "FINISHED_FAILURE"

    statusmsg = status
    try:
        statusfile = open("%s/status" % taskdir, "r")
        statusmsg = _(STATUS[int(statusfile.read())])
        statusfile.close()
    except:
        pass

    return response(start_response, "200 OK",
                    statusmsg, [("X-Task-Status", status)])