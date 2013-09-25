package com.cgraber.quizme.entities;

import java.util.List;

import com.googlecode.objectify.annotation.Entity;
import com.googlecode.objectify.annotation.Id;

@Entity
public class Quiz {
	@Id Long id;
	String name;
	List<Question> questions; 
	
	private Quiz(){}
}
