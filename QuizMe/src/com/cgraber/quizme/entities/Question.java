package com.cgraber.quizme.entities;

import java.util.List;

import com.googlecode.objectify.annotation.Entity;
import com.googlecode.objectify.annotation.Id;

@Entity
public class Question {
	@Id Long id;
	int qNum;
	String title;
	String question;
	List<String> answers;
	
	private Question(){}
}
