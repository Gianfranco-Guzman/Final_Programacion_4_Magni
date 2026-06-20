import psycopg2
conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/foodstore")
conn.autocommit = True
cur = conn.cursor()
cur.execute("ALTER TABLE pedido ADD COLUMN IF NOT EXISTS tipo_entrega VARCHAR(10) NOT NULL DEFAULT 'domicilio'")
print("OK - columna tipo_entrega agregada")
conn.close()
