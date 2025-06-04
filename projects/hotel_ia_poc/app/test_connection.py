from db.connection import get_reservas

df = get_reservas()
print(df.head())
