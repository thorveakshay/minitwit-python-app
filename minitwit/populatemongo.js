use minitwit
db.dropDatabase()
use minitwit
show collections

db.counters.insert(
   {
      _id: "userid",
      seq: 0
   }
)

function getNextSequence(name) {
   var ret = db.counters.findAndModify(
          {
            query: { _id: name },
            update: { $inc: { seq: 1 } },
            new: true
          }
   );

   return ret.seq;
}

db.counters.find()

show collections

db.users.insert({_id: getNextSequence("userid"),username:'abc',email:'abc@gmail.com',pw_hash:'pbkdf2:sha256:50000$JOl85VKA$0ba0ffedb1019ecc9229538064d9e9096006983b85a665f03bb41481d5b606c5', follows:[2.0,3.0,4.0]})

db.users.insert({_id: getNextSequence("userid"),username:'qwe',email:'qwe@gmail.com',pw_hash:'pbkdf2:sha256:50000$hlnlVi6y$fed7ffb5864cffc88704146c81cec4f1e835714c6a00dbd825c8a7e66dd42016', follows : [1.0,2.0] } )

db.users.insert({_id: getNextSequence("userid"),username:'sara',email:'sara@gmail.com',pw_hash:'pbkdf2:sha256:50000$9oBCLjTE$ddc3b87700e1ec49b6f8a609246aac5e95ac9fb5db00846b7c6a2b830b55198a',follows : [4,1]} )

db.users.insert({_id: getNextSequence("userid"),username:'max',email:'max@gmail.com',pw_hash:'pbkdf2:sha256:50000$3EV8fw6t$88b4ab7baf3388edf7cb585a592fecb23224dc62db5befd35b71dad58485c4b7',follows : [3,2] })

db.users.insert({_id: getNextSequence("userid"),username:'mini',email:'mini@gmail.com',pw_hash:'pbkdf2:sha256:50000$9CFD9KqX$f1fb6d734d66bad61ce9f1aeddb33901481d37811c51bbaf44f9860c650f8506',follows : [2,3]} )

db.users.find()
show collections

db.message.insert({author_id:1,email:'abc@gmail.com',username:'abc',text:'Wow!! I just exported the data from all tables to MongoDB file! Awesome!',pub_date:1505764842})
db.message.insert({author_id:1,email:'abc@gmail.com',username:'abc',text:'I saw GOT today! It was awesome #Season7',pub_date:1505764842})
db.message.insert({author_id:2,email:'qwe@gmail.com',username:'qwe',text:'Awesome weather!! Going for long drive any one interested ?',pub_date:1505764872})
db.message.insert({author_id:3,email:'sara@gmail.com',username:'sara',text:'Redis is fun!',pub_date:1505764894})
db.message.insert({author_id:4,email:'max@gmail.com',username:'max',text:'#476! I finished project 4 and Grad assignments. Party time :-)',pub_date:1505764922]})
db.message.insert({author_id:5,email:'mini@gmail.com',username:'mini',text:'Library Second floor! Yay',pub_date:1505764973})

db.message.find()

show collections
