from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse, HttpResponseRedirect
from grading.models import Instructor, Course, Assignment, Student, StudentAssignment, Question
from django.urls import reverse
import datetime
from django.utils import timezone

import sys

def Factorial(n): # return factorial
    result = 1
    for i in range (1,n):
        result = result * i
    print "factorial is ",result
    return result

print Factorial(10)

# Create your views here.

def mainindex(request):
        context = { 'instructor_list': Instructor.objects.all() }
        return render(request, 'grading/index.html', context)

def instructorindex(request, instructor_id):
        a = get_object_or_404(Instructor, pk=instructor_id)
        
        instructor_courses = list(Instructor.objects.get(pk=instructor_id).course_set.all())
        student_assigns = list(StudentAssignment.objects.all())
        count = 0
        for s in student_assigns:
         for c in instructor_courses:
          if s.assignment.course.title == c.title and s.score == -1:
           count = count + 1
        context = { 'course_list': a.course_set.all(),'student_assigns': student_assigns, 'submit_num': count, 'instructor_id': instructor_id }
        return render(request, 'grading/instructorindex.html', context)

def instructorcourse(request, instructor_id, course_id):
	c = get_object_or_404(Course, pk=course_id)
	a_list = c.assignment_set.filter(due_date__gte=timezone.now())
	p_list = c.assignment_set.filter(due_date__lte=timezone.now())
	context = { 'instructor_id': instructor_id, 'course_id': course_id, 'course_title': c.title, 'active_assignment_list': a_list, 'past_assignment_list': p_list }
        return render(request, 'grading/instructorcourse.html', context)

def instructorassignment(request, instructor_id, course_id, assignment_id):
	# Should get a list of all submissions for this assignment, and set it in context
  course_assign = Course.objects.get(pk=course_id).assignment_set.get(pk= assignment_id)
  sa_object_list = list(StudentAssignment.objects.all())
  sa_list = []
  for sa in sa_object_list:
   sa_list.append(sa.assignment)
  
  courseassign_sublist = []
  for sa in sa_list:
   if sa == course_assign: 
    courseassign_sublist.append(sa)

  specific_assignment = Instructor.objects.get(pk = instructor_id).course_set.get(pk=course_id).assignment_set.get(pk=assignment_id)

  submit_oblist = list(StudentAssignment.objects.filter(assignment=specific_assignment))
  student_sub_list =[]
  for i in submit_oblist:
   student_sub_list.append(i.student_id)

  studentname_list =[]
  studentlist = list(Student.objects.all())
  for i in studentlist:
   if i.id in student_sub_list:
    studentname_list.append(i.name)
  studentname_list = sorted(studentname_list)
  context = {'specific_assignment': specific_assignment, 'submit_oblist':submit_oblist, 'studentname_list':studentname_list, 'instructor_id': instructor_id, 'assignment_id': assignment_id, 'course_id': course_id, 'course_assign': course_assign, 'courseassign_sublist': courseassign_sublist }
  return render(request, 'grading/instructorassignment.html', context)

def instructorcreate(request, instructor_id, course_id):
        context = { 'course_list': Instructor.objects.all() }
        return render(request, 'grading/instructorcreate.html', context)

def instructorgradesubmission(request, instructor_id, course_id, assignment_id, student_id):
 instructor_course_assign = Instructor.objects.get(pk=instructor_id).course_set.get(pk=course_id).assignment_set.get(pk=assignment_id)
 student_sub_assignlist = list(Student.objects.get(pk=student_id).studentassignment_set.all())
 student_sub_list = []
 for i in student_sub_assignlist:
  student_sub_list.append(i.assignment)

 ssub_cassign_oblist = list(Student.objects.get(pk=student_id).studentassignment_set.filter(assignment = instructor_course_assign))
 for i in ssub_cassign_oblist:
  sanswers_for_assign = i.answers
  ssub_cassign = i.assignment

 question_of_assigns = list(Assignment.objects.filter(course_id__pk=course_id).get(pk=assignment_id).question_set.all())

 answer_of_assign = []
 for i in question_of_assigns:
  answer_of_assign.append(i.trueorfalse) # answer of assign_no

 text_of_assign = []
 for i in question_of_assigns:
  text_of_assign.append(str(i.question_text))

 sanswers_str = str(sanswers_for_assign)
 sanswers = sanswers_str.split()

 display = []
 for i in range(0,1):
  display.append(str('Question:  ' + text_of_assign[i] + ',  STUDENT ANSWER:  '+ sanswers[i] + ' ').split(','))

 answer = []
 for i in answer_of_assign:
  answer.append(str(i))

 canswer = []
 for i in answer:
  canswer.append(i.lower())

 score = 0
 for i in range(0,1):
  if canswer[i] == sanswers[i]:
   score = score + 1

 context = {'course_id': course_id, 'instructor_id': instructor_id, 'score':score, 'instructor_course_assign':instructor_course_assign, 'ssub_cassign': ssub_cassign, 'display':display }
 return render(request, 'grading/instructorgradesubmission.html', context)

def studentindex(request, student_id):
  student_course_list = Student.objects.get(pk=student_id).courses.all()
  available_assign_initlist = []
  available_assign_list = []
  past_assign_initlist=[]
  past_assign_list=[]
  finala_list = []
  finalp_list = []
  final_sublist = []

  for c in student_course_list:
    available_assign_initlist.append(c.assignment_set.filter(due_date__gte = timezone.now()))
    past_assign_initlist.append(c.assignment_set.filter(due_date__lte = timezone.now()))
  for a in available_assign_initlist:
    if a.exists():
      available_assign_list.append(a)
  for p in past_assign_initlist:
    if p.exists():
      past_assign_list.append(p)
  for a in available_assign_list:
    finala_list.append(a[0])
  for p in past_assign_list:
    finalp_list.append(p[0])

  student_sub_assignlist = Student.objects.get(pk=student_id).studentassignment_set.all()
  sub_assignlist = list(student_sub_assignlist)
  for a in sub_assignlist:
    final_sublist.append(a.assignment)
  aa_sublist = list(set(final_sublist).intersection(set(finala_list)))  # available assign submitted list 
  aa_notsublist = list(set(finala_list) - set(aa_sublist))              # available assign not submitted list
  pa_sublist = list(set(final_sublist) - (set(finala_list)))            # past assign submitted list

  score=[]
  for i in sub_assignlist:
   if i.assignment in pa_sublist:
    score.append(i.score)

  context = { 'student_id': student_id, 'student_course_list': student_course_list, 'aa_sublist':aa_sublist, 'pa_sublist': pa_sublist, 'aa_notsublist':aa_notsublist, 'finalp_list': finalp_list, 'sub_assignlist':sub_assignlist }
  return render(request, 'grading/studentindex.html', context)

def studentassignment(request, student_id, assignment_id):
	context = { 'assignment': Assignment.objects.get(pk=assignment_id), 'student': Student.objects.get(pk=student_id) }
        return render(request, 'grading/studentassignment.html', context)

def submitassignment(request, student_id, assignment_id):
	print request.POST
	answers = " ".join([request.POST["answer{}".format(i)] for i in range(1, 101) if "answer{}".format(i) in request.POST])
	sa = StudentAssignment(student=Student.objects.get(pk=student_id), assignment=Assignment.objects.get(pk=assignment_id), answers=answers, score=-1)
	sa.save()
	return HttpResponseRedirect(reverse('submittedassignment', args=(student_id,assignment_id,)))

def submittedassignment(request, student_id, assignment_id):
	context = { 'student_id': student_id, 'course_list': Student.objects.get(pk=student_id).courses.all(), 'submitted_assignment':assignment_id }
	return render(request, 'grading/studentindex.html', context)

