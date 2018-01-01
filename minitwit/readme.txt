### Grad Assignment ###

GitHub URL: https://github.com/thorveakshay/minitwit-python-app


Prepared by : Akshay Thorve

### Code Execution
Script written to execute project from one place

Inside minitwit/minitwit run ./build.sh command to start the project

### Changes in this build ( Grad Assignment )

1) Added like unlike message functionality
2) Added Leaderboard with recent score displayed
3) Added API for above functionality
4) Added Redis cache for API endpoints as well as old UI routes
5) Invalidated cache on like, unlike

used zincrby and zrevrange for calculating leadership board

### Possible improvements ##
1 user can like message only once
