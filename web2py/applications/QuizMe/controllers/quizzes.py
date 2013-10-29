from google.appengine.api import users

def index():
    stopped = None
    if auth.is_logged_in():
        if 'stop' in request.args:
            db(db.quiz.id==request.get_vars['id']).update(active=False)
            stopped=int(request.get_vars['id'])
        quizzes = db(db.quiz.author_id==auth.user.id).select(db.quiz.name)
        return dict(quizzes=quizzes,stopped=stopped)
    else:
        redirect(URL('default','user'))
        
def create():
    form=FORM('Quiz Name:',
              INPUT(_name='name', requires=IS_NOT_EMPTY()),
              INPUT(_value="Add Question", _type="submit")
              )
    if form.process().accepted:
        quizId = db.quiz.insert(name=request.vars.name,author_id=auth.user.id)
        redirect(URL('quizzes','addquestion', vars={"id":quizId}))
    return dict(form=form)

def addquestion():
    form=FORM('Question:',
              INPUT(_name='question', requires=IS_NOT_EMPTY()),BR(),
              'Answers:',BR(),
              INPUT(_name='answer1', requres=IS_NOT_EMPTY()),BR(),
              INPUT(_name='answer2', requires=IS_NOT_EMPTY()),BR(),
              INPUT(_name='answer3', requires=IS_NOT_EMPTY()),BR(),
              INPUT(_name='answer4', requires=IS_NOT_EMPTY()),BR(),
              INPUT(_name='answer5', requires=IS_NOT_EMPTY()),BR(),
              INPUT(_value="Add Question", _name="questionAdd", _type="submit"),
              INPUT(_value="Done Creating Quiz", _name="quizSubmit", _type="submit")
              )
    quiz = False
    while not quiz:
        quiz = db(db.quiz.id == request.vars.id).select()
        if quiz:
            questions = quiz[0].questions
            if form.process().accepted:
                answers = [request.vars.answer1, request.vars.answer2,
                           request.vars.answer3, request.vars.answer4,
                           request.vars.answer5]
                questionId = db.question.insert(question=request.vars.question,
                                                answers=answers,
                                                correct = 0)
                questions.append(questionId)
                db(db.quiz.id == request.vars.id).update(questions=questions)
    if (request.vars.quizSubmit):
        redirect(URL('quizzes','index'))
    return dict(form=form, qnum=len(questions)+1, name=quiz[0].name)

def show():
    quiz = db(db.quiz.id==request.get_vars['id']).select()[0]
    if quiz.author_id != auth.user.id:
        redirect('/QuizMe/quizzes')
    questions = []
    for i in xrange(len(quiz.questions)):
        questions.append(db(db.question.id == quiz.questions[i]).select()[0])
    return dict(quiz=quiz, questions=questions)

def take():
    quiz = db(db.quiz.id==request.get_vars['id']).select()[0]
    activeQ = db(db.question.id==quiz.questions[int(request.get_vars['q'])-1]).select()[0]
    status = ""
    val=request.vars
    userid = auth.user.id
    results=[]
    if userid == quiz.author_id:
        owner = True
        if not quiz.active:
            db(db.quiz.id==request.get_vars['id']).update(active=True)

        if request.vars.start:
            activeQ.update_record(active=True)
            activeQ.update_record(guesses=[])
            activeQ.update_record(guess_owners=[])
        if request.vars.stop:
            activeQ.update_record(active=False)
            for i in xrange(5):
                results.append(activeQ.guesses.count(i))
    else:
        owner = False
        if not quiz.active:
            redirect(URL('default','index'))
        if request.vars.submitAnswer:
            if activeQ.active:
                newguesses = activeQ.guesses
                if userid in activeQ.guess_owners:
                    ind = activeQ.guess_owners.index(userid)
                    newguesses[ind]=int(request.vars.answer)
                    activeQ.update_record(guesses=newguesses)
                else:
                    newguessowners = activeQ.guess_owners
                    newguessowners.append(userid)
                    newguesses.append(int(request.vars.answer))
                    activeQ.update_record(guesses=newguesses)
                    activeQ.update_record(guess_owners=newguessowners)
                    
                response.flash=T("Answer submitted!")
            else:
                response.flash=T("Answer not submitted - quiz not active")
    return dict(quiz=quiz, question = activeQ, qnum=request.get_vars['q'], owner=owner, results=results, val=activeQ.guesses, val2=activeQ.active)
