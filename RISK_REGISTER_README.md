# Risk Register DC performance testing

To prepare for running scalability tests, which include the 
app-specific tests, we need to run the set-up scripts that are coded 
in the JMeter `jira.jmx` file, in the set-up thread group. Those scripts:

* create a risk register for every project in the server; and
* create 200 risks in the ABC project (ABC project must have been created already).

In addition, the following tasks must be done. In 2021 we did this manually,
but it would be a good idea to script these actions too in future runs.

* Add the Risk issue type to every issue type scheme; and
* Add a mapping to every issue type screen scheme thus: Risk >> Risk screen scheme.

