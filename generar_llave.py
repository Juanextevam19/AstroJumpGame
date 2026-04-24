import os

# Define tus datos aquí
PASSWORD = "#W%c3#^5" # <--- CAMBIA ESTO Y ANÓTALO
ALIAS = "astrokey"

comando = (
    f'keytool -genkey -v -keystore mi-llave.keystore '
    f'-alias {ALIAS} -keyalg RSA -keysize 2048 -validity 10000 '
    f'-storepass {PASSWORD} -keypass {PASSWORD} '
    f'-dname "CN=Juan, OU=Desarrollo, O=AstroJump, L=Ciudad, S=Estado, C=ES"'
)

print("Generando llave...")
os.system(comando)
print("¡Listo! Si no hubo errores, ahora tienes un archivo llamado mi-llave.keystore")
