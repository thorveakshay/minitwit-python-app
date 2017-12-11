INSERT INTO `user` (user_id,username,email,pw_hash) VALUES
(1,'Sam','sam@gmail.com','pbkdf2:sha256:50000$IPMSDKLd$5dabbf7f347184b5493c242dfa1871f16c67fe8bcf4a44fe4d8633167d42cdb5'),
 (2,'akshay','thorveakshay@gmail.com','pbkdf2:sha256:50000$juOhkzeQ$6a75537014f93bb70d072d615c95ceee382345e74193651bba36a01993696790'),
 (3,'Froot-loops','fl@gmail.com','pbkdf2:sha256:50000$GuDowBJI$5dfc14b34162f3c6ca7f542655f627561e67bba071849af1c16c7f367d91c5cd'),
 (4,'John','John@yahoo.com','pbkdf2:sha256:50000$IMPSMJEX$011a77229275e3b1747ab91755f209cb30d4c182603f5fb694971fa8dbd7f2e1');

INSERT INTO `message` (message_id,author_id,text,pub_date) VALUES (1,2,'I like late night coding! What about you ?',1506384368),
 (2,2,'Wow!! I just exported the data from all tables to MongoDB file! Awesome!',1506384397),
 (3,1,'I saw GOT today! It was awesome #Season7',1506384418),
 (4,4,'Hello, How are you??',1506384468),
 (5,3,'@Sam: Next time invite me to watch GOT! Will sit together.',1506384588),
 (6,1,'Awesome weather!! Going for long drive any one interested ?',1506384882),
 (7,1,'Library Second floor! Yay',1506384919);

 INSERT INTO `follower` (who_id,whom_id) VALUES (1,2),
 (4,2),
 (3,4),
 (3,2);

db.counters.insert(
   {
      _id: "user_id",
      seq: 0
   }
)

 use flask-mongo-476
 db.user.drop()
 db.user.insert([{ user_id: 1,username: "Sam",email: "sam@gmail.com",pw_hash:"pbkdf2:sha256:50000$IPMSDKLd$5dabbf7f347184b5493c242dfa1871f16c67fe8bcf4a44fe4d8633167d42cdb5",  follo: { [ 90, 92, 85 ] } } } },
    {user_id:2,username:"akshay",email:"thorveakshay@gmail.com",pw_hash:"pbkdf2:sha256:50000$juOhkzeQ$6a75537014f93bb70d072d615c95ceee382345e74193651bba36a01993696790"},
    {user_id:3,username:"Froot-loops",email:"fl@gmail.com",pw_hash:"pbkdf2:sha256:50000$GuDowBJI$5dfc14b34162f3c6ca7f542655f627561e67bba071849af1c16c7f367d91c5cd"},
    {user_id:4,username:"John",email:"John@yahoo.com",pw_hash:"pbkdf2:sha256:50000$IMPSMJEX$011a77229275e3b1747ab91755f209cb30d4c182603f5fb694971fa8dbd7f2e1"}]);

db.message.drop()
db.user.insert([{ user_id: 1,username: "Sam",email: "sam@gmail.com",pw_hash:"pbkdf2:sha256:50000$IPMSDKLd$5dabbf7f347184b5493c242dfa1871f16c67fe8bcf4a44fe4d8633167d42cdb5"},
       {user_id:2,username:"akshay",email:"thorveakshay@gmail.com",pw_hash:"pbkdf2:sha256:50000$juOhkzeQ$6a75537014f93bb70d072d615c95ceee382345e74193651bba36a01993696790"},
       {user_id:3,username:"Froot-loops",email:"fl@gmail.com",pw_hash:"pbkdf2:sha256:50000$GuDowBJI$5dfc14b34162f3c6ca7f542655f627561e67bba071849af1c16c7f367d91c5cd"},
       {user_id:4,username:"John",email:"John@yahoo.com",pw_hash:"pbkdf2:sha256:50000$IMPSMJEX$011a77229275e3b1747ab91755f209cb30d4c182603f5fb694971fa8dbd7f2e1"}]);
