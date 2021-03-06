from google.appengine.api import users
from google.appengine.ext import db as googledb
from google.appengine.api.labs import taskqueue

@auth.requires_login()
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

@auth.requires_login()
def create():
    form=FORM('Quiz Name:',
              INPUT(_name='name', requires=IS_NOT_EMPTY()),BR(),'Password:',
              INPUT(_name='password'),
              INPUT(_value="Add Question", _type="submit")
              )
    if form.process().accepted:
        quizId = db.quiz.insert(name=request.vars.name,author_id=auth.user.id, password=request.vars.password)
        redirect(URL('quizzes','addquestion', vars={"id":quizId, 'qnum':1}))
    return dict(form=form)

@auth.requires_login()
def addquestion():
    if 'edit' in request.args:
        form=FORM('Question:',
                  INPUT(_name='question', requires=IS_NOT_EMPTY()),BR(),
                  'Answers:',BR(),
                  INPUT(_name='answer1', requres=IS_NOT_EMPTY()),BR(),
                  INPUT(_name='answer2', requires=IS_NOT_EMPTY()),BR(),
                  INPUT(_name='answer3', requires=IS_NOT_EMPTY()),BR(),
                  INPUT(_name='answer4', requires=IS_NOT_EMPTY()),BR(),
                  INPUT(_name='answer5', requires=IS_NOT_EMPTY()),BR(),
                  INPUT(_value="Add Question", _name="questionAdd", _type="submit"),
                  )
        qnum = int(request.vars.qnum)
        quiz = False
        while not quiz:
            quiz = db(db.quiz.id == request.vars.id).select()
            if quiz:
                questions = quiz[0].questions
                if form.process().accepted:
                    print "Got here!"
                    answers = [request.vars.answer1, request.vars.answer2,
                               request.vars.answer3, request.vars.answer4,
                               request.vars.answer5]
                    print request.vars.question
                    print answers
                    questionId = db.question.insert(question=request.vars.question,
                                                    answers=answers,
                                                    correct = 0)
                    questions.insert(int(request.vars.qnum)-1,questionId)
                    db(db.quiz.id == request.vars.id).update(questions=questions)
                    redirect(URL('quizzes','editquestion',vars={'quiz':request.vars.id, 'qnum':request.vars.qnum}))
        if (request.vars.quizSubmit):
            redirect(URL('quizzes','index'))
    else:
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
        qnum = len(questions)+1
        if (request.vars.quizSubmit):
            redirect(URL('quizzes','index'))
    return dict(form=form, qnum=qnum, name=quiz[0].name)

@auth.requires_login()
def editquestion():
    quiz = db(db.quiz.id==request.vars.quiz).select()[0]
    if quiz.author_id != auth.user.id:
        redirect('/QuizMe/quizzes')
    question = db(db.question.id == quiz.questions[int(request.vars.qnum)-1]).select()[0]
    if request.vars.questionEdit:
        form = FORM('Question:',
                  INPUT(_name='question', _value=request.vars.question, requires=IS_NOT_EMPTY()),BR(),
                  'Answers:',BR(),
                  INPUT(_name='answer0', _value = request.vars.answer0, requres=IS_NOT_EMPTY()),BR(),
                  INPUT(_name='answer1', _value = request.vars.answer1, requires=IS_NOT_EMPTY()),BR(),
                  INPUT(_name='answer2', _value = request.vars.answer2, requires=IS_NOT_EMPTY()),BR(),
                  INPUT(_name='answer3', _value = request.vars.answer3, requires=IS_NOT_EMPTY()),BR(),
                  INPUT(_name='answer4', _value = request.vars.answer4, requires=IS_NOT_EMPTY()),BR(),
                  INPUT(_value="Save Changes", _name="questionEdit", _type="submit"),
                  )
    else:
        form = FORM('Question:',
                  INPUT(_name='question', _value=question.question, requires=IS_NOT_EMPTY()),BR(),
                  'Answers:',BR(),
                  INPUT(_name='answer0', _value = question.answers[0], requres=IS_NOT_EMPTY()),BR(),
                  INPUT(_name='answer1', _value = question.answers[1], requires=IS_NOT_EMPTY()),BR(),
                  INPUT(_name='answer2', _value = question.answers[2], requires=IS_NOT_EMPTY()),BR(),
                  INPUT(_name='answer3', _value = question.answers[3], requires=IS_NOT_EMPTY()),BR(),
                  INPUT(_name='answer4', _value = question.answers[4], requires=IS_NOT_EMPTY()),BR(),
                  INPUT(_value="Save Changes", _name="questionEdit", _type="submit"),
                  )
    if request.vars.questionDelete:
        deleteQuestion(quiz, int(request.vars.qnum))
        session.flash = "Question deleted"
        if int(request.vars.qnum) == 1:
            redirect(URL('quizzes', 'editquestion', vars={'quiz':request.vars.quiz, 'qnum':int(request.vars.qnum)}))
        else:
            redirect(URL('quizzes', 'editquestion', vars={'quiz':request.vars.quiz, 'qnum':int(request.vars.qnum)-1}))
    result =  form.process().accepted
    if request.vars.questionEdit and result:
        print "New question: %s"%request.vars.question
        db(db.question.id == quiz.questions[int(request.vars.qnum)-1]).update(question=request.vars.question)
        newAnswers = [request.vars.answer0, request.vars.answer1,
                           request.vars.answer2, request.vars.answer3,
                           request.vars.answer4]
        db(db.question.id == quiz.questions[int(request.vars.qnum)-1]).update(answers = newAnswers)
    nextButton = None
    prevButton = None
    deleteButton = None
    
    insertButtonBefore = A("Add New Question Before", _href=URL('quizzes','addquestion',vars={'id':request.vars.quiz, 'qnum':int(request.vars.qnum)},args=['edit']), _class="btn")
    insertButtonAfter = A("Add New Question After", _href=URL('quizzes','addquestion',vars={'id':request.vars.quiz, 'qnum':int(request.vars.qnum)+1},args=['edit']), _class="btn")
    if len(quiz.questions) > 1:
        deleteButton = FORM(INPUT(_value="Delete",_type="submit", _class="btn",_name="questionDelete"))
    if int(request.vars.qnum) > 1:
        prevButton = A("Prev",_href=URL('quizzes','editquestion',vars={'quiz':request.vars.quiz, 'qnum':int(request.vars.qnum)-1}), _class="btn")
    if int(request.vars.qnum) < len(quiz.questions):
        nextButton = A("Next",_href=URL('quizzes','editquestion',vars={'quiz':request.vars.quiz, 'qnum':int(request.vars.qnum)+1}), _class="btn")
    return dict(name = quiz.name, form=form, qnum=request.vars.qnum, prevButton=prevButton, nextButton=nextButton,insertButtonBefore=insertButtonBefore,
                insertButtonAfter = insertButtonAfter, deleteButton=deleteButton)
        
    
@auth.requires_login()
def show():
    quiz = db(db.quiz.id==request.get_vars['id']).select()[0]
    if quiz.author_id != auth.user.id:
        redirect('/QuizMe/quizzes')
    questions = []
    for i in xrange(len(quiz.questions)):
        questions.append(db(db.question.id == quiz.questions[i]).select()[0])
    return dict(quiz=quiz, questions=questions)

@auth.requires_login()
def delete():
    quiz = db(db.quiz.id==request.get_vars['quiz']).select()[0]
    if quiz.author_id != auth.user.id:
        redirect('/QuizMe/quizzes')
    for question in quiz.questions:
        db(db.question.id==question.id).delete()
    db(db.quiz.id==quiz.id).delete()
    redirect('/QuizMe/quizzes')
#This function is used when submitting a guess so that all necessary operations are done in one transaction
def submitGuess(qid, userid, answer):
    activeQ = db(db.question.id==qid).select()[0]
    newguesses = activeQ.guesses
    if userid in activeQ.guess_owners:
        ind = activeQ.guess_owners.index(userid)
        print ind
        newguesses[ind]=answer
        activeQ.update_record(guesses=newguesses)
        db.commit()
    else:
        newguessowners = activeQ.guess_owners
        newguessowners.append(userid)
        newguesses.append(answer)
        activeQ.update_record(guesses=newguesses, guess_owners=newguessowners)
        db.commit()
    
    
@auth.requires_login()
def take():
    quiz = db(db.quiz.id==request.get_vars['id']).select()[0]
    activeQ = db(db.question.id==quiz.questions[int(request.get_vars['q'])-1]).select()[0]
    status = ""
    userid = auth.user.id
    results=[]
    if userid == quiz.author_id:
        owner = True
        if not quiz.active:
            db(db.quiz.id==request.get_vars['id']).update(active=True)
    else:
        owner = False
        if not quiz.active:
            redirect(URL('default','index'))
        if request.vars.submitAnswer:
            if activeQ.active:
                options = googledb.create_transaction_options(propagation=googledb.ALLOWED)
                googledb.run_in_transaction_options(options, submitGuess, quiz.questions[int(request.get_vars['q'])-1], unicode(userid), int(request.vars.answer))
                response.flash=T("Answer submitted!")
            else:
                response.flash=T("Answer not submitted - quiz not active")
    return dict(quiz=quiz, question = activeQ, qnum=request.get_vars['q'], owner=owner,results=results)

def activateQ():
    activeQ = db(db.question.id==int(request.vars.qId)).select()[0]
    activeQ.update_record(active=True)
    activeQ.update_record(guesses=[])
    activeQ.update_record(guess_owners=[])
    return '<input type="button" value="Stop" name="qControlBtn" class="btn" onclick="stopQ();" />'

def endQ():
    activeQ = db(db.question.id==int(request.vars.qId)).select()[0]
    activeQ.update_record(active=False)
    return '<input type="button" value="Start" name="qControlBtn" class="btn" onclick="startQ();" />'

def getResults():
    activeQ = db(db.question.id==int(request.vars.qId)).select()[0]
    command = ""
    for i in xrange(len(activeQ.answers)):
        command += "jQuery('.result%s').text(%s);"%(i, activeQ.guesses.count(i))
    return command

def submitAnswer():
    activeQ = db(db.question.id==int(request.vars.qId)).select()[0]
    if activeQ.active:
        options = googledb.create_transaction_options(propagation=googledb.ALLOWED)
        googledb.run_in_transaction_options(options, submitGuess, int(request.vars.qId), unicode(auth.user.id), int(request.vars.guess))
        result = "Submitted Guess: %c"%(chr(ord('a')+int(request.vars.guess)))
    else:
        result = "Question not active - try again in a bit!"
    return result

def deleteQuestion(quiz, qnum):
    db(db.question.id == quiz.questions[qnum-1]).delete()
    newQuestions = quiz.questions
    del newQuestions[qnum-1]
    db(db.quiz.id == quiz.id).update(questions=newQuestions)
