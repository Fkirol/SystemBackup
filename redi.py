import redis

try:
    r = redis.Redis(host='localhost', port=6379, db=0)  # Ajusta la configuración si es necesario
    r.ping()  # Intenta hacer ping al servidor
    print("Conexión a Redis exitosa!")

    # Prueba de lectura/escritura
    r.set('prueba', 'Conexión exitosa desde Python')
    valor = r.get('prueba')
    print(f"Valor recuperado: {valor.decode('utf-8')}")

except Exception as e:
    print(f"Error al conectar a Redis: {e}")