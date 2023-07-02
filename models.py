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
            sql = 'INSERT INTO Users (username, email, password) VALUES (%s, %s, %s)'
            args = (u, e, p)
            mydbCursor.execute(sql, args)
            db.commit()
        except Exception as e:
            mssg = str(e)
            start_index = mssg.find('"') + 1
            end_index = mssg.find('"', start_index)

            if start_index != -1 and end_index != -1:
                return mssg[start_index:end_index]
            else:
                return str(e)
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
            db.commit()
            rows = mydbCursor.fetchone()
            return rows
        except Exception as e:
            print(str(e))
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
            return ("Connection Removed!", "success")

        except Exception as e:
            print(str(e))
            mydbCursor.close()
            mssg = str(e)
            start_index = mssg.find('"') + 1
            end_index = mssg.find('"', start_index)

            if start_index != -1 and end_index != -1:
                return (mssg[start_index:end_index], "danger")


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
