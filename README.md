# clock
A chiming clock.

This clock chimes Cambridge quarters on the quarter hours and chimes the hour.  The bells used are recordings of the bells of St John the Baptist, Keynsham, Somerset.

The clock is set not to chime from 10PM and to start again at 8AM.

The clock runs a simple webserver.  To ring a method, access a URL such as:

	http://127.0.0.1:8080/ring/stedman

The clock will ring the named method (currently it doesn't matter what you request, you get stedman triples).  After the ringing, if there would have been a clock chime less than a minute before the ringing finishes, it still chimes.

