from app import db

class User:
    def verify(self, email):
        mydbCursor = db.cursor()
        query = 'select * from signup where email=%s'
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
        query = 'update signup set password=%s where email=%s'
        arg = (password,email)
        mydbCursor.execute(query, arg)
        db.commit()
        updated=True
        if mydbCursor is not None:
            mydbCursor.close()
        return updated
    def CreateSignupTable(self):
        try:
            mydbCursor = db.cursor()
            sql = 'CREATE TABLE IF NOT EXISTS Signup (username VARCHAR(50),email VARCHAR(50) PRIMARY KEY, password VARCHAR(25))'
            mydbCursor.execute(sql)
            db.commit()
        except Exception as e:
            print(str(e))
        finally:
            if mydbCursor is not None:
                mydbCursor.close()

    def insertToSignup(self, u, e, p):
        try:
            mydbCursor = db.cursor()
            sql = 'INSERT INTO Signup (username, email, password) VALUES (%s, %s, %s)'
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
            sql = "SELECT username FROM Signup WHERE email = %s AND password = %s"
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
