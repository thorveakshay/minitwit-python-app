INSERT INTO `user` (user_id,username,email,pw_hash) VALUES (1,'akshay','thorveakshay@gmail.com','pbkdf2:sha256:50000$YX4MFwTd$7d1403851721cc3893cbb584a56b276bb940be896d4fd7f18da043517efba9a1'),
 (2,'Sam','sam@gmail.com','pbkdf2:sha256:50000$82iZ3QCV$dbedadfe5a88d4c51cd5f0f95d7a94a869edf8c551df286e2a0de64b362d725d'),
 (3,'John','John@yahoo.com','pbkdf2:sha256:50000$087UliYt$4da3ad5aba507a50c21b0747fa345eab67323fb950efd378c1d1b86711273af8');

 INSERT INTO `message` (message_id,author_id,text,pub_date) VALUES (1,1,'I like late night coding! What about you ?',1505811310),
  (2,2,'I saw GOT today! It was awesome #Season7',1505811332),
  (3,3,'Awesome weather!! Going for long drive any one interested ?',1505811421),
  (4,1,'Wow!! I just exported the data from all tables to sql file! Awesome!',1505812142),
  (5,1,'I need coffee now! #BreakTime',1505812176),
  (6,3,'@Sam: Next time invite me to watch GOT! Will sit together.',1505812303);


 INSERT INTO `follower` (who_id,whom_id) VALUES (2,1),
 (3,2);
