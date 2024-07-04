from flask_mysqldb import MySQL

class DataBase:

    def __init__(self,app) -> None:
        self.mysql = MySQL()
        self.mysql.init_app(app)
    def insert(self,table,columns,values):
        if columns !="":
            query = "INSERT INTO {} ({}) VALUES ({});".format(table,','.join(columns),','.join(["%s"]*len(values)))
        else:
            query = "INSERT INTO {} VALUES ({});".format(table,','.join(["%s"]*len(values)))

        cur = self.mysql.connection.cursor()
        data = ()
        for i in values:
            data = data + (i,)
        print(query)
        cur.execute(query, data)
        self.mysql.connection.commit()
        cur.close()
    def select(self,columns,table,condition):
        query = "select {} from {} where {};".format(','.join(columns),table,condition[0])
        cur = self.mysql.connection.cursor()
        print(query)
        if condition[1]:
            cur.execute(query, condition[1])
        else:
            cur.execute(query)
        
        data = cur.fetchall()
        cur.close()
        return data
    def selectOne(self,columns,table,condition):
        
        query = "select {} from {} where {};".format(','.join(columns),table,condition[0])
        print(query)
        cur = self.mysql.connection.cursor()
        if condition[1]:
            cur.execute(query, condition[1])
        else:
            cur.execute(query)
        data = cur.fetchone()
        cur.close()
        return data
    def update(self,table,column,value,condition):
        query = 'update {} set {}="%s" where {};'.format(table,column,condition[0])
        if isinstance(value,int):
            query = "update {} set {}={};".format(table,column,value)
        print(query,condition[1],end='')
        
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query, (value, condition[1]))
            self.mysql.connection.commit()  # Ensure changes are committed to the database
            print("successfull entring")
            
        except:
            print("\n\n\nCouldnt upadte bro. Upadte failed.")
            
        finally:
            cur.close()
        # cur = self.mysql.connection.cursor()
        # cur.execute(query,(value,condition[1]))
        # cur.close()
    def getInsertedId(self):
        cur = self.mysql.connection.cursor()
        cur.execute("SELECT LAST_INSERT_ID();")
        result = cur.fetchone()
        cur.close()
        return result['LAST_INSERT_ID()'] if result else None
    
    def delete(self,table,condition):
        query = "delete from {} where {};".format(table,condition[0])
        print(query)
        cur = self.mysql.connection.cursor()
        cur.execute(query, condition[1])
        self.mysql.connection.commit()
        cur.close()
        print("Delete complete")
