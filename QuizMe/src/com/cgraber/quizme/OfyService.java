package com.cgraber.quizme;

import com.googlecode.objectify.Objectify;
import com.googlecode.objectify.ObjectifyFactory;
import com.googlecode.objectify.ObjectifyService;

/**
 * This class handles the registering of entities for Objectify.
 * Found here: http://code.google.com/p/objectify-appengine/wiki/BestPractices
 * 
 * In anything needed to access the datastore:
 * import static com.yourcode.OfyService.ofy;
 * Thing th = ofy().load().type(Thing).id(123L).now();
 * 
 *
 */
public class OfyService {
 static {
        //Register entities
	 	
    }

    public static Objectify ofy() {
        return ObjectifyService.ofy();
    }

    public static ObjectifyFactory factory() {
        return ObjectifyService.factory();
    }

}
