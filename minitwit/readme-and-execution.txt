
### Code Execution
Script written to execute project from one place

inside minitwit/minitwit run ./build.sh command to start the project

### Changes in this build (Project 4)
Added Redis cache for API endpoints as well as old UI routes

Invalidated cache on follow, unfollow and adding new message


###
Used pickle and cPickle.

Started with cPickle as it have much more performance than pickle but later found that
cpickle was not properly working with routes and giving many pickle and parsing errors so ended using original pickle too.
