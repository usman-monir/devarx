from app import db

class Users:

    def verify(self, email):
        mydbCursor = db.cursor()
        query = 'select * from Users where email=%s'
        arg = email
        mydbCursor.execute(query, arg)
        db.commit()
        data = mydbCursor.fetchone()
        if mydbCursor is not None:
            mydbCursor.close()
        return data

    def updatePassword(self,password, email):
        updated=False
        mydbCursor = db.cursor()
        query = 'update Users set password=%s where email=%s'
        arg = (password,email)
        mydbCursor.execute(query, arg)
        db.commit()
        updated=True
        if mydbCursor is not None:
            mydbCursor.close()
        return updated


    def CreateUsersTable(self):
        try:
            mydbCursor = db.cursor()
            sql = 'CREATE TABLE IF NOT EXISTS Users (id int NOT NULL PRIMARY KEY AUTO_INCREMENT,username VARCHAR(50),email VARCHAR(50), password VARCHAR(25))'
            mydbCursor.execute(sql)
            db.commit()
        except Exception as e:
            print(str(e))
        finally:
            if mydbCursor is not None:
                mydbCursor.close()

    def insertToUsers(self, u, e, p):
        try:
            mydbCursor = db.cursor()
            sql1 = 'SELECT * from Users where email=%s'
            args1 = (e)
            mydbCursor.execute(sql1, args1)
            res = mydbCursor.fetchone()
            if res:
                return ("User already exists with this email!", "danger")
            sql2 = 'INSERT INTO Users (username, email, password) VALUES (%s, %s, %s)'
            args2 = (u, e, p)
            mydbCursor.execute(sql2, args2)
            db.commit()
            return ("Added to Users", "success")
        except Exception as e:
            mssg = str(e)
            start_index = mssg.find('"') + 1
            end_index = mssg.find('"', start_index)

            if start_index != -1 and end_index != -1:
                return mssg[start_index:end_index]
            else:
                return (str(e), "danger")
        finally:
            if mydbCursor is not None:
                mydbCursor.close()


    def login(self, email, password):
        try:
            mydbCursor = db.cursor()
            sql = "SELECT * FROM Users WHERE email = %s AND password = %s"
            args = (email, password)
            mydbCursor.execute(sql, args)
            db.commit()
            rows = mydbCursor.fetchone()
            print(rows)
        except Exception as e:
           print(str(e))
        finally:
            if mydbCursor is not None:
                mydbCursor.close()
            return rows


    def getUserId(self, email, password):
        try:
            mydbCursor = db.cursor()
            sql = "SELECT id FROM Users WHERE email = %s AND password = %s"
            args = (email, password)
            mydbCursor.execute(sql, args)
            db.commit()
            rows = mydbCursor.fetchone()[0]
            print(rows)
        except Exception as e:
           print(str(e))
        finally:
            if mydbCursor is not None:
                mydbCursor.close()
            return rows

    def getUserNames(self):
        try:
            mydbCursor = db.cursor()
            sql = "SELECT id,username,email FROM Users"
            mydbCursor.execute(sql)
            db.commit()
            rows = mydbCursor.fetchall()
            return rows

        except Exception as e:
            print(str(e))
        finally:
            if mydbCursor is not None:
                mydbCursor.close()


    def getUserData(self, id):
        try:
            mydbCursor = db.cursor()
            sql = "SELECT * FROM Users where id=%s"
            args = (id)
            mydbCursor.execute(sql, args)
            rows = mydbCursor.fetchone()
            return rows
        except Exception as e:
            print(str(e))
        finally:
            if mydbCursor is not None:
                mydbCursor.close()

    def getAllUsers(self):
        try:
            mydbCursor = db.cursor()
            sql = "SELECT * FROM Users"
            mydbCursor.execute(sql)
            rows = mydbCursor.fetchall()
            return rows
        except Exception as e:
            print(str(e))
        finally:
            if mydbCursor is not None:
                mydbCursor.close()

    # profile
    def saveProfile(self, id, name, email, profile_photo):
        try:
            mydbCursor = db.cursor()
            sql = "insert into profiles (id, username, email, profile_photo) values (%s,%s,%s,%s)"
            args = (id, name, email, profile_photo)
            mydbCursor.execute(sql, args)
            db.commit()
            rows = mydbCursor.fetchone()
            return rows
        except Exception as e:
            print(str(e))
        finally:
            if mydbCursor is not None:
                mydbCursor.close()


    def getProfile(self, id):
        try:
            mydbCursor = db.cursor()
            sql = "select * from Profiles where id=%s"
            args = (id)
            mydbCursor.execute(sql, args)
            db.commit()
            rows = mydbCursor.fetchone()
            return rows
        except Exception as e:
            print(str(e))
        finally:
            if mydbCursor is not None:
                mydbCursor.close()


    def updateProfile(self, profileData):
        try:
            mydbCursor = db.cursor()
            sql = "UPDATE profiles SET "
            args = []
            for key, value in profileData.items():
                sql += f"{key} = %s, "
                args.append(value)
            sql = sql[:-2]
            sql += " WHERE id = %s"
            args.append(profileData.get('id'))
            mydbCursor.execute(sql, args)
            db.commit()
            return ("Profile Updated Successfully!", "success")
        except Exception as e:
            print(str(e))
            return ("Profile cannot update!", "danger")
        finally:
            if mydbCursor is not None:
                mydbCursor.close()

    def deleteProfile(self,id):
        try:
            mydbCursor = db.cursor()
            query1 = "DELETE from connections where friend1= %s or friend2 = %s"
            query2 = "DELETE from pending where reciever_id=%s or sender_id = %s"
            query3 = "DELETE from chat_history where sender_id = %s or reciever_id = %s"
            query4 = "DELETE from profiles where id = %s"
            query5 = "DELETE from users where id = %s"
            mydbCursor.execute(query1, (id, id))
            db.commit()
            mydbCursor.execute(query2, (id, id))
            db.commit()
            mydbCursor.execute(query3, (id, id))
            db.commit()
            mydbCursor.execute(query4, id)
            db.commit()
            mydbCursor.execute(query5, id)
            db.commit()
            return (True,"Your account have been deactivated! Create another to join Devarx!","danger")
        except Exception as e:
            print(str(e))
            return (False, "Profile cannot be deleted due to: " + str(e), "warning")
        finally:
            if mydbCursor is not None:
                mydbCursor.close()

    def getAllProfiles(self):
        try:
            mydbCursor = db.cursor()
            sql = "select * from Profiles"
            mydbCursor.execute(sql)
            rows = mydbCursor.fetchall()
            return rows
        except Exception as e:
            print(str(e))
            return None
        finally:
            if mydbCursor is not None:
                mydbCursor.close()


    def __AlreadySent__(self, sender_id, reciever_id):
        try:
            mydbCursor = db.cursor()
            query = "select * from pending where sender_id=%s and reciever_id=%s"
            args=(sender_id, reciever_id)

            mydbCursor.execute(query,args)
            result = mydbCursor.fetchone()

            mydbCursor.close()

            if result is None:
                return False
            else:
                print(result)
                return True
        except Exception as e:
            print(str(e))
            return True


    def __AlreadyConnected__(self, friend1, friend2):
        try:
            mydbCursor = db.cursor()
            query = "select * from connections where friend1=%s and friend2=%s"
            args=(friend1, friend2)

            mydbCursor.execute(query,args)
            result = mydbCursor.fetchone()

            mydbCursor.close()

            if result is None:
                return False
            else:
                print(result)
                return True
        except Exception as e:
            print(str(e))
            return True


    def addToPending(self, sender_id, reciever_id):
        try:
            if self.__AlreadySent__(sender_id, reciever_id):
                return ("Already sent!", "warning" )

            mydbCursor = db.cursor()
            sql = "insert into pending(sender_id, reciever_id) values(%s, %s)"
            args = (sender_id, reciever_id)
            mydbCursor.execute(sql, args)
            db.commit()
            mydbCursor.close()
            return ("Connection Request Sent!", "success")

        except Exception as e:
            print(str(e))
            mydbCursor.close()
            mssg = str(e)
            start_index = mssg.find('"') + 1
            end_index = mssg.find('"', start_index)

            if start_index != -1 and end_index != -1:
                return (mssg[start_index:end_index], "danger")


    def clearFromPending(self, sender_id, reciever_id):
        try:
            mydbCursor = db.cursor()

            sql = "delete from pending where sender_id=%s and reciever_id=%s"
            args=(sender_id,reciever_id)
            mydbCursor.execute(sql,args)
            db.commit()
        except Exception as e:
            print(str(e))
        finally:
            if mydbCursor is not None:
                mydbCursor.close()


    def addConnection(self, friend1, friend2):
        try:
            if self.__AlreadyConnected__(friend1, friend2):
                return ("Connectionn already exists!", "warning")

            mydbCursor = db.cursor()
            sql = "insert into connections(friend1, friend2) values(%s, %s)"
            args = (friend1, friend2)
            mydbCursor.execute(sql, args)
            db.commit()
            mydbCursor.close()
            return ("Connection Added!", "success")

        except Exception as e:
            print(str(e))
            mydbCursor.close()
            mssg = str(e)
            start_index = mssg.find('"') + 1
            end_index = mssg.find('"', start_index)

            if start_index != -1 and end_index != -1:
                return (mssg[start_index:end_index], "danger")


    def removeConnection(self,friend1, friend2):
        try:
            mydbCursor = db.cursor()
            sql = "delete from connections where (friend1=%s and friend2=%s) or (friend1=%s and friend2=%s)"
            args = (friend1, friend2, friend2, friend1)
            mydbCursor.execute(sql, args)
            db.commit()
            mydbCursor.close()
            return (True,"Connection Removed!", "success")

        except Exception as e:
            print(str(e))
            mydbCursor.close()
            mssg = str(e)
            start_index = mssg.find('"') + 1
            end_index = mssg.find('"', start_index)

            if start_index != -1 and end_index != -1:
                return (False, mssg[start_index:end_index], "danger")


    def getConnections(self,id):
        try:
            mydbCursor = db.cursor()
            sql = "select * from connections where friend1=%s or friend2=%s"
            args=(id,id)
            mydbCursor.execute(sql,args)

            result = mydbCursor.fetchall()

            print("connections: ", result)
            return result
        except Exception as e:
            print(str(e))
            return None
        finally:
            if mydbCursor is not None:
                mydbCursor.close()


    def getPendingRequests(self,id):
        try:
            mydbCursor = db.cursor()

            sql = "select sender_id from pending where reciever_id=%s"
            args = (id)
            mydbCursor.execute(sql, args)
            result = mydbCursor.fetchall()
            return result

        except Exception as e:
            print(str(e))

        finally:
            if mydbCursor is not None:
                mydbCursor.close()


    def getRoomId(self, id, friend_id):
        try:
            mydbCursor = db.cursor()

            sql = "select room_id from connections where (friend1=%s and friend2=%s) or (friend1=%s and friend2=%s)"
            args = (id, friend_id, friend_id, id)
            mydbCursor.execute(sql, args)
            result = mydbCursor.fetchone()
            return result

        except Exception as e:
            print(str(e))

        finally:
            if mydbCursor is not None:
                mydbCursor.close()


    def saveMessage(self, room_id, sender_id, reciever_id, message_text, time_send):
        try:
            mydbCursor = db.cursor()

            sql = "insert into chat_history(room_id, sender_id, reciever_id,message_text,time_send) values(%s,%s,%s,%s,%s)"
            args = (room_id, sender_id, reciever_id, message_text, time_send)
            mydbCursor.execute(sql, args)
            db.commit()
            res = mydbCursor.fetchall()
            print(res)
        except Exception as e:
            print(str(e))

        finally:
            if mydbCursor is not None:
                mydbCursor.close()


    def getPrevChat(self, room_id):
        try:
            mydbCursor = db.cursor()

            sql = "select * from chat_history where room_id = %s"
            args=(room_id)
            mydbCursor.execute(sql, args)
            result = mydbCursor.fetchall()
            return result

        except Exception as e:
            print(str(e))

        finally:
            if mydbCursor is not None:
                mydbCursor.close()


    def createGroup(self, name, description):
        try:
            mydbCursor = db.cursor()

            sql = "insert into public_groups (group_name, group_description) values(%s,%s)"
            args = (name, description)
            mydbCursor.execute(sql, args)
            db.commit()
            return ("Group Created", "success")

        except Exception as e:
            print(str(e))
            mssg = str(e)
            start_index = mssg.find('"') + 1
            end_index = mssg.find('"', start_index)

            if start_index != -1 and end_index != -1:
                return (mssg[start_index:end_index], "warning")
        finally:
            if mydbCursor is not None:
                mydbCursor.close()


    def getGroupData(self, room_id):
        try:
            mydbCursor = db.cursor()

            sql = "select * from public_groups where room_id=%s"
            args = (room_id)
            mydbCursor.execute(sql, args)
            res = mydbCursor.fetchone()
            return res

        except Exception as e:
            print(str(e))
        finally:
            if mydbCursor is not None:
                mydbCursor.close()


    def getAllGroups(self):
        try:
            mydbCursor = db.cursor()

            sql = "select * from public_groups"
            mydbCursor.execute(sql)
            res = mydbCursor.fetchall()
            return res

        except Exception as e:
            print(str(e))
        finally:
            if mydbCursor is not None:
                mydbCursor.close()

    def saveGroupMessage(self,room_id, sender_id ,name, message_text,time_send):
        try:
            mydbCursor = db.cursor()

            sql = "insert into public_group_chat_history values(%s,%s,%s,%s,%s)"
            args = (room_id, sender_id ,name, message_text,time_send)
            mydbCursor.execute(sql, args)
            db.commit()
            mydbCursor.close()
            return True
        except Exception as e:
            print(str(e))
            return False


    def getPrevGroupChat(self, room_id):
        try:
            mydbCursor = db.cursor()

            sql = "select * from public_group_chat_history where room_id = %s"
            args=(room_id)
            mydbCursor.execute(sql, args)
            result = mydbCursor.fetchall()
            return result

        except Exception as e:
            print(str(e))

        finally:
            if mydbCursor is not None:
                mydbCursor.close()


    def getDp(self, id):
        try:
            mydbCursor = db.cursor()
            mydbCursor.execute("select profile_photo from profiles where id=%s",id)
            path = mydbCursor.fetchone()
            return path

        except Exception as e:
            print(str(e))
            return None

        finally:
            if mydbCursor is not None:
                mydbCursor.close()


    def changeDp(self, id, filename):
        try:
            mydbCursor = db.cursor()
            path = "/static/images/"+filename
            print(path)
            sql="update profiles set profile_photo=%s where id=%s"
            args=(path,id)
            mydbCursor.execute(sql,args)
            print(mydbCursor.fetchone())
            db.commit()
        except Exception as e:
            print("error",str(e))
            return False
        finally:
            if mydbCursor is not None:
                mydbCursor.close()
                return path
