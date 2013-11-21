from google.appengine.api import users

def set_mode():
    print "setting mode to: %s"%request.vars.mode
    session.mode = request.vars.mode
    return "submit();"

def checkpass():
    quiz = db(db.quiz.id==int(request.vars.quiz)).select()[0]
    if quiz.password == request.vars["%d"%quiz.id]:
        redirect(URL('quizzes','take',vars={'id':quiz.id,'q':1}, extension="html"), client_side=True)
        return
    else:
        return "jQuery('.flash').html('Password Incorrect').slideDown()"
def index():
    return dict()

def home():
    url = URL('default', 'user')
    if request.vars.mode:
        session.mode = request.vars.mode
    currentMode = request.vars.mode if request.vars.mode else session.mode
    if currentMode == "professor":
        redirect(URL("quizzes","index", extension="html"), client_side=True)
    user = users.get_current_user()
    subscriptions=[]
    form = FORM(INPUT(_name="newsubscription", _placeholder="Enter professor e-mail address...",requres=IS_NOT_EMPTY()),INPUT(_value="Add Subscription", _type="submit"))
    
    if form.process().accepted:
        newUser = db(db.auth_user.email==request.vars.newsubscription).select()
        if newUser:
            newList = auth.user.subscriptions
            newList.append(newUser[0].id)
            db(db.auth_user.id==auth.user_id).update(subscriptions=newList)
            response.flash=T("Professor added!")
        else:
            response.flash=T("ERROR - Professor not found")
    if auth.user:
        for subscription in auth.user.subscriptions:
            sub = db(db.auth_user.id==subscription).select()[0]
            quizzes = db(db.quiz.author_id==sub.id).select()
            activeQuizzes = []
            for quiz in quizzes:
                #activeQuizzes.append(quiz)
                if quiz.active:
                    activeQuizzes.append((quiz, quiz.password!=None))
            subscriptions.append([sub.first_name, activeQuizzes])
    else:
        subscriptions=None
    return dict(user=user, url=url, subscriptions=subscriptions, form=form, mode=request.vars.mode)

def user():
    return dict(form=auth())

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
