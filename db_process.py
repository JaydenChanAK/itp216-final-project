import sqlite3 as sl

db = "heart-disease.db"
def create(filename):
	with open(filename, 'r') as file:
		header = file.readline().strip().split(",")
		for i in range(len(header)):
			header[i] = "'" + header[i].replace(" ", "_") + "'"
		header = ", ".join(header)
		file.close()
		
		conn = sl.connect(db)
		curs = conn.cursor()
		
		create_stmt = "CREATE TABLE IF NOT EXISTS heart_disease (" + header + ")"
		curs.execute(create_stmt)
		
		conn.commit()
		conn.close()
		
def store_data(filename, table):
	conn = sl.connect(db)
	curs = conn.cursor()
	
	with open(filename, 'r') as file:
		file.readline()
		for line in file:
			line = line.strip()
			values = line.split(",")
			values = ", ".join(values)
			
			insert_stmt = "INSERT INTO " + table + " VALUES (" + values + " )"
			curs.execute(insert_stmt)
	
	conn.commit()
	conn.close()

def main():
	filename = "./dataset/heart_statlog_cleveland_hungary_final.csv"
	create(filename)
	store_data(filename, "heart_disease")
	print("Success!")
	
if __name__ == "__main__":
	main()