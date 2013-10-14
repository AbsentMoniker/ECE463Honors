from google.appengine.api import users

def index():
    user = users.get_current_user()
    if user:
        quizzes = db(db.quiz.author_id==user.user_id()).select(db.quiz.name)
        return dict(quizzes=quizzes)
    else:
        redirect(users.create_login_url('/quizzes'))
        
def create():
    form=FORM('Quiz Name:',
              INPUT(_name='name', requires=IS_NOT_EMPTY()),
              INPUT(_type='submit'))
    if form.process().accepted:
        db.quiz.insert(name=request.vars.name,author_id=users.get_current_user().user_id())
        redirect('/QuizMe/quizzes')
    return form

def show():
    quiz = db(db.quiz.id==request.get_vars['id']).select()[0]
    if quiz.author_id != users.get_current_user().user_id():
        redirect('/QuizMe/quizzes')
    return dict(quiz=quiz)
