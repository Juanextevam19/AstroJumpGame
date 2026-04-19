[app]
title = Astro Jump
package.name = astrojump
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,kv,mp3
version = 0.1
requirements = python3,kivy==2.3.0,pillow

orientation = landscape
fullscreen = 1
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# Configuración de herramientas (Vital para que GitHub no de error)
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True
android.skip_update = False

[buildozer]
log_level = 2
warn_on_root = 1
